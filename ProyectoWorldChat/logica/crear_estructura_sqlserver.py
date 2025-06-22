from conexion.conexion_sqlserver import obtener_conexion_sqlserver

def crear_estructura_sqlserver(cursor):
    cursor.execute("IF DB_ID('ProyectoBD') IS NULL CREATE DATABASE ProyectoBD;")
    cursor.execute("USE ProyectoBD;")

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Usuario' AND xtype='U')
        CREATE TABLE Usuario (
            id_usuario INT IDENTITY(1,1) PRIMARY KEY,
            nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
            nombre_completo VARCHAR(100) NOT NULL,
            telefono VARCHAR(20) UNIQUE NOT NULL,
            correo VARCHAR(100) UNIQUE NOT NULL,
            contrasenna VARBINARY(MAX) NOT NULL,
            foto_perfil VARCHAR(255),
            estado VARCHAR(20),
            fecha_creacion DATETIME DEFAULT GETDATE(),
            ultimo_ingreso DATETIME
        );
    """)

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Chat' AND xtype='U')
        CREATE TABLE Chat (
            id_chat INT IDENTITY(1,1) PRIMARY KEY,
            nombre_chat VARCHAR(100) NOT NULL,
            id_creador INT NOT NULL,
            fecha_creacion DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (id_creador) REFERENCES Usuario(id_usuario)
        );
    """)

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Participante' AND xtype='U')
        CREATE TABLE Participante (
            id_participante INT IDENTITY(1,1) PRIMARY KEY,
            id_chat INT NOT NULL,
            id_usuario INT NOT NULL,
            rol VARCHAR(20),
            FOREIGN KEY (id_chat) REFERENCES Chat(id_chat),
            FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
        );
    """)

    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Mensaje' AND xtype='U')
        CREATE TABLE Mensaje (
            id_mensaje INT IDENTITY(1,1) PRIMARY KEY,
            id_emisor INT NOT NULL,
            id_receptor INT,
            id_chat INT,
            contenido VARBINARY(MAX) NOT NULL,
            fecha_envio DATETIME DEFAULT GETDATE(),
            estado_envio VARCHAR(20) NOT NULL,
            FOREIGN KEY (id_emisor) REFERENCES Usuario(id_usuario),
            FOREIGN KEY (id_receptor) REFERENCES Usuario(id_usuario),
            FOREIGN KEY (id_chat) REFERENCES Chat(id_chat)
        );
    """)

# si se ejecuta directamente:
if __name__ == "__main__":
    conn = obtener_conexion_sqlserver()
    if not conn:
        exit("🛑 No se pudo conectar a SQL Server.")
    cursor = conn.cursor()
    crear_estructura_sqlserver(cursor)
    conn.commit()
    print("✅ Estructura creada (ejecutado directamente).")
    cursor.close()
    conn.close()