from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from logica.controllers.Usuario import usuario_router
from logica.controllers.Mensaje import mensaje_router
from logica.controllers.Chat import chat_router
from logica.controllers.Participante import participante_router
from conexion.conexion_activa import iniciar_hilo_verificacion
from logica.app.temporizador_respaldo import iniciar_temporizador_respaldo
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia "*" por tu frontend si usas un dominio específico
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

@app.on_event("startup")
async def iniciar_conexiones():
    iniciar_hilo_verificacion()
    iniciar_temporizador_respaldo() 

@app.get("/")
async def root():
    return PlainTextResponse("Hola Mundo!")

app.include_router(usuario_router)
app.include_router(mensaje_router)
app.include_router(chat_router)
app.include_router(participante_router)
