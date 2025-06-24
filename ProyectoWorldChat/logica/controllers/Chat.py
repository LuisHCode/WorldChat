from fastapi import APIRouter, Request, Response, status, Depends
from sqlalchemy import text
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from sqlalchemy.exc import DBAPIError
from datetime import datetime


import base64
from conexion import conexion_sqlserver as s
from logica.app import encriptador as en

chat_router = APIRouter(prefix="/api/chat")

@chat_router.post("/create")
async def create_chat(
    request: Request, response: Response, db=Depends(s.obtener_conexion_sqlserver)
):
    body = await request.json()
    # SQL con parámetros nombrados
    sql = text(
        """
        EXEC sp_CrearChat 
            @nombre_chat = :nombre_chat, 
            @id_creador = :id_creador 
    """
    )
    with db.begin() as trans:
        result = db.execute(sql, {
            "nombre_chat": body.get("nombre_chat"),
            "id_creador": body.get("id_creador")
        })

        # Verificar si devuelve algún resultado
        rows = result.fetchall() if result.returns_rows else []

    print("Resultado del SP:", rows)


# Sin `with db.begin()`, solo ejecutá directamente:
@chat_router.post("/create")
async def create_chat(
    request: Request,
    response: Response,
    db=Depends(s.obtener_conexion_sqlserver)
):
    body = await request.json()

    sql = text("""
        EXEC sp_CrearChat 
            @nombre_chat = :nombre_chat, 
            @id_creador = :id_creador
    """)

    try:
        result = db.execute(sql, {
            "nombre_chat": body.get("nombre_chat"),
            "id_creador": body.get("id_creador")
        })

        return JSONResponse(status_code=201, content={"message": "Chat creado exitosamente."})

    except DBAPIError as e:
        mensaje = str(e.orig)

        # 👇 Detectar error lanzado por el SP (por ejemplo THROW 50004)
        if "50004" in mensaje:
            raise HTTPException(status_code=409, detail="El usuario creador no existe.")
        else:
            raise HTTPException(status_code=500, detail="Error de base de datos: " + mensaje)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error inesperado: " + str(e))

