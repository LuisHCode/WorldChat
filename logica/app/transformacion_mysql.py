import pandas as pd
from conexion.conexion_mysql import obtener_conexion_mysql
from .encriptador import desencriptar
from .encriptador import desencriptar_seguro, passphrase


# --- Configuración ---
passphrase = "MiLlaveSecreta"
archivo_salida = "data/multi_tablas.xlsx"
tablas = ["Usuario", "Chat", "Participante", "Mensaje"]

# --- Conexión ---
conn = obtener_conexion_mysql()
if not conn:
    exit("🛑 No se pudo conectar a MySQL.")
cursor = conn.cursor()

# --- Exportar a Excel ---
with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
    for tabla in tablas:
        print(f"📤 Exportando tabla {tabla}...")

        query = f"SELECT * FROM {tabla}"
        df = pd.read_sql(query, conn)

        # 🔓 Desencriptar si es necesario
        if tabla == "Usuario" and not df.empty and "contrasenna" in df.columns:
            df["contrasenna_texto"] = df["contrasenna"].apply(
                lambda b: desencriptar(b, passphrase) if pd.notna(b) else None
            )

        if tabla == "Mensaje" and not df.empty and "contenido" in df.columns:
            df["contenido_texto"] = df["contenido"].apply(
                lambda b: desencriptar(b, passphrase) if pd.notna(b) else None
            )

        df.to_excel(writer, sheet_name=tabla[:31], index=False)
        print(f"✅ {tabla} exportada.")

# --- Cierre ---
cursor.close()
conn.close()
print(f"\n🎯 Exportación desde MySQL completada. Archivo generado: {archivo_salida}")
