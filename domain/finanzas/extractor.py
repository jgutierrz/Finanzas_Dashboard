import pandas as pd

# -------------------------
# 🧩 HELPERS
# -------------------------
def get_number(prop):
    if not prop:
        return None

    if prop["type"] == "number":
        return prop.get("number")

    elif prop["type"] == "formula":
        formula = prop.get("formula", {})
        if formula.get("type") == "number":
            return formula.get("number")

    return None


def get_title(prop):
    if prop["type"] == "title" and prop["title"]:
        return prop["title"][0]["plain_text"]
    return ""


def get_select(prop):
    if prop["type"] == "select" and prop["select"]:
        return prop["select"]["name"]
    return None


def get_relation_id(prop):
    if prop["type"] == "relation" and prop["relation"]:
        return prop["relation"][0]["id"]
    return None


def limpiar_tipo(tipo):
    if tipo:
        tipo = tipo.replace("🔴", "").replace("🟢", "").replace("💰", "")
        return tipo.strip()
    return tipo


# -------------------------
# 🚀 FUNCIÓN PRINCIPAL
# -------------------------
def extract_rows(data, categorias_dict=None):

    rows = []

    for item in data["results"]:
        props = item["properties"]

        # -------------------------
        # 📅 FECHA
        # -------------------------
        fecha = props["Fecha"]["date"]["start"] if props["Fecha"]["date"] else None

        # -------------------------
        # 🔄 TIPO
        # -------------------------
        tipo = limpiar_tipo(get_select(props["Tipo de Movimiento"]))

        # -------------------------
        # 💰 MONTO (prioridad fórmula)
        # -------------------------
        monto = get_number(props.get("Monto Ajustado"))

        if monto is None:
            monto = get_number(props.get("Monto"))

        # -------------------------
        # 📝 DESCRIPCIÓN
        # -------------------------
        descripcion = get_title(props["Descripción Movimiento"])

        # -------------------------
        # 🧩 CATEGORÍA (RELATION)
        # -------------------------
        categoria_id = get_relation_id(props["Categorías"])

        categoria_nombre = "No clasificado"

        if categoria_id and categorias_dict:
            categoria_nombre = categorias_dict.get(categoria_id, "No clasificado")

        # -------------------------
        # 🧾 ROW
        # -------------------------
        rows.append({
            "fecha": fecha,
            "tipo": tipo,
            "monto": monto,
            "descripcion": descripcion,
            "categoria_id": categoria_id,
            "categoria": categoria_nombre
        })

    # -------------------------
    # 📊 DATAFRAME
    # -------------------------
    df = pd.DataFrame(rows)

    # limpieza segura
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce")

    df = df.dropna(subset=["fecha", "monto"])

    # columnas derivadas
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    df["año"] = df["fecha"].dt.year

    return df