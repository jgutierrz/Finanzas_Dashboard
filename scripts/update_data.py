# scripts/update_data.py

from src.notion_api import query_database, get_categorias
from src.extractor import extract_rows
import pandas as pd

def actualizar_datos():
    data = query_database()
    categorias_dict = get_categorias()

    df = extract_rows(data, categorias_dict)

    df.to_csv("data/processed/datos.csv", index=False)

    return len(df)

# para ejecución manual
if __name__ == "__main__":
    total = actualizar_datos()
    print(f"✅ Datos actualizados: {total} registros")