import pandas as pd


# =========================================================
# SCORE FINANCIERO
# =========================================================

def calcular_score_financiero(
    ingresos: float,
    gastos: float,
    balance: float,
) -> int:
    score = 100

    if balance < 0:
        score -= 40

    if ingresos > 0 and abs(gastos) > ingresos:
        score -= 30

    ratio_gasto = abs(gastos) / ingresos if ingresos > 0 else 1

    if ratio_gasto > 0.8:
        score -= 20

    return max(score, 0)


# =========================================================
# PENDIENTES DE CLASIFICAR
# =========================================================

def contar_movimientos_pendientes(
    df: pd.DataFrame,
) -> int:

    if df.empty:
        return 0

    pendientes = df[
        (df["tipo"].fillna("") == "Gasto")
        & (
            (df["monto"].fillna(0) == 0)
            | (
                df["categoria"]
                .fillna("Sin categoría")
                .eq("Sin categoría")
            )
        )
    ]

    return len(pendientes)