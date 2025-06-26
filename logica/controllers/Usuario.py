from fastapi import APIRouter, Request, Response, status, Depends, HTTPException
from sqlalchemy import text
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from sqlalchemy.exc import DBAPIError
from datetime import datetime


import base64
from conexion import conexion_sqlserver as s
from logica.app import encriptador as en
from logica.app.encriptador import passphrase, encriptar
from conexion.conexion_activa import obtener_db, obtener_motor_actual
import re


usuario_router = APIRouter(prefix="/api/usuario")


@usuario_router.post("/contactos")
async def usuario_read_contacts(
    request: Request, response: Response, db=Depends(s.obtener_conexion_sqlserver_dep)
):
    body = await request.json()

    # SQL con parámetros nombrados
    sql = text(
        """
        EXEC sp_traerChatsPrivado 
            @id_usuario = :id_usuario
    """
    )

    try:
        # Ejecutamos la consulta con el parámetro `id_usuario`
        result = db.execute(sql, {"id_usuario": body.get("id_usuario")})

        # Asegurarse de que el resultado contiene datos antes de intentar acceder a ellos
        rows = result.mappings().all()

        if not rows:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        res = []
        for row in rows:
            row_dict = dict(row)

            # Agregamos impresión de depuración para el contenido
            print(f"Tipo de contenido: {type(row['ultimo_mensaje'])}")
            print(f"Contenido (hex): {row['ultimo_mensaje'].hex()}")

            try:
                try:
                    contenido_desencriptado = en.desencriptar(
                        row["ultimo_mensaje"], passphrase
                    )
                except Exception:
                    contenido_desencriptado = "[error al desencriptar]"
                # Si el contenido desencriptado es de tipo bytes, convertirlo a base64
                if isinstance(contenido_desencriptado, bytes):
                    print("Contenido desencriptado (bytes), convirtiendo a base64...")
                    contenido_desencriptado = base64.b64encode(
                        contenido_desencriptado
                    ).decode("utf-8")

            except Exception as e:
                # Si ocurre un error al desencriptar, se marca como error en el contenido
                contenido_desencriptado = "[error al desencriptar]"

            row_dict["ultimo_mensaje"] = contenido_desencriptado
            res.append(row_dict)

        return JSONResponse(content=res, status_code=status.HTTP_200_OK)

    except DBAPIError as e:
        # Error de base de datos
        raise HTTPException(
            status_code=500, detail="Error de base de datos: " + str(e.orig)
        )
    except Exception as e:
        # Cualquier otro error inesperado
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))


@usuario_router.get("/read/{idUsuario}")
async def usuario_read(
    idUsuario: int, response: Response, db=Depends(s.obtener_conexion_sqlserver_dep)
):
    sql = text("SELECT * FROM Usuario WHERE id_usuario = :id_usuario")
    result = db.execute(sql, {"id_usuario": idUsuario})

    res = []
    for row in result.mappings().all():
        row_dict = dict(row)

        # Codificar contraseña
        if "contrasenna" in row_dict and row_dict["contrasenna"] is not None:
            try:
                contenido = en.desencriptar(row["contrasenna"], passphrase)
                row_dict["contrasenna"] = contenido
            except Exception:
                contenido = "[error al desencriptar]"
                row_dict["contrasenna"] = contenido
        # Codificar foto (si existe)
        if "foto_perfil" in row_dict and row_dict["foto_perfil"] is not None:
            if isinstance(row_dict["foto_perfil"], bytes):
                row_dict["foto_perfil"] = base64.b64encode(
                    row_dict["foto_perfil"]
                ).decode("utf-8")
            else:
                row_dict["foto_perfil"] = str(row_dict["foto_perfil"])

        # Serializar campos datetime
        for campo in ["fecha_creacion", "ultimo_ingreso"]:
            if campo in row_dict and isinstance(row_dict[campo], datetime):
                row_dict[campo] = row_dict[
                    campo
                ].isoformat()  # o .strftime("%Y-%m-%d %H:%M:%S")

        res.append(row_dict)
    if not res:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return JSONResponse(content=res, status_code=status.HTTP_200_OK)


