from pathlib import Path
from datetime import datetime
import pandas as pd

from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def formatear_hoja(
    ws,
    fill_header,
    font_header,
    align_center,
    align_right,
    border_thin,
    formato_moneda='[$S/] #,##0.00'
):
    """
    Aplica formato estándar a una hoja Excel:
    - Fuente Calibri 10 en todas las celdas
    - Zoom 80%
    - Fila superior congelada
    - AutoFiltro
    - Encabezado azul oscuro
    - Bordes finos
    - Ajuste automático de columnas
    - Formato monetario en columnas numéricas (excepto primera columna)
    """

    # -----------------------------------------------------
    # Configuración general
    # -----------------------------------------------------
    ws.sheet_view.zoomScale = 80
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    # -----------------------------------------------------
    # Fuente base y bordes
    # -----------------------------------------------------
    for row in ws.iter_rows():
        for cell in row:
            cell.font = Font(
                name="Calibri",
                size=10,
                bold=cell.font.bold,
                italic=cell.font.italic
            )
            cell.border = border_thin

    # -----------------------------------------------------
    # Encabezado
    # -----------------------------------------------------
    for cell in ws[1]:
        cell.fill = fill_header
        cell.font = font_header
        cell.alignment = align_center
        cell.border = border_thin

    # -----------------------------------------------------
    # Ajuste de columnas y formato monetario
    # -----------------------------------------------------
    for i, col in enumerate(ws.columns, 1):
        max_length = 0
        column = get_column_letter(i)

        for cell in col:
            # Aplicar formato monetario a columnas numéricas
            # (excepto la primera columna)
            if (
                cell.row > 1
                and i > 1
                and isinstance(cell.value, (int, float))
            ):
                cell.number_format = formato_moneda
                cell.alignment = align_right

            # Calcular longitud máxima del contenido
            try:
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))
            except Exception:
                pass

        # Ancho mínimo 12, máximo 50
        ancho = max(12, min(max_length + 2, 50))
        ws.column_dimensions[column].width = ancho
        
def calcular_score_financiero(ingresos, gastos, balance):
    score = 100

    if balance < 0:
        score -= 40

    if abs(gastos) > ingresos and ingresos > 0:
        score -= 30

    ratio_gasto = abs(gastos) / ingresos if ingresos > 0 else 1

    if ratio_gasto > 0.8:
        score -= 20

    return max(score, 0)


