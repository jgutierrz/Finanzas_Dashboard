from pathlib import Path
from datetime import datetime

import pandas as pd

from domain.finanzas.kpis import calcular_score_financiero

from exporters.excel_styles import (
    crear_estilos,
    formatear_hoja,
    aplicar_formato_condicional_resumen_mensual,
)


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

COLUMNAS_OCULTAR = ["categoria_id"]

# =========================================================
# EXPORTACIÓN PRINCIPAL
# =========================================================

def exportar_finanzas_excel(
    df: pd.DataFrame,
    output_path: str | Path | None = None,
) -> str:

    Path("dist").mkdir(exist_ok=True)

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path("dist") / f"finanzas_{timestamp}.xlsx"
    else:
        output_path = Path(output_path)

    # -----------------------------------------------------
    # Copia y limpieza
    # -----------------------------------------------------

    df = df.copy()

    df = df.drop(
        columns=[c for c in COLUMNAS_OCULTAR if c in df.columns],
        errors="ignore",
    )

    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(
            df["fecha"],
            errors="coerce",
        )

        # -----------------------------------------------------
        # KPIs
        # -----------------------------------------------------
        ingresos = (
            df.loc[df["monto"] > 0, "monto"].sum()
            if "monto" in df.columns
            else 0
        )

        gastos = (
            df.loc[df["monto"] < 0, "monto"].sum()
            if "monto" in df.columns
            else 0
        )

        balance = ingresos + gastos

        total_movimientos = len(df)

        categoria_top = "N/A"

        if {"categoria", "monto"}.issubset(df.columns):
            gastos_df = df[df["monto"] < 0]

            if not gastos_df.empty:
                try:
                    categoria_top = (
                        gastos_df.groupby("categoria")["monto"]
                        .sum()
                        .idxmin()
                    )
                except Exception:
                    pass

        promedio_mensual = 0

        if {"mes", "monto"}.issubset(df.columns):
            try:
                promedio_mensual = (
                    df.groupby("mes")["monto"]
                    .sum()
                    .mean()
                )
            except Exception:
                pass

        score = calcular_score_financiero(
            ingresos=ingresos,
            gastos=gastos,
            balance=balance,
        )
        # -----------------------------------------------------
        # Resumen
        # -----------------------------------------------------
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
        # HOJAS ANALÍTICAS
        # =================================================

        if {"mes", "categoria", "monto"}.issubset(df.columns):

            gastos_df = df[df["monto"] < 0].copy()

            if not gastos_df.empty:

                # -----------------------------------------
                # Pivot_Categorias
                # -----------------------------------------

                pivot_categorias = pd.pivot_table(
                    gastos_df,
                    index="mes",
                    columns="categoria",
                    values="monto",
                    aggfunc="sum",
                    fill_value=0,
                )

                pivot_categorias.to_excel(
                    writer,
                    sheet_name="Pivot_Categorias",
                )

                # -----------------------------------------
                # Resumen_Mensual
                # -----------------------------------------

                ingresos_m = (
                    df[df["monto"] > 0]
                    .groupby("mes")["monto"]
                    .sum()
                )

                gastos_m = (
                    df[df["monto"] < 0]
                    .groupby("mes")["monto"]
                    .sum()
                )

                resumen_mensual = pd.DataFrame(
                    {
                        "Ingresos": ingresos_m,
                        "Gastos": gastos_m,
                    }
                ).fillna(0)

                resumen_mensual["Balance"] = (
                    resumen_mensual["Ingresos"]
                    + resumen_mensual["Gastos"]
                )

                resumen_mensual["Pct_Gastos"] = (
                    resumen_mensual.apply(
                        lambda r:
                        abs(r["Gastos"]) / r["Ingresos"]
                        if r["Ingresos"] != 0
                        else 0,
                        axis=1,
                    )
                )

                resumen_mensual["Pct_Ahorro"] = (
                    resumen_mensual.apply(
                        lambda r:
                        r["Balance"] / r["Ingresos"]
                        if r["Ingresos"] != 0
                        else 0,
                        axis=1,
                    )
                )

                resumen_mensual["Variacion_Balance"] = (
                    resumen_mensual["Balance"]
                    .pct_change()
                    .fillna(0)
                )

                resumen_mensual.to_excel(
                    writer,
                    sheet_name="Resumen_Mensual",
                )

                # -----------------------------------------
                # Top_Gastos
                # -----------------------------------------

                top_gastos = (
                    gastos_df
                    .sort_values("monto")
                    .head(50)
                )

                top_gastos.to_excel(
                    writer,
                    sheet_name="Top_Gastos",
                    index=False,
                )

        # =================================================
        # DASHBOARD EJECUTIVO
        # =================================================

        dashboard = pd.DataFrame(
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
                    promedio_mensual,
                    score,
                    abs(gastos) / ingresos
                    if ingresos != 0
                    else 0,
                    balance / ingresos
                    if ingresos != 0
                    else 0,
                ],
            }
        )

        dashboard.to_excel(
            writer,
            sheet_name="Dashboard",
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
        # AJUSTES RESUMEN
        # =================================================

        ws_res = writer.book["Resumen"]

        # Número de movimientos
        ws_res.cell(
            row=5,
            column=2,
        ).number_format = "0"

        ws_res.cell(
            row=5,
            column=2,
        ).alignment = estilos["align_center"]

        # Score
        ws_res.cell(
            row=8,
            column=2,
        ).number_format = "0"

        ws_res.cell(
            row=8,
            column=2,
        ).alignment = estilos["align_center"]

        # =================================================
        # FORMATO CONDICIONAL
        # =================================================

        if "Resumen_Mensual" in writer.book.sheetnames:

            ws_rm = writer.book["Resumen_Mensual"]

            aplicar_formato_condicional_resumen_mensual(
                ws_rm
            )

        # =================================================
        # DASHBOARD
        # =================================================

        if "Dashboard" in writer.book.sheetnames:

            ws_dash = writer.book["Dashboard"]

            # % Gastos / Ingresos
            ws_dash.cell(
                row=7,
                column=2,
            ).number_format = "0.00%"

            # % Ahorro
            ws_dash.cell(
                row=8,
                column=2,
            ).number_format = "0.00%"

            # Score
            ws_dash.cell(
                row=6,
                column=2,
            ).number_format = "0"

    return str(output_path)