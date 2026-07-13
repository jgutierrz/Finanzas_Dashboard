from __future__ import annotations

import pandas as pd

# ==========================================================
# KPIs
# ==========================================================


def calcular_kpis(
    df: pd.DataFrame,
) -> dict:
    """
    Calcula los indicadores principales del dashboard.
    """

    if df.empty:
        return {
            "total": 0,
            "costo_mensual": 0.0,
            "costo_anual": 0.0,
            "vencidas": 0,
            "vence_pronto": 0,
            "proximas": 0,
            "vigentes": 0,
        }

    return {
        "total": len(df),
        "costo_mensual": float(df["Costo_Mensual"].sum()),
        "costo_anual": float(df["Costo_Anual"].sum()),
        "vencidas": int((df["Estado_Vencimiento"] == "Vencida").sum()),
        "vence_pronto": int((df["Estado_Vencimiento"] == "Vence pronto").sum()),
        "proximas": int((df["Estado_Vencimiento"] == "Próxima").sum()),
        "vigentes": int((df["Estado_Vencimiento"] == "Vigente").sum()),
    }


# ==========================================================
# ALERTAS
# ==========================================================


def obtener_alertas(
    df: pd.DataFrame,
) -> dict:
    """
    Devuelve las suscripciones clasificadas por prioridad.
    """

    return {
        "vencidas": (
            df[df["Estado_Vencimiento"] == "Vencida"].sort_values("Fecha_Vencimiento")
        ),
        "vence_pronto": (
            df[df["Estado_Vencimiento"] == "Vence pronto"].sort_values(
                "Fecha_Vencimiento"
            )
        ),
        "proximas": (
            df[df["Estado_Vencimiento"] == "Próxima"].sort_values("Fecha_Vencimiento")
        ),
    }


# ==========================================================
# RESUMEN POR PROVEEDOR
# ==========================================================


def costos_por_proveedor(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    resumen = (
        df.groupby(
            "Proveedor",
            as_index=False,
        )
        .agg(
            Cantidad=("Nombre", "count"),
            Costo_Mensual=("Costo_Mensual", "sum"),
            Costo_Anual=("Costo_Anual", "sum"),
        )
        .sort_values(
            "Costo_Mensual",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return resumen


# ==========================================================
# VENCIMIENTOS POR MES
# ==========================================================


def vencimientos_por_mes(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    return df.groupby(
        "Mes_Vencimiento",
        as_index=False,
    ).agg(
        Cantidad=("Nombre", "count"),
        Costo_Mensual=("Costo_Mensual", "sum"),
    )


# ==========================================================
# PRÓXIMOS VENCIMIENTOS
# ==========================================================


def proximos_vencimientos(
    df: pd.DataFrame,
    cantidad: int = 10,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    return df.sort_values("Fecha_Vencimiento").head(cantidad)


# ==========================================================
# RESUMEN GENERAL
# ==========================================================


def resumen_general(
    df: pd.DataFrame,
) -> dict:

    return {
        "kpis": calcular_kpis(df),
        "alertas": obtener_alertas(df),
        "proveedores": costos_por_proveedor(df),
        "vencimientos": vencimientos_por_mes(df),
        "proximos": proximos_vencimientos(df),
    }
