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

    def query_database(self, FINANZAS_DB_ID):
        url = f"https://api.notion.com/v1/databases/{FINANZAS_DB_ID}/query"

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

    def get_categorias(self, FINANZAS_DB_ID):
        results = self.query_database(FINANZAS_DB_ID)

        categorias = {}

        for item in results:
            try:
                nombre = item["properties"]["Name"]["title"][0]["plain_text"]
                categorias[item["id"]] = nombre
            except (KeyError, IndexError):
                continue

        return categorias
    
    def get_personal(self, FINANZAS_DB_ID):
        """
        Obtiene la base Personal y devuelve un diccionario:
        {id_del_registro: nombre_de_la_persona}
        """
        results = self.query_database(FINANZAS_DB_ID)

        personal = {}

        for item in results:
            try:
                # Obtener el título de la página (nombre de la persona)
                props = item["properties"]

                # Buscar la propiedad de tipo "title"
                nombre = ""
                for _, prop in props.items():
                    if prop["type"] == "title":
                        nombre = "".join(
                            x.get("plain_text", "")
                            for x in prop.get("title", [])
                        )
                        break

                # Guardar en diccionario: {id: nombre}
                personal[item["id"]] = nombre

            except Exception:
                # Si algún registro tiene problemas, no detener el proceso
                pass

        return personal