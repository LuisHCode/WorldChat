from fastapi import APIRouter, Request, Response, status, Depends
from sqlalchemy import text
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from sqlalchemy.exc import DBAPIError
from datetime import datetime


import base64
from conexion import conexion_sqlserver as s
from logica.app import encriptador as en
from logica.app.encriptador import desencriptar_seguro, passphrase


mensaje_router = APIRouter(prefix="/api/mensaje")


@mensaje_router.get("/read")
def mensaje_read(response: Response, db=Depends(s.obtener_conexion_sqlserver_dep)):
    sql = text("SELECT * FROM Mensaje")
    result = db.execute(sql)

    res = []
    for row in result.mappings().all():
        row_dict = dict(row)

        # Codificar contraseña
        if "contenido" in row_dict and row_dict["contenido"] is not None:
            if isinstance(row_dict["contenido"], bytes):
                row_dict["contenido"] = base64.b64encode(row_dict["contenido"]).decode(
                    "utf-8"
                )
            else:
                row_dict["contenido"] = str(row_dict["contenido"])

        # Serializar campos datetime
        for campo in ["fecha_envio"]:
            if campo in row_dict and isinstance(row_dict[campo], datetime):
                row_dict[campo] = row_dict[
                    campo
                ].isoformat()  # o .strftime("%Y-%m-%d %H:%M:%S")

        res.append(row_dict)
    if not res:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return JSONResponse(content=res, status_code=status.HTTP_200_OK)


@mensaje_router.post("/enviar/{id_receptor}")
async def crear_mensaje_privado(
    id_receptor: int,
    request: Request,
    response: Response,
    db=Depends(s.obtener_conexion_sqlserver_dep),
):
    body = await request.json()

    # Convertir cadenas vacías a None
    for k, v in body.items():
        if isinstance(v, str) and v.strip() == "":
            body[k] = None

    id_emisor = body.get("id_emisor")
    contenido = body.get("contenido")

    if not id_emisor or not id_receptor or not contenido:
        raise HTTPException(status_code=400, detail="Faltan parámetros obligatorios")

    # 🛡️ Encriptar contenido antes de enviar
    try:
        contenido_encriptado = en.encriptar(contenido, en.passphrase)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error al encriptar el mensaje: " + str(e)
        )

    sql = text(
        """
        EXEC sp_EnviarMensajePrivado 
            @id_emisor = :id_emisor, 
            @id_receptor = :id_receptor, 
            @contenido = :contenido
    """
    )

    try:
        with db.begin():
            result = db.execute(
                sql,
                {
                    "id_emisor": id_emisor,
                    "id_receptor": id_receptor,
                    "contenido": contenido_encriptado,
                },
            )

            rows = result.mappings().all()
            if not rows:
                raise HTTPException(status_code=400, detail="No hay datos para leer.")

            fila = rows[0]
            if fila.get("exito") == 1:
                return {"mensaje": "Mensaje enviado con éxito"}
            else:
                raise HTTPException(
                    status_code=400, detail="No se pudo enviar el mensaje"
                )

    except DBAPIError as e:
        raise HTTPException(
            status_code=500, detail="Error de base de datos: " + str(e.orig)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))


@mensaje_router.get("/read/{id_receptor}")
async def leer_mensaje_privado(
    id_receptor: int,
    request: Request,
    response: Response,
    db=Depends(s.obtener_conexion_sqlserver_dep),
):
    body = await request.json()

    for k, v in body.items():
        if isinstance(v, str) and v.strip() == "":
            body[k] = None

    id_usuario = body.get("id_usuario")
    clave = en.passphrase  # Reutiliza tu clave simétrica (segura)

    if not id_usuario:
        raise HTTPException(status_code=400, detail="Faltan parámetros obligatorios")

    sql = text(
        """
        EXEC sp_ObtenerMensajesPrivados 
            @id_usuario1 = :id_usuario, 
            @id_usuario2 = :id_receptor
    """
    )

    try:
        with db.begin():
            result = db.execute(
                sql,
                {"id_usuario": id_usuario, "id_receptor": id_receptor},
            )

            rows = result.mappings().all()

            if not rows:
                return Response(status_code=status.HTTP_204_NO_CONTENT)

        mensajes = []
        for row in rows:
            try:
                contenido_desencriptado = en.desencriptar(row["contenido"], clave)
            except Exception as e:
                contenido_desencriptado = "[error al desencriptar]"

            fecha_envio = row["fecha_envio"]
            if isinstance(fecha_envio, datetime):
                fecha_envio = fecha_envio.isoformat()

            mensajes.append(
                {
                    "id_mensaje": row["id_mensaje"],
                    "emisor": row["emisor"],
                    "contenido": contenido_desencriptado,
                    "fecha_envio": fecha_envio,
                    "estado_envio": row["estado_envio"],
                }
            )

        return JSONResponse(content={"mensajes": mensajes}, status_code=200)

    except DBAPIError as e:
        raise HTTPException(
            status_code=500, detail="Error de base de datos: " + str(e.orig)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))


