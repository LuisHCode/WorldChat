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


participante_router = APIRouter(prefix="/api/participante")


@participante_router.post("/agregar/{id_chat}")
async def agregar_participante(
    id_chat: int,
    request: Request,
    response: Response,
    db=Depends(s.obtener_conexion_sqlserver_dep),
):
    body = await request.json()
    # SQL con parámetros nombrados
    sql = text(
        """
        EXEC sp_AgregarParticipante 
            @id_chat = :id_chat, 
            @id_usuario = :id_usuario 
    """
    )
    try:
        with db.begin() as trans:
            result = db.execute(sql, {
                "id_chat": id_chat,
                "id_usuario": body.get("id_usuario")
            })

            return JSONResponse(status_code=201, content={"message": "Participante agregado exitosamente."})

    except DBAPIError as e:
        mensaje = str(e.orig)

        # 👇 Detectar error lanzado por el SP (por ejemplo THROW 50004)
        if "50005" in mensaje:
            raise HTTPException(status_code=409, detail="El chat no existe.")
        if "50006" in mensaje:
            raise HTTPException(status_code=409, detail="El usuario no existe.")
        if "50007" in mensaje:
            raise HTTPException(status_code=409, detail="El usuario ya es parte del chat.")
        else:
            raise HTTPException(status_code=500, detail="Error de base de datos: " + mensaje)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))

@participante_router.post("/eliminar/{id_chat}")
async def eliminar_participante(
    id_chat: int,
    request: Request,
    response: Response,
    db=Depends(s.obtener_conexion_sqlserver_dep),
):
    body = await request.json()
    # SQL con parámetros nombrados
    sql = text(
        """
        EXEC sp_EliminarParticipante 
            @id_chat = :id_chat, 
            @id_usuario = :id_usuario,
            @id_admin = :id_admin 
    """
    )
    try:
        with db.begin() as trans:
            result = db.execute(sql, {
                "id_chat": id_chat,
                "id_usuario": body.get("id_usuario"),
                "id_admin": body.get("id_admin")
            })

            return JSONResponse(status_code=201, content={"message": "Participante eliminado exitosamente."})

    except DBAPIError as e:
        mensaje = str(e.orig)

        # 👇 Detectar error lanzado por el SP (por ejemplo THROW 50004)
        if "50005" in mensaje:
            raise HTTPException(status_code=409, detail="El chat no existe.")
        if "50006" in mensaje:
            raise HTTPException(status_code=409, detail="El usuario no existe.")
        if "50007" in mensaje:
            raise HTTPException(status_code=409, detail="El usuario no es parte del chat.")
        if "50008" in mensaje:
            raise HTTPException(status_code=409, detail="El Usuario no es administrador.")
        else:
            raise HTTPException(status_code=500, detail="Error de base de datos: " + mensaje)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))
