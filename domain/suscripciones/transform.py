from __future__ import annotations

import pandas as pd

from domain.suscripciones.constants import (
    DIAS_ALERTA,
    DIAS_PROXIMO,
    MESES,
)

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

DIAS_ALERTA = 7
DIAS_PROXIMO = 30

MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

# ==========================================================
# HELPERS
# ==========================================================


def _calcular_dias_vencimiento(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calcula los días restantes para el vencimiento.
    """

    df = df.copy()

    hoy = pd.Timestamp.now().normalize()

    df["Dias_Vencimiento"] = (df["Fecha_Vencimiento"] - hoy).dt.days

    return df


def _calcular_estado_vencimiento(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clasifica cada suscripción según su vencimiento.
    """

    df = df.copy()

    condiciones = [
        df["Dias_Vencimiento"] < 0,
        df["Dias_Vencimiento"].between(
            0,
            DIAS_ALERTA,
        ),
        df["Dias_Vencimiento"].between(
            DIAS_ALERTA + 1,
            DIAS_PROXIMO,
        ),
    ]

    opciones = [
        "Vencida",
        "Vence pronto",
        "Próxima",
    ]

    df["Estado_Vencimiento"] = "Vigente"

    for condicion, valor in zip(condiciones, opciones):
        df.loc[condicion, "Estado_Vencimiento"] = valor

    return df


def _calcular_costo_anual(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calcula el costo anual estimado.
    """

    df = df.copy()

    df["Costo_Anual"] = (df["Costo_Mensual"] * 12).round(2)

    return df


def _extraer_componentes_fecha(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Genera columnas auxiliares para agrupaciones.
    """

    df = df.copy()

    df["Año_Vencimiento"] = df["Fecha_Vencimiento"].dt.year

    df["Mes_Vencimiento"] = df["Fecha_Vencimiento"].dt.month

    df["Mes_Nombre"] = df["Mes_Vencimiento"].map(MESES)

    return df


def _ordenar(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Ordena por fecha de vencimiento.
    """

    return df.sort_values(
        by="Fecha_Vencimiento",
        ascending=True,
        na_position="last",
    ).reset_index(drop=True)


# ==========================================================
# TRANSFORMACIÓN
# ==========================================================


def transformar_suscripciones(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Enriquece el DataFrame con columnas calculadas.
    """

    if df.empty:
        return df.copy()

    df = _calcular_dias_vencimiento(df)

    df = _calcular_estado_vencimiento(df)

    df = _calcular_costo_anual(df)

    df = _extraer_componentes_fecha(df)

    df = _ordenar(df)

    return df