@mensaje_router.get("/read/chat/{id_chat}")
async def leer_mensaje_chat(
    id_chat: int,
    request: Request,
    response: Response,
    db=Depends(s.obtener_conexion_sqlserver_dep),
):
    clave = en.passphrase  # Reutiliza tu clave simétrica (segura)

    sql = text(
        """
        EXEC sp_LeerMensajesChat 
            @id_chat = :id_chat
    """
    )

    try:
        with db.begin():
            result = db.execute(
                sql,
                {"id_chat": id_chat},
            )

            rows = result.mappings().all()

            if not rows:
                return Response(status_code=status.HTTP_204_NO_CONTENT)

        mensajes = []
        for row in rows:
            try:
                contenido_desencriptado = en.desencriptar(row["contenido"], clave)
            except Exception as e:
                contenido_desencriptado = "[error al desencriptar]"

            fecha_envio = row["fecha_envio"]
            if isinstance(fecha_envio, datetime):
                fecha_envio = fecha_envio.isoformat()

            mensajes.append(
                {
                    "id_mensaje": row["id_mensaje"],
                    "emisor": row["emisor"],
                    "contenido": contenido_desencriptado,
                    "fecha_envio": fecha_envio,
                    "estado_envio": row["estado_envio"],
                }
            )

        return JSONResponse(content={"mensajes": mensajes}, status_code=200)

    except DBAPIError as e:
        raise HTTPException(
            status_code=500, detail="Error de base de datos: " + str(e.orig)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))


@mensaje_router.post("/enviar/chat/{id_chat}")
async def crear_mensaje_chat(
    id_chat: int,
    request: Request,
    response: Response,
    db=Depends(s.obtener_conexion_sqlserver_dep),
):
    body = await request.json()

    id_emisor = body.get("id_emisor")
    contenido_texto = body.get("contenido_texto")

    # Validación de parámetros obligatorios
    if not id_emisor or not contenido_texto or not id_chat:
        raise HTTPException(status_code=400, detail="Faltan parámetros obligatorios")

    # 🛡️ Encriptar el contenido antes de enviar
    try:
        contenido_encriptado = en.encriptar(contenido_texto, en.passphrase)
        if not isinstance(contenido_encriptado, bytes):
            raise ValueError("El contenido encriptado no es tipo bytes.")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Error al encriptar el mensaje: " + str(e)
        )

    # Preparar y ejecutar el SP
    sql = text(
        """
        EXEC sp_EnviarMensaje 
            @id_emisor = :id_emisor, 
            @id_chat = :id_chat, 
            @contenido = :contenido
    """
    )

    
    try:
        # Ejecutar y capturar resultado
        result = db.execute(
            sql,
            {
                "id_emisor": id_emisor,
                "id_chat": id_chat,
                "contenido": contenido_encriptado
            },
        )
        # Recuperar resultados (si el SP devuelve SELECT)
        rows = result.mappings().all()

        if not rows:
            raise HTTPException(
                status_code=204, detail="No se devolvieron datos del SP."
            )

        fila = rows[0]
        if fila.get("exito") == 1:
            db.commit()  # 💾 Confirmar si todo fue exitoso
            return {"mensaje": "Mensaje enviado con éxito"}
        else:
            raise HTTPException(
                status_code=500,
                detail=fila.get("error") or "No se pudo enviar el mensaje",
            )

    except DBAPIError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error de base de datos: " + str(e.orig)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))
