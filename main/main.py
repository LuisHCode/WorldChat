import sys
import os

# Asegura que la carpeta raíz del proyecto esté en sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib
from conexion.conexion_sqlserver import obtener_conexion_sqlserver
from conexion.conexion_mysql import obtener_conexion_mysql
from app import ejecutar_opcion  # Importar la función de app.py

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
0️⃣  Salir
""")



# --- Main loop ---
if __name__ == "__main__":
    while True:
        limpiar_consola()
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()
        limpiar_consola()
        ejecutar_opcion(opcion)  # Llamar a la función de app.py
        input("\nPresiona ENTER para continuar...")