from domain.inventory.extractor import extract_inventory_rows
from infrastructure.config import INVENTARIO_DB_ID
from infrastructure.notion_client import NotionClient

ESTADOS_INACTIVOS = ["DE BAJA", "POR ASIGNAR"]


def obtener_inventario():

    client = NotionClient()

    # -------------------------------------------------
    # Consultar base Inventario
    # -------------------------------------------------
    results = client.query_database(INVENTARIO_DB_ID)

    data = {"results": results}

    # -------------------------------------------------
    # Extraer DataFrame completo
    # -------------------------------------------------
    df = extract_inventory_rows(data)

    # -------------------------------------------------
    # Guardar histórico completo
    # -------------------------------------------------
    df.to_csv("data/processed/inventario_historico.csv", index=False)

    # -------------------------------------------------
    # Filtrar activos
    # -------------------------------------------------
    if "Estado" in df.columns:
        estados = df["Estado"].fillna("").astype(str).str.strip().str.upper()

        df = df[~estados.isin(ESTADOS_INACTIVOS)]

    # -------------------------------------------------
    # Guardar inventario activo
    # -------------------------------------------------
    df.to_csv("data/processed/inventario.csv", index=False)

    return df
