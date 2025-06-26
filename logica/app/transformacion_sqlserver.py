import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
from conexion.conexion_sqlserver import obtener_conexion_sqlserver
from logica.app.encriptador import desencriptar
from logica.app.encriptador import desencriptar_seguro, passphrase


# --- Configuración ---
passphrase = "MiLlaveSecreta"
archivo_salida = "data/replicacion_sqlserver.xlsx"
tablas = ["Usuario", "Chat", "Participante", "Mensaje"]

# --- Conexión ---
conn = obtener_conexion_sqlserver()
if not conn:
    exit("🛑 No se pudo conectar a SQL Server.")
cursor = conn.cursor()

# --- Exportar a Excel con múltiples hojas ---
with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
    for tabla in tablas:
        print(f"📤 Exportando tabla {tabla}...")

        query = f"SELECT * FROM {tabla}"
        df = pd.read_sql(query, conn)

        # 🔓 Aplicar desencriptación si es necesario
        if tabla == "Usuario" and not df.empty:
            df["contrasenna_texto"] = df["contrasenna"].apply(
                lambda b: desencriptar_seguro(b, passphrase) if pd.notna(b) else None
            )

        if tabla == "Mensaje" and not df.empty:
            df["contenido_texto"] = df["contenido"].apply(
                lambda b: desencriptar_seguro(b, passphrase) if pd.notna(b) else None
            )

        df.to_excel(writer, sheet_name=tabla[:31], index=False)
        print(f"✅ {tabla} exportada.")

# --- Cierre ---
cursor.close()
conn.close()
print(f"\n Exportación desde SQL Server completada. Archivo generado: {archivo_salida}")
