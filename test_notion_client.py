from infrastructure.notion_client import NotionClient
from infrastructure.config import DATABASE_ID

client = NotionClient()
results = client.query_database(DATABASE_ID)

print(f"Registros obtenidos: {len(results)}")