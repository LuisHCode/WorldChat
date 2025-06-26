import sys
import os
import subprocess
import webbrowser
import requests
import time
from threading import Timer
from pathlib import Path

# Configuración de paths
BASE_DIR = Path(__file__).parent.parent
PRESENTACION_DIR = BASE_DIR / "presentacion"
HTML_FILE = PRESENTACION_DIR / "src" / "index.html"
API_URL = "http://127.0.0.1:8000"  # URL base de la API

# Asegura que la carpeta raíz del proyecto esté en sys.path
sys.path.append(str(BASE_DIR))

def limpiar_consola():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_menu():
    print("""
 WORLDCHAT - Mensajería

1️⃣  Crear estructura en SQL Server
2️⃣  Crear estructura en MySQL
3️⃣  Restaurar datos en SQL Server desde Excel
4️⃣  Restaurar datos en MySQL desde Excel
5️⃣  Exportar datos desde SQL Server a Excel
6️⃣  Exportar datos desde MySQL a Excel
7️⃣  Verificar conexión a SQL Server
8️⃣  Verificar conexión a MySQL
9️⃣  Ver datos desencriptados (pruebas)
🔟  Iniciar servidor de chat (FastAPI + Interfaz)
0️⃣  Salir
""")

def verificar_servidor():
    """Verifica si el servidor está respondiendo"""
    try:
        response = requests.get(f"{API_URL}/docs", timeout=2)
        return response.status_code == 200
    except:
        return False

def iniciar_servidor_chat():
    """Inicia el servidor FastAPI y abre el navegador con la interfaz"""
    try:
        # Comando para iniciar el servidor FastAPI
        fastapi_cmd = "python -m uvicorn logica.app.routes:app --reload"
        
        # Verificar si el servidor ya está corriendo
        if verificar_servidor():
            print("✅ El servidor ya está en ejecución")
            abrir_navegador()
            return
        
        # Iniciar el servidor en un proceso separado
        server_process = subprocess.Popen(
            fastapi_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=BASE_DIR
        )
        
        # Esperar a que el servidor esté listo
        print("⏳ Iniciando servidor API...", end='', flush=True)
        for _ in range(10):  # Esperar máximo 10 segundos
            if verificar_servidor():
                print("\n✅ Servidor API listo en", API_URL)
                abrir_navegador()
                return
            print('.', end='', flush=True)
            time.sleep(1)
        
        print("\n❌ El servidor no respondió a tiempo")
        
    except Exception as e:
        print(f"\n❌ Error al iniciar el servidor: {e}")

def abrir_navegador():
    """Abre el navegador con la interfaz HTML"""
    try:
        html_path = f"file://{HTML_FILE.absolute()}"
        
        if not HTML_FILE.exists():
            print(f"❌ Archivo HTML no encontrado en: {html_path}")
            return
        
        webbrowser.open(html_path)
        print(f"🌐 Navegador abierto en: {html_path}")
        print("\n🔍 Verifica lo siguiente si las rutas no funcionan:")
        print("1. Que tu HTML use URLs absolutas como http://localhost:8000/api/ruta")
        print("2. Que CORS esté configurado correctamente en tu API")
        print("3. Que no haya errores en la consola del navegador (F12)")
        
    except Exception as e:
        print(f"❌ Error al abrir navegador: {e}")

def ejecutar_opcion(opcion):
    """Ejecuta la opción seleccionada"""
    if opcion == "10":
        iniciar_servidor_chat()
    else:
        # Importar y ejecutar la lógica original
        from app import ejecutar_opcion as ejecutar_opcion_original
        ejecutar_opcion_original(opcion)

if __name__ == "__main__":
    while True:
        limpiar_consola()
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()
        
        if opcion == "0":
            print("Saliendo del programa...")
            break
            
        limpiar_consola()
        ejecutar_opcion(opcion)
        
        if opcion != "10":  # No pausar si inició el servidor
            input("\nPresiona ENTER para continuar...")