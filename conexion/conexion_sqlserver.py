from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pyodbc

SERVIDOR = "localhost"
BASE_DATOS = "ProyectoBD"
DRIVER_ODBC = "ODBC+Driver+17+for+SQL+Server"

DATABASE_URL = (
    f"mssql+pyodbc://{SERVIDOR}/{BASE_DATOS}"
    f"?driver={DRIVER_ODBC}"
    f"&trusted_connection=yes"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def obtener_conexion_sqlserver():
    try:
        conn = pyodbc.connect(
            "DRIVER={SQL Server};SERVER=localhost;DATABASE=ProyectoBD;Trusted_Connection=yes;",
            autocommit=True
        )
        return conn
    except Exception as e:
        print("Error de conexión:", e)
        return None
    
def obtener_conexion_sqlserver_dep():
    """Para usar con Depends en FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()