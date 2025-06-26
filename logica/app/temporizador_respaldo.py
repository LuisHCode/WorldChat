import time
import subprocess
from datetime import datetime
import threading
from conexion.conexion_activa import (
    obtener_motor_actual,
    verificar_conexion_sqlserver,
    verificar_conexion_mysql
)

def ejecutar_backup(transformar_script, restaurar_script, tipo):
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ejecutando respaldo {tipo}: {transformar_script}")
        subprocess.call(["python", transformar_script])

        print(f"Restaurando con: {restaurar_script}")
        subprocess.call(["python", restaurar_script])
    except Exception as e:
        print(f"Error durante el respaldo {tipo}: {str(e)}")

def _temporizador():
    t_completo = 60  # cada 60 segundos se hace un respaldo completo
    t_diferencial = 30  # cada 30 segundos se hace un respaldo diferencial
    contador = 0

    while True:
        contador += 1
        hora_actual = datetime.now().strftime("%H:%M:%S")
        print(f"[{hora_actual}] Temporizador en ejecución...")

        motor = obtener_motor_actual()
        sqlserver_activo = verificar_conexion_sqlserver()
        mysql_activo = verificar_conexion_mysql()

        if motor == "sqlserver":
            print("Motor activo: SQL Server → MySQL")
            if mysql_activo:
                if contador % t_completo == 0:
                    ejecutar_backup(
                        "logica/app/transformacion_sqlserver.py",
                        "logica/app/restauracion_a_mysql.py",
                        "completo"
                    )
                    contador = 0
                elif contador % t_diferencial == 0:
                    ejecutar_backup(
                        "logica/app/transformacion_sqlserver.py",
                        "logica/app/restauracion_a_mysql.py",
                        "diferencial"
                    )
            else:
                print("MySQL no disponible. Se omite la restauración.")

        elif motor == "mysql":
            print("Motor activo: MySQL → SQL Server")
            if sqlserver_activo:
                if contador % t_completo == 0:
                    ejecutar_backup(
                        "logica/app/transformacion_mysql.py",
                        "logica/app/restauracion_a_sqlserver.py",
                        "completo"
                    )
                    contador = 0
                elif contador % t_diferencial == 0:
                    ejecutar_backup(
                        "logica/app/transformacion_mysql.py",
                        "logica/app/restauracion_a_sqlserver.py",
                        "diferencial"
                    )
            else:
                print("SQL Server no disponible. Se omite la restauración.")

        else:
            print("Ningún motor disponible actualmente. No se realiza respaldo.")

        time.sleep(1)

def iniciar_temporizador_respaldo():
    hilo = threading.Thread(target=_temporizador, daemon=True)
    hilo.start()

if __name__ == "__main__":
    _temporizador()
