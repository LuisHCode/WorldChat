import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
from conexion.conexion_sqlserver import obtener_conexion_sqlserver
from logica.app.encriptador import encriptar
from logica.app.crear_estructura_sqlserver import crear_estructura_sqlserver


# --- Configuración ---
passphrase = "MiLlaveSecreta"
archivo_excel = "data/multi_tablas.xlsx"
tablas_ordenadas = ["Usuario", "Chat", "Participante", "Mensaje"]

# --- Conexión ---
conn = obtener_conexion_sqlserver()
if not conn:
    exit("🛑 No se pudo conectar a SQL Server.")

cursor = conn.cursor()

# --- Crear estructura si no existe ---
crear_estructura_sqlserver(cursor)
conn.commit()

# --- Limpiar tablas respetando claves foráneas ---
print(" Limpiando datos en SQL Server...")
for tabla in reversed(tablas_ordenadas):
    cursor.execute(f"DELETE FROM {tabla}")
    conn.commit()
print("Tablas limpiadas.\n")

# --- Restaurar desde Excel ---
def insertar_desde_excel(nombre_tabla, df, cursor, usar_identity=False, cifrar_col=None, destino_col=None):
    columnas = df.columns.tolist()

    # 🔧 Eliminar columna duplicada (binaria) si ya viene en el Excel
    if cifrar_col and destino_col and destino_col in columnas:
        df = df.drop(columns=[destino_col])
        columnas.remove(destino_col)

    if usar_identity:
        cursor.execute(f"SET IDENTITY_INSERT {nombre_tabla} ON")

    for _, fila in df.iterrows():
        valores = []
        columnas_sql = []

        for col in columnas:
            val = fila[col]
            if pd.isna(val):
                valores.append(None)
                columnas_sql.append(destino_col if col == cifrar_col else col)
            elif isinstance(val, pd.Timestamp):
                valores.append(val.to_pydatetime())
                columnas_sql.append(destino_col if col == cifrar_col else col)
            elif col == cifrar_col:
                valores.append(encriptar(val, passphrase))  # 🔐 Cifrado correcto
                columnas_sql.append(destino_col)
            else:
                valores.append(val)
                columnas_sql.append(col)

        placeholders = ", ".join(["?"] * len(valores))
        columnas_final = ", ".join(columnas_sql)
        sql = f"INSERT INTO {nombre_tabla} ({columnas_final}) VALUES ({placeholders})"
        cursor.execute(sql, valores)

    if usar_identity:
        cursor.execute(f"SET IDENTITY_INSERT {nombre_tabla} OFF")

    conn.commit()
    print(f"✅ {nombre_tabla} restaurada.")

# --- Conexión ---
conn = obtener_conexion_sqlserver()
if not conn:
    exit("🛑 No se pudo conectar a SQL Server.")
cursor = conn.cursor()

# --- Crear base y tablas si no existen ---
crear_estructura_sqlserver(cursor)
conn.commit()

# --- Limpiar tablas respetando claves foráneas ---
print("🧹 Limpiando datos existentes en SQL Server...")
for tabla in reversed(tablas_ordenadas):
    cursor.execute(f"DELETE FROM {tabla}")
    conn.commit()
print("✅ Tablas limpiadas.\n")

# --- Leer archivo Excel y restaurar ---
xlsx = pd.ExcelFile(archivo_excel)

insertar_desde_excel("Usuario", xlsx.parse("Usuario"), cursor, usar_identity=True, cifrar_col="contrasenna_texto", destino_col="contrasenna")
insertar_desde_excel("Chat", xlsx.parse("Chat"), cursor, usar_identity=True)
insertar_desde_excel("Participante", xlsx.parse("Participante"), cursor)
insertar_desde_excel("Mensaje", xlsx.parse("Mensaje"), cursor, usar_identity=True, cifrar_col="contenido_texto", destino_col="contenido")

# --- Cierre ---
cursor.close()
conn.close()
print("\n🎯 Restauración desde Excel a SQL Server completada con éxito.")