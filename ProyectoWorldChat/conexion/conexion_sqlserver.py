import pyodbc

BASE_DATOS = "ProyectoBD"
SERVIDOR = "localhost"

def obtener_conexion_sqlserver():
    try:
        # Conexión normal a la base de datos
        conexion = pyodbc.connect(
            f"DRIVER={{SQL Server}};SERVER={SERVIDOR};DATABASE={BASE_DATOS};Trusted_Connection=yes;",
            timeout=5
        )
        print(f"✅ Conexión a SQL Server con base '{BASE_DATOS}' exitosa.")
        return conexion
    except pyodbc.Error as e:
        print(f"⚠️  No se pudo conectar a la base '{BASE_DATOS}': {e}")
        print("🔄 Intentando conexión sin base de datos para crearla...")

        try:
            # Conexión sin especificar base de datos
            conexion = pyodbc.connect(
                f"DRIVER={{SQL Server}};SERVER={SERVIDOR};Trusted_Connection=yes;",
                timeout=5,
                autocommit=True  #  NECESARIO para CREATE DATABASE
            )
            print("✅ Conexión a SQL Server sin base. Lista para crear estructura.")
            return conexion
        except pyodbc.Error as err:
            print("❌ Error al conectar a SQL Server sin base:", str(err))
            return None
