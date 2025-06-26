import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
# ...el resto de tus imports...
from conexion.conexion_mysql    import obtener_conexion_mysql
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Dependencia de conexión ya existente en tu proyecto
from conexion.conexion_sqlserver import obtener_conexion_sqlserver

# Utilidades de cifrado ya existentes
from logica.app.encriptador import desencriptar, passphrase


def verificar_credenciales(identificador: str, pwd_plano: str, db=None):
    """Comprueba si la contraseña enviada coincide con la almacenada.

    Args:
        identificador (str): Correo o teléfono del usuario.
        pwd_plano (str): Contraseña que el usuario acaba de introducir (texto plano).
        db (Session | None): Sesión SQLAlchemy opcional. Si no se pasa, se crea
            una conexión nueva y se cierra al finalizar.

    Returns:
        int | None: id_usuario si la contraseña es correcta, None en cualquier otro caso.
    """

    # ---------------------------------------------------
    # 1. Preparar conexión
    # ---------------------------------------------------
    nueva_sesion = False
    if db is None:
        db = obtener_conexion_sqlserver()
        nueva_sesion = True

    
    try:
        # ---------------------------------------------------
        # 2. Traer solo la columna "contrasenna" para el usuario
        # ---------------------------------------------------
        sql = """
            SELECT TOP (1) id_usuario, contrasenna
            FROM   Usuario
            WHERE  correo   = ?
               OR  telefono = ?
        """
        cursor = db.cursor()
        cursor.execute(sql, (identificador, identificador))
        row = cursor.fetchone()

        # Usuario no encontrado o sin contraseña
        if row is None or row[1] is None:
            return None

        id_usuario = row[0]
        contrasenna_cifrada: bytes = row[1]
        
        
        
        
        
        
        
        
        

        # ---------------------------------------------------
        # 3. Desencriptar de forma segura
        # ---------------------------------------------------
        try:
            contrasenna_desencriptada = desencriptar(contrasenna_cifrada, passphrase)
        except Exception:
            return None

        return id_usuario if contrasenna_desencriptada == pwd_plano else None

    except Exception:
        return None

    finally:
        if nueva_sesion:
            db.close()
            
       
            

def verificar_credencialesmysql(identificador: str, pwd_plano: str, db=None):
    """Comprueba si la contraseña enviada coincide con la almacenada (MySQL).

    Args:
        identificador (str): Correo o teléfono del usuario.
        pwd_plano (str): Contraseña en texto plano.
        db (MySQLConnection | None): Conexión opcional. Si no se pasa, la función
            abrirá una nueva y la cerrará al final.

    Returns:
        int: 1 si la contraseña es correcta, 0 en caso contrario.
    """

    # ---------------------------------------------------
    # 1. Preparar conexión
    # ---------------------------------------------------
    nueva_conexion = False
    if db is None:
        db = obtener_conexion_mysql()
        nueva_conexion = True

    try:
        # ---------------------------------------------------
        # 2. Traer solo la columna "contrasenna" para el usuario
        # ---------------------------------------------------
        sql = (
            """
            SELECT id_usuario, contrasenna
            FROM   Usuario
            WHERE  correo   = %s
               OR  telefono = %s
            LIMIT 1
            """
        )
        cursor = db.cursor()
        cursor.execute(sql, (identificador, identificador))
        row = cursor.fetchone()

        # Usuario no encontrado o sin contraseña
        if row is None or row[1] is None:
            return None

        id_usuario = row[0]
        contrasenna_cifrada: bytes = row[1]

        # ---------------------------------------------------
        # 3. Desencriptar de forma segura
        # ---------------------------------------------------
        try:
            contrasenna_desencriptada = desencriptar(contrasenna_cifrada, passphrase)
        except Exception:
            return None

        return id_usuario if contrasenna_desencriptada == pwd_plano else None
    except SQLAlchemyError:
        return None
    finally:
        if nueva_conexion:
            db.close()
