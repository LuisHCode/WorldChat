
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException
from sqlalchemy import text
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from sqlalchemy.exc import DBAPIError
from datetime import datetime


import base64
from conexion import conexion_sqlserver as s
from logica.app import encriptador as en
from logica.app.encriptador import desencriptar_seguro, passphrase
from logica.app.encriptador import passphrase
from conexion.conexion_activa import obtener_db, obtener_motor_actual


mensaje_router = APIRouter(prefix="/api/mensaje")


@mensaje_router.get("/read")
def mensaje_read(response: Response, db=Depends(obtener_db)):
    try:
        sql = text("SELECT * FROM Mensaje")
        result = db.execute(sql)

        res = []
        for row in result.mappings().all():
            row_dict = dict(row)

            if "contenido" in row_dict and row_dict["contenido"] is not None:
                row_dict["contenido"] = base64.b64encode(row_dict["contenido"]).decode("utf-8")

            if "fecha_envio" in row_dict and isinstance(row_dict["fecha_envio"], datetime):
                row_dict["fecha_envio"] = row_dict["fecha_envio"].isoformat()

            res.append(row_dict)

        if not res:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        return JSONResponse(content=res, status_code=status.HTTP_200_OK)

    except DBAPIError as e:
        raise HTTPException(status_code=500, detail="Error de base de datos: " + str(e.orig))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))


@mensaje_router.post("/enviar/{id_receptor}")
async def crear_mensaje_privado(
    id_receptor: int,
    request: Request,
    response: Response,
    db=Depends(obtener_db),
    motor=Depends(obtener_motor_actual)
):
    body = await request.json()

    for k, v in body.items():
        if isinstance(v, str) and v.strip() == "":
            body[k] = None

    id_emisor = body.get("id_emisor")
    contenido = body.get("contenido")

    if not id_emisor or not id_receptor or not contenido:
        raise HTTPException(status_code=400, detail="Faltan parámetros obligatorios")

    try:
        contenido_encriptado = en.encriptar(contenido, passphrase)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al encriptar: " + str(e))

    try:
        if motor == "mysql":
            cursor = db.cursor()
            cursor.callproc("sp_EnviarMensajePrivado", [id_emisor, id_receptor, contenido_encriptado])
            db.commit()
            cursor.close()
        else:
            sql = """
                EXEC sp_EnviarMensajePrivado 
                    @id_emisor = ?, 
                    @id_receptor = ?, 
                    @contenido = ?
            """
            cursor = db.cursor()
            cursor.execute(sql, (id_emisor, id_receptor, contenido_encriptado))
            db.commit()
            cursor.close()

        return {"mensaje": "Mensaje enviado con éxito"}

    except DBAPIError as e:
        raise HTTPException(status_code=500, detail="DB error: " + str(e.orig))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))


@mensaje_router.post("/read/{id_receptor}")
async def leer_mensaje_privado(
    id_receptor: int,
    request: Request,
    response: Response,
    db=Depends(obtener_db),
    motor=Depends(obtener_motor_actual),
):
    body = await request.json()
    for k, v in body.items():
        if isinstance(v, str) and v.strip() == "":
            body[k] = None

    id_usuario = body.get("id_usuario")
    if not id_usuario:
        raise HTTPException(status_code=400, detail="Faltan parámetros obligatorios")

    try:
        mensajes = []

        if motor == "mysql":
            cursor = db.cursor(dictionary=True)
            cursor.callproc("sp_ObtenerMensajesPrivados", [id_usuario, id_receptor])

            for result in cursor.stored_results():
                rows = result.fetchall()
                for row in rows:
                    try:
                        contenido = en.desencriptar(row["contenido"], passphrase)
                    except Exception:
                        contenido = "[error al desencriptar]"

                    mensajes.append(
                        {
                            "id_mensaje": row["id_mensaje"],
                            "id_emisor": row["id_emisor"],
                            "emisor": row["emisor"],
                            "contenido": contenido,
                            "fecha_envio": (
                                row["fecha_envio"].isoformat()
                                if isinstance(row["fecha_envio"], datetime)
                                else row["fecha_envio"]
                            ),
                            "estado_envio": row["estado_envio"],
                        }
                    )
            cursor.close()

        else:
            sql = """
                EXEC sp_ObtenerMensajesPrivados 
                    @id_usuario1 = ?, 
                    @id_usuario2 = ?
            """
            cursor = db.cursor()
            cursor.execute(sql, (id_usuario, id_receptor))
            columns = [column[0] for column in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()

            for row in rows:
                try:
                    contenido = en.desencriptar(row["contenido"], passphrase)
                except Exception:
                    contenido = "[error al desencriptar]"

                mensajes.append(
                    {
                        "id_mensaje": row["id_mensaje"],
                        "id_emisor": row["id_emisor"],
                        "emisor": row["emisor"],
                        "contenido": contenido,
                        "fecha_envio": (
                            row["fecha_envio"].isoformat()
                            if isinstance(row["fecha_envio"], datetime)
                            else row["fecha_envio"]
                        ),
                        "estado_envio": row["estado_envio"],
                    }
                )

        if not mensajes:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        return JSONResponse(content={"mensajes": mensajes}, status_code=200)

    except DBAPIError as e:
        raise HTTPException(status_code=500, detail="Error BD: " + str(e.orig))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))


