import requests
from .config import NOTION_TOKEN

NOTION_VERSION = "2022-06-28"


class NotionClient:

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json"
        }

    def query_database(self, database_id):
        url = f"https://api.notion.com/v1/databases/{database_id}/query"

        all_results = []
        has_more = True
        next_cursor = None

        while has_more:
            payload = {}

            if next_cursor:
                payload["start_cursor"] = next_cursor

            response = requests.post(url, headers=self.headers, json=payload)

            if response.status_code != 200:
                raise Exception(f"Error Notion API: {response.text}")

            data = response.json()

            all_results.extend(data.get("results", []))

            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor", None)

        return all_results

    def get_categorias(self, database_id):
        results = self.query_database(database_id)

        categorias = {}

        for item in results:
            try:
                nombre = item["properties"]["Name"]["title"][0]["plain_text"]
                categorias[item["id"]] = nombre
            except (KeyError, IndexError):
                continue

        return categorias