@usuario_router.post("/create")
async def create_usuario(
    request: Request,
    response: Response,
    db=Depends(obtener_db),
    motor=Depends(obtener_motor_actual),
):
    body = await request.json()

    # Limpiar cadenas vacías
    for k, v in body.items():
        if isinstance(v, str) and v.strip() == "":
            body[k] = None

    # Validar contraseña
    if "contrasenna" in body and body["contrasenna"]:
        password = body["contrasenna"]
        if (
            len(password) < 8
            or not re.search(r"[A-Z]", password)
            or not re.search(r"[a-z]", password)
            or not re.search(r"[^A-Za-z0-9]", password)
        ):
            raise HTTPException(
                status_code=400,
                detail="La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas y un símbolo.",
            )

    # Encriptar contraseña
    if "contrasenna" in body and body["contrasenna"]:
        body["contrasenna"] = encriptar(body["contrasenna"], passphrase)

    body.setdefault("estado", "Activo")

    if motor == "mysql":
        sql = """
            CALL sp_CrearUsuario(
                %(nombre_usuario)s, %(nombre_completo)s, %(telefono)s, %(correo)s,
                %(contrasenna)s, %(foto_perfil)s, %(estado)s)
        """
    else:
        sql = """
            EXEC sp_CrearUsuario 
                @nombre_usuario = ?, 
                @nombre_completo = ?, 
                @telefono = ?, 
                @correo = ?, 
                @contrasenna = ?, 
                @foto_perfil = ?, 
                @estado = ?
        """

    try:
        cursor = db.cursor()
        if motor == "mysql":
            cursor.execute(sql, body)
        else:
            cursor.execute(
                sql,
                [
                    body.get("nombre_usuario"),
                    body.get("nombre_completo"),
                    body.get("telefono"),
                    body.get("correo"),
                    body.get("contrasenna"),
                    body.get("foto_perfil"),
                    body.get("estado"),
                ],
            )
        db.commit()
        cursor.close()
        return JSONResponse(
            status_code=201, content={"message": "Usuario creado exitosamente."}
        )
    except DBAPIError as e:
        raise HTTPException(
            status_code=500, detail="Error de base de datos: " + str(e.orig)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))


@usuario_router.put("/update/{id}")
async def update_usuario(
    id: int,
    request: Request,
    response: Response,
    db=Depends(obtener_db),
    motor=Depends(obtener_motor_actual),
):
    body = await request.json()

    # Limpiar campos vacíos
    for k, v in body.items():
        if isinstance(v, str) and v.strip() == "":
            body[k] = None

    # Encriptar contraseña si viene
    if "contrasenna" in body and body["contrasenna"]:
        body["contrasenna"] = encriptar(body["contrasenna"], passphrase)

    body.setdefault("estado", "Activo")
    body["id_usuario"] = id

    if motor == "mysql":
        sql = """
            CALL sp_ModificarUsuario(
                %(id_usuario)s, %(nombre_usuario)s, %(nombre_completo)s,
                %(telefono)s, %(correo)s, %(contrasenna)s, %(foto_perfil)s, %(estado)s)
        """
    else:
        sql = """
            EXEC sp_ModificarUsuario 
                @id_usuario = ?, 
                @nombre_usuario = ?, 
                @nombre_completo = ?, 
                @telefono = ?, 
                @correo = ?, 
                @contrasenna = ?, 
                @foto_perfil = ?, 
                @estado = ?
        """

    try:
        cursor = db.cursor()
        if motor == "mysql":
            cursor.execute(sql, body)
        else:
            cursor.execute(
                sql,
                [
                    body.get("id_usuario"),
                    body.get("nombre_usuario"),
                    body.get("nombre_completo"),
                    body.get("telefono"),
                    body.get("correo"),
                    body.get("contrasenna"),
                    body.get("foto_perfil"),
                    body.get("estado"),
                ],
            )
        db.commit()
        cursor.close()
        return {"message": "Usuario actualizado correctamente."}
    except DBAPIError as e:
        raise HTTPException(
            status_code=500, detail="Error de base de datos: " + str(e.orig)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))
