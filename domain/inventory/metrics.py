import pandas as pd


# =========================================================
# KPIs
# =========================================================
def calcular_kpis(df: pd.DataFrame) -> dict:

    total_equipos = len(df)

    equipos_asignados = df["Asignado"].fillna("").astype(str).str.strip().ne("").sum()

    sin_asignar = total_equipos - equipos_asignados

    total_marcas = df["Marca"].fillna("").astype(str).str.strip().nunique()

    sin_serie = df["Serie"].fillna("").astype(str).str.strip().eq("").sum()

    return {
        "total_equipos": int(total_equipos),
        "equipos_asignados": int(equipos_asignados),
        "sin_asignar": int(sin_asignar),
        "total_marcas": int(total_marcas),
        "sin_serie": int(sin_serie),
    }


# =========================================================
# ALERTAS
# =========================================================
def obtener_alertas(df: pd.DataFrame) -> dict:

    sin_serie = df[df["Serie"].fillna("").astype(str).str.strip().eq("")]

    sin_factura = df[df["Factura"].fillna("").astype(str).str.strip().eq("")]

    sin_fecha_compra = df[
        pd.to_datetime(
            df["Fecha Compra"],
            errors="coerce",
        ).isna()
    ]

    sin_asignar = df[df["Asignado"].fillna("").astype(str).str.strip().eq("")]

    return {
        "sin_serie": sin_serie,
        "sin_factura": sin_factura,
        "sin_fecha_compra": sin_fecha_compra,
        "sin_asignar": sin_asignar,
    }


# =========================================================
# GRAFICOS
# =========================================================
def equipos_por_tipo(df: pd.DataFrame) -> pd.Series:

    return df["Tipo"].fillna("Sin Tipo").value_counts().sort_values(ascending=False)


def equipos_por_marca(df: pd.DataFrame) -> pd.Series:

    return df["Marca"].fillna("Sin Marca").value_counts().sort_values(ascending=False)


def antiguedad_equipos(df: pd.DataFrame) -> pd.Series:

    fechas = pd.to_datetime(
        df["Fecha Compra"],
        errors="coerce",
    )

    hoy = pd.Timestamp.today()

    antiguedad_anios = (hoy - fechas).dt.days / 365.25

    categorias = pd.cut(
        antiguedad_anios,
        bins=[-1, 1, 3, 5, 100],
        labels=[
            "0-1 años",
            "1-3 años",
            "3-5 años",
            "+5 años",
        ],
    )

    return categorias.value_counts().reindex(
        [
            "0-1 años",
            "1-3 años",
            "3-5 años",
            "+5 años",
        ],
        fill_value=0,
    )
