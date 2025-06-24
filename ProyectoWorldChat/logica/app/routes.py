from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from logica.controllers.Usuario import usuario_router
from logica.controllers.Mensaje import mensaje_router
from logica.controllers.Chat import chat_router

app = FastAPI()

# Ruta raíz
@app.get("/")
async def root():
    return PlainTextResponse("Hola Mundo!")

# Registrar los routers en la app
app.include_router(usuario_router)
app.include_router(mensaje_router)
app.include_router(chat_router)
