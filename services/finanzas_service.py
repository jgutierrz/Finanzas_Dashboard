from infrastructure.notion_client import NotionClient
from infrastructure.config import FINANZAS_DB_ID, CATEGORIAS_DB_ID
from domain.finanzas.extractor import extract_rows


def obtener_finanzas():
    """
    Obtiene los datos de Notion y devuelve un DataFrame procesado.
    """
    client = NotionClient()

    # Consultar Notion
    results = client.query_database(FINANZAS_DB_ID)
    categorias = client.get_categorias(CATEGORIAS_DB_ID)

    # Mantener compatibilidad con extract_rows()
    data = {"results": results}

    # Convertir a DataFrame
    df = extract_rows(data, categorias)
    
    return df