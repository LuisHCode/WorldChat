from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from logica.controllers.Usuario import usuario_router
from logica.controllers.Mensaje import mensaje_router
from logica.controllers.Chat import chat_router
from logica.controllers.Participante import participante_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# Agregar middleware CORS a la app de FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia "*" por tu frontend si usas un dominio específico
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

# Ruta raíz
@app.get("/")
async def root():
    return PlainTextResponse("Hola Mundo!")

# Registrar los routers en la app
app.include_router(usuario_router)
app.include_router(mensaje_router)
app.include_router(chat_router)
app.include_router(participante_router)
