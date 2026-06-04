import pandas as pd

# -------------------------ELIMINAR
# 📂 CATEGORIZACIÓN
# -------------------------
#def categorizar(descripcion):
#    try:
#        d = str(descripcion).lower()
###    except:
#        return "Otros"

#    if "pluz" in d or "luz" in d:
#        return "Servicios"
#    elif "movistar" in d:
#        return "Internet"
#    elif "retiro" in d:
#        return "Efectivo"
#    elif "sueldo" in d:
#        return "Ingreso Fijo"
#    elif "reembolso" in d:
#        return "Ingreso Variable"
#    else:
#        return "Otros"


# -------------------------
# ⚠️ ALERTAS
# -------------------------
def detectar_alertas(df):
    alertas = []

    if df.empty or "monto" not in df.columns:
        return alertas

    gastos = df[df["monto"] < 0]

    if not gastos.empty:
        promedio = gastos["monto"].mean()

        # Nota técnica:
        # Como los gastos son negativos, un gasto "más alto"
        # es un valor más negativo que el promedio * 1.5.
        gastos_altos = gastos[gastos["monto"] < promedio * 1.5]

        if not gastos_altos.empty:
            alertas.append(f"Tienes {len(gastos_altos)} gastos altos")

    return alertas



# -------------------------
# 🧠 INSIGHTS
# -------------------------
def generar_insights(df):
    insights = []

    balance = df["monto"].sum()

    if balance < 0:
        insights.append("Estás gastando más de lo que ganas")
    else:
        insights.append("Tu flujo es positivo")

    gastos = df[df["monto"] < 0]

    if not gastos.empty:
        categoria_top = gastos.groupby("categoria")["monto"].sum().idxmin()
        insights.append(f"Tu mayor gasto es en: {categoria_top}")

    return insights