from __future__ import annotations

import pandas as pd

from domain.suscripciones.constants import COLUMNAS_MODELO

# ==========================================================
# HELPERS
# ==========================================================


def _crear_columnas_faltantes(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Garantiza que existan todas las columnas oficiales.
    """

    df = df.copy()

    for columna in COLUMNAS_MODELO:
        if columna not in df.columns:
            df[columna] = None

    return df


def _convertir_tipos(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convierte los tipos de datos.
    """

    df = df.copy()

    # Texto
    columnas_texto = [
        "Nombre",
        "Proveedor",
        "Estado",
        "Descripcion",
        "Observaciones",
    ]

    for columna in columnas_texto:
        df[columna] = df[columna].fillna("").astype(str).str.strip()

    # Número
    df["Costo_Mensual"] = pd.to_numeric(
        df["Costo_Mensual"],
        errors="coerce",
    ).fillna(0)

    # Fecha
    df["Fecha_Vencimiento"] = pd.to_datetime(
        df["Fecha_Vencimiento"],
        errors="coerce",
    )

    return df


def _ordenar_columnas(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Devuelve únicamente las columnas oficiales
    en el orden establecido.
    """

    return df[COLUMNAS_MODELO].copy()


# ==========================================================
# EXTRACTOR
# ==========================================================


def extraer_suscripciones(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normaliza el DataFrame de suscripciones.
    """

    if df.empty:
        return pd.DataFrame(columns=COLUMNAS_MODELO)

    df = _crear_columnas_faltantes(df)

    df = _convertir_tipos(df)

    df = _ordenar_columnas(df)

    return df.reset_index(drop=True)
