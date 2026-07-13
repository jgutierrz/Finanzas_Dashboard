from __future__ import annotations

from typing import Any

import pandas as pd


# =========================================================
# HELPERS
# =========================================================

def get_number(prop: dict[str, Any] | None) -> float | None:
    """
    Extrae un número desde una propiedad Number o Formula.
    """
    if not prop:
        return None

    prop_type = prop.get("type")

    if prop_type == "number":
        return prop.get("number")

    if prop_type == "formula":
        formula = prop.get("formula", {})

        if formula.get("type") == "number":
            return formula.get("number")

    return None


def get_title(prop: dict[str, Any] | None) -> str:
    """
    Extrae el texto completo de una propiedad Title.
    """
    if not prop:
        return ""

    if prop.get("type") != "title":
        return ""

    bloques = prop.get("title", [])

    return "".join(
        bloque.get("plain_text", "")
        for bloque in bloques
    )


def get_select(prop: dict[str, Any] | None) -> str | None:
    """
    Extrae el valor de una propiedad Select.
    """
    if not prop:
        return None

    if prop.get("type") == "select":
        select = prop.get("select")

        if select:
            return select.get("name")

    return None


def get_relation_id(prop: dict[str, Any] | None) -> str | None:
    """
    Extrae el primer ID de una relación.
    """
    if not prop:
        return None

    if prop.get("type") == "relation":
        relation = prop.get("relation", [])

        if relation:
            return relation[0].get("id")

    return None


def limpiar_tipo(tipo: str | None) -> str | None:
    """
    Elimina emojis utilizados en Notion.
    """
    if not tipo:
        return tipo

    return (
        tipo.replace("🔴", "")
        .replace("🟢", "")
        .replace("💰", "")
        .strip()
    )


# =========================================================
# EXTRACTOR PRINCIPAL
# =========================================================

def extract_rows(
    data: dict[str, Any],
    categorias_dict: dict[str, str] | None = None,
) -> pd.DataFrame:
    """
    Convierte la respuesta de Notion a DataFrame.
    """

    rows: list[dict[str, Any]] = []

    for item in data.get("results", []):

        props = item.get("properties", {})

        # -------------------------------------------------
        # FECHA
        # -------------------------------------------------

        fecha_prop = props.get("Fecha")

        fecha = None

        if fecha_prop and fecha_prop.get("date"):
            fecha = fecha_prop["date"].get("start")

        # -------------------------------------------------
        # TIPO
        # -------------------------------------------------

        tipo = limpiar_tipo(
            get_select(
                props.get("Tipo de Movimiento")
            )
        )

        # -------------------------------------------------
        # MONTO
        # Prioridad: Monto Ajustado
        # -------------------------------------------------

        monto = get_number(
            props.get("Monto Ajustado")
        )

        if monto is None:
            monto = get_number(
                props.get("Monto")
            )

        # -------------------------------------------------
        # DESCRIPCIÓN
        # -------------------------------------------------

        descripcion = get_title(
            props.get("Descripción Movimiento")
        )

        # -------------------------------------------------
        # CATEGORÍA
        # -------------------------------------------------

        categoria_id = get_relation_id(
            props.get("Categorías")
        )

        categoria = "No clasificado"

        if categoria_id and categorias_dict:
            categoria = categorias_dict.get(
                categoria_id,
                "No clasificado",
            )

        # -------------------------------------------------
        # ROW
        # -------------------------------------------------

        rows.append(
            {
                "fecha": fecha,
                "tipo": tipo,
                "monto": monto,
                "descripcion": descripcion,
                "categoria_id": categoria_id,
                "categoria": categoria,
            }
        )

    # =====================================================
    # DATAFRAME
    # =====================================================

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # -----------------------------------------------------
    # LIMPIEZA
    # -----------------------------------------------------

    df["fecha"] = pd.to_datetime(
        df["fecha"],
        errors="coerce",
    )

    df["monto"] = pd.to_numeric(
        df["monto"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "fecha",
            "monto",
        ]
    )

    # -----------------------------------------------------
    # COLUMNAS DERIVADAS
    # -----------------------------------------------------

    df["año"] = df["fecha"].dt.year

    df["mes_num"] = df["fecha"].dt.month

    df["mes"] = (
        df["fecha"]
        .dt.to_period("M")
        .astype(str)
    )

    df["mes_nombre"] = (
        df["fecha"]
        .dt.strftime("%B")
    )

    df["trimestre"] = (
        "T"
        + df["fecha"]
        .dt.quarter.astype(str)
    )

    # Flujo financiero (+ ingresos / - gastos)
    df["flujo"] = df["monto"]
    # -----------------------------------------------------
    # ORDEN
    # -----------------------------------------------------

    df = (
        df.sort_values(
            by="fecha",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return df