@mensaje_router.post("/enviar/chat/{id_chat}")
async def crear_mensaje_chat(
    id_chat: int,
    request: Request,
    response: Response,
    db=Depends(obtener_db),
    motor=Depends(obtener_motor_actual),
):
    body = await request.json()
    id_emisor = body.get("id_emisor")
    contenido_texto = body.get("contenido_texto")

    if not id_emisor or not contenido_texto or not id_chat:
        raise HTTPException(status_code=400, detail="Faltan parámetros obligatorios")

    try:
        contenido_encriptado = en.encriptar(contenido_texto, passphrase)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al encriptar: " + str(e))

    try:
        if motor == "mysql":
            cursor = db.cursor()
            cursor.callproc(
                "sp_EnviarMensaje", [id_emisor, None, id_chat, contenido_encriptado]
            )
            db.commit()
            cursor.close()
        else:
            sql = """
                EXEC sp_EnviarMensaje 
                    @id_emisor = ?, 
                    @id_chat = ?, 
                    @contenido = ?
            """
            cursor = db.cursor()
            cursor.execute(sql, (id_emisor, id_chat, contenido_encriptado))
            db.commit()
            cursor.close()

        return {"mensaje": "Mensaje enviado con éxito"}

    except DBAPIError as e:
        raise HTTPException(status_code=500, detail="DB error: " + str(e.orig))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))


@mensaje_router.get("/read/chat/{id_chat}")
async def leer_mensaje_chat(
    id_chat: int,
    request: Request,
    response: Response,
    db=Depends(obtener_db),
    motor=Depends(obtener_motor_actual),
):
    try:
        mensajes = []

        if motor == "mysql":
            cursor = db.cursor(dictionary=True)
            cursor.callproc("sp_LeerMensajesChat", [id_chat])
            for result in cursor.stored_results():
                rows = result.fetchall()
                for row in rows:
                    try:
                        contenido = en.desencriptar(row["contenido"], passphrase)
                    except Exception:
                        contenido = "[error al desencriptar]"

                    mensajes.append(
                        {
                            "id_mensaje": row["id_mensaje"],
                            "emisor": row["emisor"],
                            "contenido": contenido,
                            "fecha_envio": (
                                row["fecha_envio"].isoformat()
                                if isinstance(row["fecha_envio"], datetime)
                                else row["fecha_envio"]
                            ),
                            "estado_envio": row["estado_envio"],
                        }
                    )
            cursor.close()

        else:
            sql = "EXEC sp_LeerMensajesChat @id_chat = ?"
            cursor = db.cursor()
            cursor.execute(sql, (id_chat,))
            columns = [column[0] for column in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()

            for row in rows:
                try:
                    contenido = en.desencriptar(row["contenido"], passphrase)
                except Exception:
                    contenido = "[error al desencriptar]"

                mensajes.append(
                    {
                        "id_mensaje": row["id_mensaje"],
                        "emisor": row["emisor"],
                        "contenido": contenido,
                        "fecha_envio": (
                            row["fecha_envio"].isoformat()
                            if isinstance(row["fecha_envio"], datetime)
                            else row["fecha_envio"]
                        ),
                        "estado_envio": row["estado_envio"],
                    }
                )

        if not mensajes:
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        return JSONResponse(content={"mensajes": mensajes}, status_code=200)

    except DBAPIError as e:
        raise HTTPException(status_code=500, detail="Error BD: " + str(e.orig))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))
