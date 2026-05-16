import requests
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

# Validación básica
if not NOTION_TOKEN or not DATABASE_ID:
    print("❌ Falta NOTION_TOKEN o DATABASE_ID en el .env")
    exit()

url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28"
}

try:
    response = requests.post(url, headers=headers)
    print("STATUS:", response.status_code)

    data = response.json()  # 👈 AQUÍ se define

    if response.status_code != 200:
        print("❌ Error en la API:")
        print(json.dumps(data, indent=2))
        exit()

    results = data.get("results", [])

    print("✅ Total registros:", len(results))

    if len(results) > 0:
        print("\n🔍 Primer registro (resumen):")
        print(json.dumps(results[0]["properties"], indent=2))

except Exception as e:
    print("❌ Error ejecutando script:")
    print(str(e))