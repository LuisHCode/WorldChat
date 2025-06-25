from fastapi import APIRouter, Request, Response, status, Depends
from sqlalchemy import text
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from sqlalchemy.exc import DBAPIError

from datetime import datetime
import base64
from conexion import conexion_sqlserver as s
from logica.app.encriptador import desencriptar_seguro, passphrase
from logica.app.encriptador import encriptar


usuario_router = APIRouter(prefix="/api/usuario")


@usuario_router.get("/read")
def usuario_read(response: Response, db=Depends(s.obtener_conexion_sqlserver_dep)):
    sql = text("SELECT * FROM Usuario")
    result = db.execute(sql)

    res = []
    for row in result.mappings().all():
        row_dict = dict(row)

        # Codificar contraseña
        if "contrasenna" in row_dict and row_dict["contrasenna"] is not None:
            if isinstance(row_dict["contrasenna"], bytes):
                row_dict["contrasenna"] = base64.b64encode(
                    row_dict["contrasenna"]
                ).decode("utf-8")
            else:
                row_dict["contrasenna"] = str(row_dict["contrasenna"])

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
    request: Request, response: Response, db=Depends(s.obtener_conexion_sqlserver_dep)
):
    body = await request.json()

    # Convertir strings vacíos a None (equivalente a null en SQL)
    for k, v in body.items():
        if isinstance(v, str) and v.strip() == "":
            body[k] = None

    # SQL con parámetros nombrados
    sql = text(
        """
        EXEC sp_CrearUsuario 
            @nombre_usuario = :nombre_usuario, 
            @nombre_completo = :nombre_completo, 
            @telefono = :telefono, 
            @correo = :correo, 
            @contrasenna = :contrasenna, 
            @foto_perfil = :foto_perfil, 
            @estado = :estado
    """
    )

    # Encriptar contraseña si viene
    if "contrasenna" in body and body["contrasenna"]:
        body["contrasenna"] = encriptar(body["contrasenna"], passphrase)

    # Asignar valores por defecto si no vienen
    body.setdefault("estado", "Activo")

    try:
        with db.begin():
            db.execute(
                sql,
                {
                    "nombre_usuario": body.get("nombre_usuario"),
                    "nombre_completo": body.get("nombre_completo"),
                    "telefono": body.get("telefono"),
                    "correo": body.get("correo"),
                    "contrasenna": body.get("contrasenna"),
                    "foto_perfil": body.get("foto_perfil"),
                    "estado": body.get("estado"),
                },
            )
        return JSONResponse(
            status_code=201, content={"message": "Usuario creado exitosamente."}
        )

    except DBAPIError as e:
        mensaje = str(e.orig) if hasattr(e, "orig") else str(e)

        if "50000" in mensaje:
            raise HTTPException(status_code=500, detail="Error al crear usuario.")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))


@usuario_router.put("/update/{id}")
async def update_usuario(
    id: int,
    request: Request,
    response: Response,
    db=Depends(s.obtener_conexion_sqlserver_dep),
):
    body = await request.json()

    # Convertir cadenas vacías a None (como en PHP)
    for k, v in body.items():
        if isinstance(v, str) and v.strip() == "":
            body[k] = None

    # Encriptar contraseña si viene
    if "contrasenna" in body and body["contrasenna"]:
        body["contrasenna"] = encriptar(body["contrasenna"], passphrase)

    body.setdefault("estado", "Activo")

    sql = text(
        """
        EXEC sp_ModificarUsuario 
            @id_usuario = :id_usuario,
            @nombre_usuario = :nombre_usuario,
            @nombre_completo = :nombre_completo,
            @telefono = :telefono,
            @correo = :correo,
            @contrasenna = :contrasenna,
            @foto_perfil = :foto_perfil,
            @estado = :estado
    """
    )

    try:
        with db.begin():
            db.execute(
                sql,
                {
                    "id_usuario": id,
                    "nombre_usuario": body.get("nombre_usuario"),
                    "nombre_completo": body.get("nombre_completo"),
                    "telefono": body.get("telefono"),
                    "correo": body.get("correo"),
                    "contrasenna": body.get("contrasenna"),
                    "foto_perfil": body.get("foto_perfil"),
                    "estado": body.get("estado"),
                },
            )

        return {"message": "Usuario actualizado correctamente."}

    except DBAPIError as e:
        mensaje = str(e.orig) if hasattr(e, "orig") else str(e)

        # Puedes capturar errores específicos si el SP lanza códigos como 50001, 50002...
        if "50001" in mensaje:
            raise HTTPException(status_code=409, detail="Nombre de usuario duplicado.")
        elif "50002" in mensaje:
            raise HTTPException(status_code=409, detail="Correo ya registrado.")
        elif "50003" in mensaje:
            raise HTTPException(status_code=409, detail="Teléfono ya registrado.")
        elif "Usuario no encontrado" in mensaje:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        else:
            raise HTTPException(
                status_code=500, detail="Error al actualizar usuario: " + mensaje
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))
