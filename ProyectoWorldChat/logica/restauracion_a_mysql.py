import pandas as pd
from conexion.conexion_mysql import obtener_conexion_mysql
from logica.encriptador import encriptar
from logica.crear_estructura_mysql import crear_estructura_si_no_existe_mysql
import datetime

# --- Configuración ---
passphrase = "MiLlaveSecreta"
archivo_excel = "data/replicacion_sqlserver.xlsx"
tablas_ordenadas = ["Usuario", "Chat", "Participante", "Mensaje"]

# --- Conexión ---
conn = obtener_conexion_mysql()
if not conn:
    exit("🛑 No se pudo conectar a MySQL.")
cursor = conn.cursor()

# --- Crear base y tablas si no existen ---
crear_estructura_si_no_existe_mysql(cursor)

# --- Limpiar tablas (orden inverso por claves foráneas) ---
print("🧹 Limpiando datos en MySQL...")
for tabla in reversed(tablas_ordenadas):
    cursor.execute(f"DELETE FROM {tabla}")
    conn.commit()
print("✅ Tablas limpiadas.\n")

# --- Función para insertar desde DataFrame ---
def insertar_desde_excel_mysql(nombre_tabla, df, cifrar_col=None, destino_col=None):
    columnas = df.columns.tolist()

    # 🔧 Eliminar la columna original binaria si viene del Excel (evita duplicado)
    if cifrar_col and destino_col and destino_col in columnas:
        df = df.drop(columns=[destino_col])
        columnas.remove(destino_col)
    
    for _, fila in df.iterrows():
        valores = []
        columnas_sql = []

        for col in columnas:
            val = fila[col]

            # Convertir valores nulos
            if pd.isna(val):
                valores.append(None)
                columnas_sql.append(destino_col if col == cifrar_col else col)

            # Convertir pandas.Timestamp a datetime.datetime
            elif isinstance(val, pd.Timestamp):
                valores.append(val.to_pydatetime())
                columnas_sql.append(destino_col if col == cifrar_col else col)

            # Encriptar columnas sensibles
            elif cifrar_col == col:
                valores.append(encriptar(val, passphrase))
                columnas_sql.append(destino_col)

            # Valor normal
            else:
                valores.append(val)
                columnas_sql.append(col)

        placeholders = ", ".join(["%s"] * len(valores))
        columnas_final = ", ".join(columnas_sql)

        sql = f"INSERT INTO {nombre_tabla} ({columnas_final}) VALUES ({placeholders})"
        cursor.execute(sql, valores)

    conn.commit()
    print(f"✅ {nombre_tabla} restaurada en MySQL.")

# --- Leer archivo Excel ---
xlsx = pd.ExcelFile(archivo_excel)

insertar_desde_excel_mysql("Usuario", xlsx.parse("Usuario"), cifrar_col="contrasenna_texto", destino_col="contrasenna")
insertar_desde_excel_mysql("Chat", xlsx.parse("Chat"))
insertar_desde_excel_mysql("Participante", xlsx.parse("Participante"))
insertar_desde_excel_mysql("Mensaje", xlsx.parse("Mensaje"), cifrar_col="contenido_texto", destino_col="contenido")

# --- Cierre ---
cursor.close()
conn.close()
print("\n🎯 Restauración a MySQL completada con cifrado desde Python.")
