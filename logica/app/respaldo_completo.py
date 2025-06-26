import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import os
from datetime import datetime
from conexion.conexion_activa import obtener_motor_actual

def respaldo_completo():
    motor = obtener_motor_actual()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f" [{fecha}] Iniciando respaldo completo...")

    if motor == "sqlserver":
        print(" SQL Server activo. Exportando completo a MySQL...")
        os.system("python logica/app/transformacion_sqlserver.py")
        os.system("python logica/app/restauracion_a_mysql.py")
    else:
        print(" MySQL activo. Exportando completo a SQL Server...")
        os.system("python logica/app/transformacion_mysql.py")
        os.system("python logica/app/restauracion_a_sqlserver.py")

if __name__ == "__main__":
    respaldo_completo()