def exportar_finanzas_excel(df, output_path=None):
    """
    Exporta un DataFrame financiero a un archivo Excel con formato profesional.

    Características:
    - Hoja 'Movimientos' con todos los registros.
    - Hoja 'Resumen' con KPIs financieros.
    - Encabezados con formato ejecutivo.
    - AutoFiltro y fila superior congelada.
    - Formato contable para columnas monetarias.
    - Ajuste automático del ancho de columnas.

    Parámetros:
        df (pd.DataFrame): DataFrame a exportar.
        output_path (str | Path | None): Ruta del archivo de salida.

    Retorna:
        str: Ruta del archivo generado.
    """

    Path("dist").mkdir(exist_ok=True)

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path("dist") / f"finanzas_{timestamp}.xlsx"
    else:
        output_path = Path(output_path)

    df = df.copy()

    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    # ---------------------------------------------------------
    # KPIs
    # ---------------------------------------------------------
    if "monto" in df.columns:
        ingresos = df.loc[df["monto"] > 0, "monto"].sum()
        gastos = df.loc[df["monto"] < 0, "monto"].sum()
    else:
        ingresos = 0
        gastos = 0

    balance = ingresos + gastos
    total_movimientos = len(df)

    # Categoría de mayor gasto
    categoria_top = "N/A"
    if "categoria" in df.columns and "monto" in df.columns:
        gastos_df = df[df["monto"] < 0]
        if not gastos_df.empty:
            try:
                categoria_top = (
                    gastos_df.groupby("categoria")["monto"]
                    .sum()
                    .idxmin()
                )
            except Exception:
                categoria_top = "N/A"

    # Promedio mensual del balance
    promedio_mensual = 0
    if "mes" in df.columns and "monto" in df.columns:
        try:
            balances_mensuales = df.groupby("mes")["monto"].sum()
            if len(balances_mensuales) > 0:
                promedio_mensual = balances_mensuales.mean()
        except Exception:
            promedio_mensual = 0

    # Score financiero
    score = calcular_score_financiero(ingresos, gastos, balance)

    # ---------------------------------------------------------
    # Escritura del archivo
    # ---------------------------------------------------------
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # Hoja de movimientos
        df.to_excel(writer, sheet_name="Movimientos", index=False)

        # Hoja resumen
        resumen = pd.DataFrame({
            "Indicador": [
                "Total de ingresos",
                "Total de gastos",
                "Balance neto",
                "Número de movimientos",
                "Categoría de mayor gasto",
                "Promedio mensual",
                "Score financiero"
            ],
            "Valor": [
                ingresos,
                gastos,
                balance,
                total_movimientos,
                categoria_top,
                promedio_mensual,
                score
            ]
        })

        resumen.to_excel(writer, sheet_name="Resumen", index=False)

        # -----------------------------------------------------
        # Estilos
        # -----------------------------------------------------
        fill_header = PatternFill("solid", fgColor="1F4E78")
        font_header = Font(name="Calibri", size=10, color="FFFFFF", bold=True)
        align_center = Alignment(horizontal="center", vertical="center")
        align_right = Alignment(horizontal="right")
        border_thin = Border(
            left=Side(style="thin", color="D9D9D9"),
            right=Side(style="thin", color="D9D9D9"),
            top=Side(style="thin", color="D9D9D9"),
            bottom=Side(style="thin", color="D9D9D9"),
        )

        formato_moneda = '[$S/] #,##0.00'
        formato_fecha = 'dd/mm/yyyy'

        # -----------------------------------------------------
        # Formato general de hojas
        # -----------------------------------------------------
        for sheet_name in ["Movimientos", "Resumen"]:
            ws = writer.book[sheet_name]

            formatear_hoja(
                ws,
                fill_header,
                font_header,
                align_center,
                align_right,
                border_thin,
                formato_moneda
            )

        # -----------------------------------------------------
        # Formato hoja Movimientos
        # -----------------------------------------------------
        ws_mov = writer.book["Movimientos"]

        col_map = {cell.value: cell.column for cell in ws_mov[1]}

        # Fecha
        if "fecha" in col_map:
            col_fecha = col_map["fecha"]
            for row in range(2, ws_mov.max_row + 1):
                ws_mov.cell(row=row, column=col_fecha).number_format = formato_fecha

        # Moneda
        if "monto" in col_map:
            col_monto = col_map["monto"]
            for row in range(2, ws_mov.max_row + 1):
                cell = ws_mov.cell(row=row, column=col_monto)
                cell.number_format = formato_moneda
                cell.alignment = align_right

        # -----------------------------------------------------
        # Formato hoja Resumen
        # -----------------------------------------------------
        ws_res = writer.book["Resumen"]

        # Filas monetarias: ingresos, gastos, balance, promedio mensual
        for row in [2, 3, 4, 7]:
            cell = ws_res.cell(row=row, column=2)
            cell.number_format = formato_moneda
            cell.alignment = align_right

        # Número de movimientos y score
        ws_res.cell(row=5, column=2).alignment = align_center
        ws_res.cell(row=8, column=2).alignment = align_center

        # -----------------------------------------------------
        # Hojas analíticas (tipo tabla dinámica con pandas)
        # -----------------------------------------------------
        if "mes" in df.columns and "categoria" in df.columns and "monto" in df.columns:
            try:
                # Solo gastos para análisis de categorías
                gastos_df = df[df["monto"] < 0].copy()

                if not gastos_df.empty:
                    # Pivot mensual por categoría
                    pivot_categorias = pd.pivot_table(
                        gastos_df,
                        index="mes",
                        columns="categoria",
                        values="monto",
                        aggfunc="sum",
                        fill_value=0
                    )
                    pivot_categorias.to_excel(writer, sheet_name="Pivot_Categorias")

                    # Resumen mensual (ingresos, gastos y balance)
                    resumen_mensual = pd.DataFrame({
                        "Ingresos": df[df["monto"] > 0].groupby("mes")["monto"].sum(),
                        "Gastos": df[df["monto"] < 0].groupby("mes")["monto"].sum(),
                    }).fillna(0)
                    resumen_mensual["Balance"] = (
                        resumen_mensual["Ingresos"] + resumen_mensual["Gastos"]
                    )
                    resumen_mensual.to_excel(writer, sheet_name="Resumen_Mensual")

                    # Top 50 gastos individuales
                    top_gastos = (
                        gastos_df.sort_values("monto")
                        .head(50)
                    )
                    top_gastos.to_excel(writer, sheet_name="Top_Gastos", index=False)

                    # Formatear nuevas hojas
                    for sheet_name in [
                        "Pivot_Categorias",
                        "Resumen_Mensual",
                        "Top_Gastos",
                    ]:
                        ws = writer.book[sheet_name]
                        formatear_hoja(
                            ws,
                            fill_header,
                            font_header,
                            align_center,
                            align_right,
                            border_thin,
                            formato_moneda
                        )

            except Exception:
                # Si alguna hoja analítica falla, no se interrumpe la exportación principal
                pass


    return str(output_path)
