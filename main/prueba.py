from conexion.conexion_sqlserver import obtener_conexion_sqlserver
from logica.app.encriptador import encriptar, desencriptar, passphrase

conn = obtener_conexion_sqlserver()
cursor = conn.cursor()

texto = "clave123"
cifrada = encriptar(texto, passphrase)

cursor.execute("""
    INSERT INTO Usuario (nombre_usuario, nombre_completo, telefono, correo, contrasenna, estado)
    VALUES (?, ?, ?, ?, ?, ?)
""", ("testuser", "Test User", "8888-8898", "test@example.com", cifrada, "Activo"))

conn.commit()
cursor.close()
conn.close()
