import mysql.connector
from mysql.connector import Error

# Nombre de la base de datos
BASE_DATOS = "ProyectoBD"
CONTRA = "mora1112"

# Intenta conectar a la base de datos. Si no existe, se conecta sin base.
def obtener_conexion_mysql(auto_detectar=True):
    try:
        if auto_detectar:
            # Primero intentamos conectarnos a la base normalmente
            conexion = mysql.connector.connect(
                host='localhost',
                user='root',
                password=CONTRA,
                database=BASE_DATOS,
                connection_timeout=5
            )
            if conexion.is_connected():
                print(f"✅ Conexión a MySQL con base '{BASE_DATOS}' exitosa.")
                return conexion
        else:
            raise Exception("Forzando conexión sin base.")
    except:
        try:
            # Si falla, nos conectamos sin base para crearla
            conexion = mysql.connector.connect(
                host='localhost',
                user='root',
                password=CONTRA,
                connection_timeout=5
            )
            if conexion.is_connected():
                print("⚠️  Conexión a MySQL sin base. La base aún no existe.")
                return conexion
        except Error as e:
            print("❌ Error al conectar a MySQL:", str(e))
            return None

# --- Prueba de Conexion ---
if __name__ == "__main__":
    conexion = obtener_conexion_mysql()
    if conexion:
        conexion.close()
