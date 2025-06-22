import sys
import os

# Asegura que la carpeta raíz del proyecto esté en sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib
from conexion.conexion_sqlserver import obtener_conexion_sqlserver
from conexion.conexion_mysql import obtener_conexion_mysql



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

def ejecutar_opcion(opcion):
    if opcion == "1":
        import logica.crear_estructura_sqlserver as m
        conn = obtener_conexion_sqlserver()
        if conn:
            cursor = conn.cursor()
            m.crear_estructura_sqlserver(cursor)
            conn.commit()
            cursor.close()
            conn.close()

    elif opcion == "2":
        import logica.crear_estructura_mysql as m
        conn = obtener_conexion_mysql()
        if conn:
            cursor = conn.cursor()
            m.crear_estructura_si_no_existe_mysql(cursor)
            conn.commit()
            cursor.close()
            conn.close()

    elif opcion == "3":
        import logica.restauracion_a_sqlserver

    elif opcion == "4":
        import logica.restauracion_a_mysql

    elif opcion == "5":
        import logica.transformacion_sqlserver

    elif opcion == "6":
        import logica.transformacion_mysql

    elif opcion == "7":
        conn = obtener_conexion_sqlserver()
        if conn:
            print("✅ Conexión a SQL Server verificada correctamente.")
            conn.close()
        else:
            print("❌ No se pudo conectar a SQL Server.")

    elif opcion == "8":
        conn = obtener_conexion_mysql()
        if conn:
            print("✅ Conexión a MySQL verificada correctamente.")
            conn.close()
        else:
            print("❌ No se pudo conectar a MySQL.")

    elif opcion == "9":
        from logica.ver_datos_desencriptados import main as ver_datos_main
        ver_datos_main()

    elif opcion == "0":
        print("Saliendo del sistema.")
        exit()

    else:
        print("❌ Opción no válida.")

# --- Main loop ---
if __name__ == "__main__":
    while True:
        limpiar_consola()
        mostrar_menu()
        opcion = input("Selecciona una opción: ").strip()
        limpiar_consola()
        ejecutar_opcion(opcion)
        input("\nPresiona ENTER para continuar...")
