import pandas as pd
from src.analysis import calcular_flujo, resumen_mensual

df = pd.read_csv("data/processed/datos.csv")

df = calcular_flujo(df)
resumen = resumen_mensual(df)

print("📊 Balance mensual:")
print(resumen)