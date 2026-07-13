from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from domain.finanzas.kpis import calcular_score_financiero
from exporters.excel_styles import (
    aplicar_formato_condicional_resumen_mensual,
    crear_estilos,
    formatear_hoja,
)

# =========================================================
# CONFIGURACIÓN
# =========================================================

COLUMNAS_OCULTAR = {
    "categoria_id",
}


# =========================================================
# HELPERS
# =========================================================


def _resolver_output_path(
    output_path: str | Path | None,
) -> Path:
    """
    Genera la ruta de salida del Excel.
    """

    Path("dist").mkdir(
        exist_ok=True,
        parents=True,
    )

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return Path("dist") / f"finanzas_{timestamp}.xlsx"

    return Path(output_path)


def _crear_resumen(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """
    Genera KPIs generales.
    """

    ingresos = df.loc[
        df["monto"] > 0,
        "monto",
    ].sum()

    gastos = df.loc[
        df["monto"] < 0,
        "monto",
    ].sum()

    balance = ingresos + gastos

    total_movimientos = len(df)

    categoria_top = "N/A"

    gastos_df = df[df["monto"] < 0]

    if not gastos_df.empty:
        categoria_top = gastos_df.groupby("categoria")["monto"].sum().idxmin()

    promedio_mensual = df.groupby("mes")["monto"].sum().mean()

    score = calcular_score_financiero(
        ingresos=ingresos,
        gastos=gastos,
        balance=balance,
    )

    resumen = pd.DataFrame(
        {
            "Indicador": [
                "Total de ingresos",
                "Total de gastos",
                "Balance neto",
                "Número de movimientos",
                "Categoría de mayor gasto",
                "Promedio mensual",
                "Score financiero",
            ],
            "Valor": [
                ingresos,
                gastos,
                balance,
                total_movimientos,
                categoria_top,
                promedio_mensual,
                score,
            ],
        }
    )

    kpis = {
        "ingresos": ingresos,
        "gastos": gastos,
        "balance": balance,
        "promedio_mensual": promedio_mensual,
        "score": score,
    }

    return resumen, kpis


def _crear_dashboard(
    kpis: dict,
) -> pd.DataFrame:

    ingresos = kpis["ingresos"]
    gastos = kpis["gastos"]
    balance = kpis["balance"]

    return pd.DataFrame(
        {
            "Indicador": [
                "Total Ingresos",
                "Total Gastos",
                "Balance Neto",
                "Promedio Mensual",
                "Score Financiero",
                "% Gastos / Ingresos",
                "% Ahorro",
            ],
            "Valor": [
                ingresos,
                gastos,
                balance,
                kpis["promedio_mensual"],
                kpis["score"],
                abs(gastos) / ingresos if ingresos else 0,
                balance / ingresos if ingresos else 0,
            ],
        }
    )


def _crear_resumen_mensual(
    df: pd.DataFrame,
) -> pd.DataFrame:

    ingresos = df[df["monto"] > 0].groupby("mes")["monto"].sum()

    gastos = df[df["monto"] < 0].groupby("mes")["monto"].sum()

    resumen = pd.DataFrame(
        {
            "Ingresos": ingresos,
            "Gastos": gastos,
        }
    ).fillna(0)

    resumen["Balance"] = resumen["Ingresos"] + resumen["Gastos"]

    resumen["Pct_Gastos"] = resumen["Gastos"].abs().div(resumen["Ingresos"]).fillna(0)

    resumen["Pct_Ahorro"] = resumen["Balance"].div(resumen["Ingresos"]).fillna(0)

    resumen["Variacion_Balance"] = resumen["Balance"].pct_change().fillna(0)

    resumen = resumen.sort_index()

    return resumen


def _crear_pivot_categorias(
    df: pd.DataFrame,
) -> pd.DataFrame:

    gastos_df = df[df["monto"] < 0].copy()

    if gastos_df.empty:
        return pd.DataFrame()

    pivot = pd.pivot_table(
        gastos_df,
        index="mes",
        columns="categoria",
        values="monto",
        aggfunc="sum",
        fill_value=0,
    )

    return pivot.sort_index()


def _crear_ranking_categorias(
    df: pd.DataFrame,
) -> pd.DataFrame:

    ranking = df[df["monto"] < 0].groupby("categoria", as_index=False)["monto"].sum()

    ranking["Total_Gastado"] = ranking["monto"].abs().round(2)

    total_gastos = ranking["Total_Gastado"].sum()

    ranking["Porcentaje"] = (ranking["Total_Gastado"] / total_gastos * 100).round(4)

    ranking = (
        ranking[
            [
                "categoria",
                "Total_Gastado",
                "Porcentaje",
            ]
        ]
        .sort_values(
            by="Total_Gastado",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    ranking.insert(
        0,
        "Ranking",
        range(1, len(ranking) + 1),
    )

    ranking.rename(
        columns={
            "categoria": "Categoria",
        },
        inplace=True,
    )

    return ranking


# =========================================================
# EXPORTACIÓN
# =========================================================


def exportar_finanzas_excel(
    df: pd.DataFrame,
    output_path: str | Path | None = None,
) -> str:

    output_path = _resolver_output_path(output_path)

    df = df.copy()

    df = df.drop(
        columns=[c for c in COLUMNAS_OCULTAR if c in df.columns],
        errors="ignore",
    )

    resumen, kpis = _crear_resumen(df)

    dashboard = _crear_dashboard(kpis)

    resumen_mensual = _crear_resumen_mensual(df)

    pivot_categorias = _crear_pivot_categorias(df)

    ranking_categorias = _crear_ranking_categorias(df)

    estilos = crear_estilos()

    with pd.ExcelWriter(
        output_path,
        engine="openpyxl",
    ) as writer:
        # =================================================
        # MOVIMIENTOS
        # =================================================

        df.to_excel(
            writer,
            sheet_name="Movimientos",
            index=False,
        )

        # =================================================
        # RESUMEN
        # =================================================

        resumen.to_excel(
            writer,
            sheet_name="Resumen",
            index=False,
        )

        # =================================================
        # DASHBOARD
        # =================================================

        dashboard.to_excel(
            writer,
            sheet_name="Dashboard",
            index=False,
        )

        # =================================================
        # RESUMEN MENSUAL
        # =================================================

        resumen_mensual.to_excel(
            writer,
            sheet_name="Resumen_Mensual",
        )

        # =================================================
        # PIVOT
        # =================================================

        if not pivot_categorias.empty:
            pivot_categorias.to_excel(
                writer,
                sheet_name="Pivot_Categorias",
            )

        # =================================================
        # RANKING CATEGORIAS
        # =================================================

        if not ranking_categorias.empty:
            ranking_categorias.to_excel(
                writer,
                sheet_name="Ranking_Categorias",
                index=False,
            )

        # =================================================
        # FORMATO GENERAL
        # =================================================

        for sheet_name in writer.book.sheetnames:
            ws = writer.book[sheet_name]

            formatear_hoja(
                ws,
                estilos,
            )

        # =================================================
        # FORMATO CONDICIONAL
        # =================================================

        if "Resumen_Mensual" in writer.book.sheetnames:
            aplicar_formato_condicional_resumen_mensual(writer.book["Resumen_Mensual"])

        # =================================================
        # AJUSTES RESUMEN
        # =================================================

        ws_res = writer.book["Resumen"]

        ws_res["B5"].number_format = "0"
        ws_res["B8"].number_format = "0"

        # =================================================
        # AJUSTES DASHBOARD
        # =================================================

        ws_dash = writer.book["Dashboard"]

        ws_dash["B6"].number_format = "0"
        ws_dash["B7"].number_format = "0.00%"
        ws_dash["B8"].number_format = "0.00%"

    return str(output_path)
