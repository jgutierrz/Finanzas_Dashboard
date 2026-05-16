from services.finanzas_service import obtener_finanzas

df = obtener_finanzas()

print(df.head())
print(f"Registros: {len(df)}")