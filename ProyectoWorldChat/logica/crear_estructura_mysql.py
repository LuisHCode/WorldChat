from conexion.conexion_mysql import obtener_conexion_mysql

def crear_estructura_si_no_existe_mysql(cursor):
    # Crear base de datos si no existe
    cursor.execute("CREATE DATABASE IF NOT EXISTS ProyectoBD;")
    cursor.execute("USE ProyectoBD;")

    # Tabla Usuario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
            nombre_completo VARCHAR(100) NOT NULL,
            telefono VARCHAR(20) UNIQUE NOT NULL,
            correo VARCHAR(100) UNIQUE NOT NULL,
            contrasenna VARBINARY(4096) NOT NULL,
            foto_perfil VARCHAR(255),
            estado VARCHAR(20),
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultimo_ingreso DATETIME
        );
    """)

    # Tabla Chat
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Chat (
            id_chat INT AUTO_INCREMENT PRIMARY KEY,
            nombre_chat VARCHAR(100) NOT NULL,
            id_creador INT NOT NULL,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_creador) REFERENCES Usuario(id_usuario)
        );
    """)

    # Tabla Participante
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Participante (
            id_participante INT AUTO_INCREMENT PRIMARY KEY,
            id_chat INT NOT NULL,
            id_usuario INT NOT NULL,
            rol VARCHAR(20),
            FOREIGN KEY (id_chat) REFERENCES Chat(id_chat),
            FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
        );
    """)

    # Tabla Mensaje
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Mensaje (
            id_mensaje INT AUTO_INCREMENT PRIMARY KEY,
            id_emisor INT NOT NULL,
            id_receptor INT DEFAULT NULL,
            id_chat INT DEFAULT NULL,
            contenido VARBINARY(4096) NOT NULL,
            fecha_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
            estado_envio VARCHAR(20) NOT NULL,
            FOREIGN KEY (id_emisor) REFERENCES Usuario(id_usuario),
            FOREIGN KEY (id_receptor) REFERENCES Usuario(id_usuario),
            FOREIGN KEY (id_chat) REFERENCES Chat(id_chat)
        );
    """)

# --- Ejecutar si se corre directamente ---
if __name__ == "__main__":
    try:
        conn = obtener_conexion_mysql(auto_detectar=True)
        if not conn:
            exit("🛑 No se pudo conectar a MySQL.")
        cursor = conn.cursor()
        crear_estructura_si_no_existe_mysql(cursor)
        conn.commit()
        print("✅ Base de datos y tablas creadas (si no existían).")
    except Exception as e:
        print("❌ Error al crear la estructura:", str(e))
    finally:
        cursor.close()
        conn.close()
