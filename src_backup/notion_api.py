import requests
from .config import NOTION_TOKEN, DATABASE_ID

def query_database():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28"
    }

    all_results = []
    has_more = True
    next_cursor = None

    while has_more:
        payload = {}

        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        results = data.get("results", [])
        all_results.extend(results)

        has_more = data.get("has_more", False)
        next_cursor = data.get("next_cursor", None)

    return {"results": all_results}

def get_categorias():
    import requests
    import os

    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    CATEGORIAS_DB_ID = os.getenv("CATEGORIAS_DB_ID")

    url = f"https://api.notion.com/v1/databases/{CATEGORIAS_DB_ID}/query"

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28"
    }

    response = requests.post(url, headers=headers)
    data = response.json()

    categorias = {}

    for item in data["results"]:
        nombre = item["properties"]["Name"]["title"][0]["plain_text"]
        categorias[item["id"]] = nombre

    return categorias