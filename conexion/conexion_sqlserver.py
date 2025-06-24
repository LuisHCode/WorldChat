from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

# ✅ Ahora esta función es directamente usable en Depends()
def obtener_conexion_sqlserver():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
