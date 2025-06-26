import threading
import time
import os
from sqlalchemy.exc import SQLAlchemyError
from conexion.conexion_sqlserver import obtener_conexion_sqlserver
from conexion.conexion_mysql import obtener_conexion_mysql

conexion_actual = "sqlserver"
lock = threading.Lock()

def obtener_motor_actual():
    with lock:
        return conexion_actual

def obtener_db():
    motor = obtener_motor_actual()
    if motor == "sqlserver":
        from conexion.conexion_sqlserver import obtener_conexion_sqlserver as conn
    else:
        from conexion.conexion_mysql import obtener_conexion_mysql as conn
    return conn()

def verificar_conexion_sqlserver():
    try:
        conn = obtener_conexion_sqlserver()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return True
        return False
    except Exception as e:
        print("Error verificando SQL Server:", e)
        return False

def verificar_conexion_mysql():
    try:
        conn = obtener_conexion_mysql()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchall()
            cursor.close()
            conn.close()
            return True
        return False
    except Exception as e:
        print("Error verificando MySQL:", str(e))
        return False

def restaurar_base_sqlserver():
    print("Restaurando en SQL Server desde MySQL...")
    os.system("python logica/app/restauracion_a_sqlserver.py")

def _verificador():
    global conexion_actual

    while True:
        sqlserver_activo = verificar_conexion_sqlserver()
        mysql_activo = verificar_conexion_mysql()

        if sqlserver_activo:
            nuevo_estado = "sqlserver"
        elif mysql_activo:
            nuevo_estado = "mysql"
        else:
            nuevo_estado = None

        with lock:
            if nuevo_estado and nuevo_estado != conexion_actual:
                print(f"Cambio de motor activo a: {nuevo_estado}")
                anterior = conexion_actual
                conexion_actual = nuevo_estado

                if nuevo_estado == "sqlserver" and anterior == "mysql":
                    restaurar_base_sqlserver()

        time.sleep(10)

def iniciar_hilo_verificacion():
    hilo = threading.Thread(target=_verificador, daemon=True)
    hilo.start()
