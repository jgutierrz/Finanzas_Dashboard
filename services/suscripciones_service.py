from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from domain.inventory.extractor import parse_property
from domain.suscripciones.extractor import extraer_suscripciones
from domain.suscripciones.metrics import (
    calcular_kpis,
    costos_por_proveedor,
    obtener_alertas,
    proximos_vencimientos,
    vencimientos_por_mes,
)
from domain.suscripciones.status import obtener_estado
from domain.suscripciones.transform import transformar_suscripciones
from infrastructure.config import SUSCRIPCIONES_DB_ID
from infrastructure.notion_client import NotionClient

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CSV = BASE_DIR / "data" / "processed" / "suscripciones.csv"


def _resolver_ruta(csv_path: str | Path) -> Path:
    """Convierte rutas relativas a la raíz del proyecto."""
    ruta = Path(csv_path)
    if not ruta.is_absolute():
        ruta = BASE_DIR / ruta
    return ruta


def _obtener_valor(props: dict[str, Any], nombres: list[str]) -> Any:
    """Busca un valor de Notion entre varias variantes de nombre."""
    for nombre in nombres:
        if nombre in props:
            valor = parse_property(props[nombre])
            if valor not in (None, ""):
                return valor
    return ""


def obtener_suscripciones_notion() -> pd.DataFrame:
    """Consulta Notion y devuelve un DataFrame limpio para el dashboard."""
    client = NotionClient()
    results = client.query_database(SUSCRIPCIONES_DB_ID)

    rows: list[dict[str, Any]] = []

    for item in results:
        props = item.get("properties", {})
        rows.append(
            {
                "Nombre": _obtener_valor(
                    props,
                    ["Servicio", "Suscripción", "Nombre", "Name", "Título", "Title"],
                ),
                "Proveedor": _obtener_valor(
                    props,
                    ["Proveedor", "Empresa", "Vendor"],
                ),
                "Estado": _obtener_valor(props, ["Estatus", "Estado", "Status"]),
                "Costo_Mensual": _obtener_valor(
                    props,
                    ["Precio", "Coste Mensual", "Costo Mensual", "Costo_Mensual"],
                ),
                "Fecha_Vencimiento": _obtener_valor(
                    props,
                    [
                        "Renovación",
                        "Fecha de Vencimiento",
                        "Fecha_Vencimiento",
                        "Fecha de Renovación",
                        "Vencimiento",
                        "Fecha de pago",
                    ],
                ),
                "Descripcion": _obtener_valor(
                    props,
                    [
                        "Periodicidad",
                        "Descripcion",
                        "Descripción",
                        "Description",
                        "Detalle",
                    ],
                ),
                "Grupo": _obtener_valor(props, ["Grupo", "Group"]),
                "Observaciones": _obtener_valor(
                    props,
                    ["Observaciones", "Observación", "Notes", "Facturas"],
                ),
            }
        )

    df = pd.DataFrame(rows)
    df = extraer_suscripciones(df)
    df = transformar_suscripciones(df)

    # ==========================================================
    # Estado visual de vencimiento
    # ==========================================================

    estados = df["Fecha_Vencimiento"].apply(obtener_estado)

    df["Dias_Restantes"] = estados.apply(lambda x: x["dias_restantes"])

    df["Estado_Vencimiento"] = estados.apply(lambda x: x["estado"])

    df["Estado_UI"] = estados.apply(lambda x: x["estado_ui"])

    df["Color"] = estados.apply(lambda x: x["color"])

    df["Prioridad"] = estados.apply(lambda x: x["prioridad"])

    df = df.sort_values(["Prioridad", "Dias_Restantes"]).reset_index(drop=True)

    return df


def actualizar_suscripciones(csv_path: str | Path = DEFAULT_CSV) -> pd.DataFrame:
    """Actualiza el CSV de suscripciones a partir de Notion."""
    ruta = _resolver_ruta(csv_path)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    df = obtener_suscripciones_notion()

    historico = ruta.with_name("suscripciones_historico.csv")
    df.to_csv(historico, index=False)
    df.to_csv(ruta, index=False)

    return df


