import pandas as pd


def aplicar_filtros(
    df: pd.DataFrame,
    tipo: str | None = None,
    marca: str | None = None,
) -> pd.DataFrame:

    resultado = df.copy()

    if tipo and tipo != "Todos":
        resultado = resultado[resultado["Tipo"] == tipo]

    if marca and marca != "Todas":
        resultado = resultado[resultado["Marca"] == marca]

    return resultado
