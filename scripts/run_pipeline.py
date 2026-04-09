from src.notion_api import query_database
from src.extractor import extract_rows
from src.transform import clean_data
from src.analysis import calcular_flujo

data = query_database()
df = extract_rows(data)
df = clean_data(df)
df = calcular_flujo(df)

df.to_csv("data/processed/datos.csv", index=False)

print("Pipeline ejecutado correctamente")