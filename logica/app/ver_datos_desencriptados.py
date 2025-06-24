from logica.encriptador import desencriptar
from conexion.conexion_sqlserver import obtener_conexion_sqlserver
from conexion.conexion_mysql import obtener_conexion_mysql
import pandas as pd

# Configuración
passphrase = "MiLlaveSecreta"

def ver_usuarios(conn, motor):
    print(f"\n Usuarios en {motor}:")
    df = pd.read_sql("SELECT * FROM Usuario", conn)
    if "contrasenna" in df.columns:
        df["contrasenna_texto"] = df["contrasenna"].apply(
            lambda b: desencriptar(b, passphrase) if pd.notna(b) else None
        )
    print(df[["id_usuario", "nombre_usuario", "correo", "contrasenna_texto"]])

def ver_mensajes(conn, motor):
    print(f"\n Mensajes en {motor}:")
    df = pd.read_sql("SELECT * FROM Mensaje", conn)
    if "contenido" in df.columns:
        df["contenido_texto"] = df["contenido"].apply(
            lambda b: desencriptar(b, passphrase) if pd.notna(b) else None
        )
    print(df[["id_mensaje", "id_emisor", "id_receptor", "contenido_texto"]])

# --- Menú ---
def main():
    print("🧪 Ver datos desencriptados")
    motor = input("¿Qué motor querés usar? (1=SQL Server, 2=MySQL): ").strip()

    if motor == "1":
        conn = obtener_conexion_sqlserver()
        if not conn:
            print("❌ Error al conectar a SQL Server.")
            return
        origen = "SQL Server"

    elif motor == "2":
        conn = obtener_conexion_mysql()
        if not conn:
            print("❌ Error al conectar a MySQL.")
            return
        origen = "MySQL"

    else:
        print("❌ Opción inválida.")
        return

    ver_usuarios(conn, origen)
    ver_mensajes(conn, origen)
    conn.close()

if __name__ == "__main__":
    main()