# ==========================================================
# CARGA
# ==========================================================


def cargar_suscripciones(
    csv_path: str | Path = DEFAULT_CSV,
) -> pd.DataFrame:
    """
    Carga el archivo CSV de suscripciones y devuelve un
    DataFrame completamente preparado para el dashboard.
    """

    ruta = _resolver_ruta(csv_path)

    if not ruta.exists():
        return actualizar_suscripciones(ruta)

    try:
        df = pd.read_csv(ruta)
    except Exception:
        return actualizar_suscripciones(ruta)

    columnas_requeridas = {"Nombre", "Proveedor", "Estado", "Costo_Mensual"}
    if df.empty or not columnas_requeridas.issubset(df.columns):
        return actualizar_suscripciones(ruta)

    if df["Nombre"].fillna("").astype(str).str.strip().eq("").all():
        return actualizar_suscripciones(ruta)

    df = extraer_suscripciones(df)
    df = transformar_suscripciones(df)

    # ==========================================================
    # Estado de vencimiento
    # ==========================================================

    estados = df["Fecha_Vencimiento"].apply(obtener_estado)

    df["Dias_Restantes"] = estados.apply(lambda x: x["dias_restantes"])

    df["Estado_Vencimiento"] = estados.apply(lambda x: x["estado"])

    df["Estado_UI"] = estados.apply(lambda x: x["estado_ui"])

    df["Color"] = estados.apply(lambda x: x["color"])

    df["Prioridad"] = estados.apply(lambda x: x["prioridad"])

    df = df.sort_values(
        by=["Prioridad", "Dias_Restantes"],
        ascending=[True, True],
    ).reset_index(drop=True)

    return df


# ==========================================================
# FILTROS
# ==========================================================


def aplicar_filtros(
    df: pd.DataFrame,
    proveedor: str | None = None,
    estado: str | None = None,
    grupo: str | None = None,
    estado_vencimiento: str | None = None,
    mes: int | None = None,
) -> pd.DataFrame:
    """
    Aplica los filtros seleccionados por el usuario.
    """

    df_filtrado = df.copy()

    if proveedor and proveedor != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Proveedor"] == proveedor]

    if estado and estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estado"] == estado]

    if grupo and grupo != "Todos" and "Grupo" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["Grupo"] == grupo]

    if estado_vencimiento and estado_vencimiento != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["Estado_Vencimiento"] == estado_vencimiento
        ]

    if mes not in (None, "Todos"):
        df_filtrado = df_filtrado[df_filtrado["Mes_Vencimiento"] == mes]

    return df_filtrado.reset_index(drop=True)


# ==========================================================
# DASHBOARD
# ==========================================================


def calcular_dashboard(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """
    Calcula toda la información necesaria para el dashboard.
    """

    return {
        "df": df,
        "kpis": calcular_kpis(df),
        "alertas": obtener_alertas(df),
        "proveedores": costos_por_proveedor(df),
        "vencimientos": vencimientos_por_mes(df),
        "proximos": proximos_vencimientos(df),
    }


# ==========================================================
# SERVICIO COMPLETO
# ==========================================================


def obtener_dashboard(
    csv_path: str | Path = DEFAULT_CSV,
    proveedor: str | None = None,
    estado: str | None = None,
    estado_vencimiento: str | None = None,
    mes: int | None = None,
) -> dict[str, Any]:
    """
    Servicio de alto nivel.

    Carga las suscripciones, aplica los filtros y devuelve
    toda la información necesaria para la interfaz.
    """

    df = cargar_suscripciones(csv_path)

    df = aplicar_filtros(
        df=df,
        proveedor=proveedor,
        estado=estado,
        grupo=None,
        estado_vencimiento=estado_vencimiento,
        mes=mes,
    )

    return calcular_dashboard(df)
