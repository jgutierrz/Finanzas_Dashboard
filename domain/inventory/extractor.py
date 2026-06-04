import pandas as pd


# ---------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------
def get_title(prop):

    if not prop or "title" not in prop:
        return ""

    return "".join(
        x.get("plain_text", "")
        for x in prop["title"]
    )


def get_rich_text(prop):

    if not prop or "rich_text" not in prop:
        return ""

    return "".join(
        x.get("plain_text", "")
        for x in prop["rich_text"]
    )


def get_number(prop):

    if not prop:
        return None

    return prop.get("number")


def get_select(prop):

    if not prop or not prop.get("select"):
        return ""

    return prop["select"].get("name", "")


def get_multi_select(prop):

    if not prop or "multi_select" not in prop:
        return ""

    return ", ".join(
        x.get("name", "")
        for x in prop["multi_select"]
    )


def get_date(prop):

    if not prop or not prop.get("date"):
        return None

    return prop["date"].get("start")


def get_checkbox(prop):

    if not prop:
        return False

    return prop.get("checkbox", False)


def get_relation(prop):

    if not prop or "relation" not in prop:
        return ""

    return ", ".join(
        item.get("id", "")
        for item in prop["relation"]
    )


def get_formula(prop):

    if not prop or "formula" not in prop:
        return ""

    formula = prop["formula"]

    tipo = formula.get("type")

    if tipo == "string":
        return formula.get("string", "")

    elif tipo == "number":
        return formula.get("number")

    elif tipo == "boolean":
        return formula.get("boolean")

    elif tipo == "date":

        fecha = formula.get("date")

        if fecha:
            return fecha.get("start")

    return ""


# ---------------------------------------------------------
# Parser genérico propiedades Notion
# ---------------------------------------------------------
def parse_property(prop):

    tipo = prop.get("type")

    if tipo == "title":
        return get_title(prop)

    elif tipo == "rich_text":
        return get_rich_text(prop)

    elif tipo == "number":
        return get_number(prop)

    elif tipo == "select":
        return get_select(prop)

    elif tipo == "multi_select":
        return get_multi_select(prop)

    elif tipo == "date":
        return get_date(prop)

    elif tipo == "checkbox":
        return get_checkbox(prop)

    elif tipo == "relation":
        return get_relation(prop)

    elif tipo == "formula":
        return get_formula(prop)

    return ""


# ---------------------------------------------------------
# Extracción principal
# ---------------------------------------------------------
def extract_inventory_rows(data, personal_data=None):
    """
    Convierte registros de Notion Inventario
    a DataFrame limpio y estructurado.
    """

    rows = []

    for item in data.get("results", []):

        props = item.get("properties", {})

        row = {}

        # -------------------------------------------------
        # Procesar propiedades
        # -------------------------------------------------
        for nombre, prop in props.items():

            row[nombre] = parse_property(prop)

        rows.append(row)

    # -----------------------------------------------------
    # Crear DataFrame
    # -----------------------------------------------------
    df = pd.DataFrame(rows)

    # -----------------------------------------------------
    # Renombrar columnas
    # -----------------------------------------------------
    rename_map = {
        "Categoria": "Tipo",
        "Caracteristicas": "Especificaciones Tecnicas",
    }

    df = df.rename(columns=rename_map)

    # -----------------------------------------------------
    # Columnas finales
    # -----------------------------------------------------
    columnas_finales = [
        "Estado",
        "Asignado",
        "Fecha Compra",
        "Proveedor",
        "Serie",
        "Tipo",
        "Marca",
        "Modelo",
        "Color",
        "Especificaciones Tecnicas",
        "Observaciones",
        "Factura",
    ]

    # Crear columnas faltantes
    for col in columnas_finales:

        if col not in df.columns:
            df[col] = ""

    # -----------------------------------------------------
    # Ordenar columnas
    # -----------------------------------------------------
    df = df[columnas_finales]

    # -----------------------------------------------------
    # Convertir fechas
    # -----------------------------------------------------
    if "Fecha Compra" in df.columns:

        df["Fecha Compra"] = pd.to_datetime(
            df["Fecha Compra"],
            errors="coerce"
        )

    return df