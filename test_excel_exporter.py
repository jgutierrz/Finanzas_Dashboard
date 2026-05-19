import pandas as pd
from exporters.excel_exporter import exportar_finanzas_excel

# Cargar datos existentes
df = pd.read_csv("data/processed/datos.csv")

# Generar archivo Excel
archivo = exportar_finanzas_excel(df)

print(f"Archivo generado: {archivo}")