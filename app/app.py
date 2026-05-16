import sys
import os

# ✅ ya no dependes de esto si usas -m, pero lo dejamos por compatibilidad
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd

from domain.finanzas.metrics import detectar_alertas
from scripts.update_data import actualizar_datos  # 🔥 BOTÓN

# -------------------------
# ⚙️ CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard Financiero", layout="wide")

# -------------------------
# 🔄 BOTÓN ACTUALIZAR PRO
# -------------------------
st.title("💰 Dashboard Financiero PRO")

if "actualizando" not in st.session_state:
    st.session_state.actualizando = False

col_btn, col_info = st.columns([1, 3])

with col_btn:
    if st.button("🔄 Actualizar datos") and not st.session_state.actualizando:

        st.session_state.actualizando = True

        with st.spinner("Actualizando datos desde Notion..."):
            try:
                total = actualizar_datos()
                st.success(f"✅ {total} registros actualizados")
            except Exception as e:
                st.error(f"❌ Error: {e}")

        st.session_state.actualizando = False
        st.rerun()

# -------------------------
# 📥 Cargar datos
# -------------------------
df = pd.read_csv("data/processed/datos.csv")

df["descripcion"] = df["descripcion"].fillna("")
df["categoria"] = df["categoria"].fillna("Sin categoría")

df["fecha"] = pd.to_datetime(df["fecha"])
df["mes"] = df["fecha"].dt.to_period("M").astype(str)
df["año"] = df["fecha"].dt.year

df["flujo"] = df["monto"]

# -------------------------
# 🚫 Excluir transferencias
# -------------------------
df = df[~df["tipo"].str.contains("Transfer", case=False, na=False)]

# -------------------------
# 🎯 FILTROS
# -------------------------
años = sorted(df["año"].unique(), reverse=True)
año_seleccionado = st.selectbox("Selecciona año", años)

df_año = df[df["año"] == año_seleccionado]

meses = sorted(df_año["mes"].unique(), reverse=True)
mes_seleccionado = st.selectbox("Selecciona mes", meses)

df_filtrado = df_año[df_año["mes"] == mes_seleccionado]
df_gastos = df_año[df_año["monto"] < 0]

# -------------------------
# 💰 KPIs
# -------------------------
ingresos = df_filtrado[df_filtrado["monto"] > 0]["monto"].sum()
gastos = df_filtrado[df_filtrado["monto"] < 0]["monto"].sum()
balance = ingresos + gastos

col1, col2, col3 = st.columns(3)

col1.metric("Ingresos (Mes)", f"S/ {ingresos:,.2f}")
col2.metric("Gastos (Mes)", f"S/ {gastos:,.2f}")
col3.metric("Balance (Mes)", f"S/ {balance:,.2f}")

# -------------------------
# 📊 SCORE FINANCIERO PRO
# -------------------------
st.subheader("📊 Score financiero mensual")

score = 100

if balance < 0:
    score -= 40

if abs(gastos) > ingresos:
    score -= 30

ratio_gasto = abs(gastos) / ingresos if ingresos > 0 else 1

if ratio_gasto > 0.8:
    score -= 20

score = max(score, 0)

st.metric("Score", f"{score}/100")

if score > 80:
    st.success("✔️ Excelente salud financiera")
elif score > 50:
    st.warning("⚠️ Salud financiera media")
else:
    st.error("🚨 Riesgo financiero")

# -------------------------
# 📊 RESUMEN ANUAL
# -------------------------
st.subheader("📊 Resumen anual")

ingresos_año = df_año[df_año["monto"] > 0]["monto"].sum()
gastos_año = df_año[df_año["monto"] < 0]["monto"].sum()
balance_año = ingresos_año + gastos_año

col1, col2, col3 = st.columns(3)

col1.metric("Ingresos Año", f"S/ {ingresos_año:,.2f}")
col2.metric("Gastos Año", f"S/ {gastos_año:,.2f}")
col3.metric("Balance Año", f"S/ {balance_año:,.2f}")

# -------------------------
# 📈 BALANCE ACUMULADO
# -------------------------
st.subheader("📈 Balance acumulado del año")

df_ordenado = df_año.sort_values("fecha").copy()
df_ordenado["acumulado"] = df_ordenado["flujo"].cumsum()

acumulado_mensual = df_ordenado.groupby("mes")["acumulado"].last()

st.line_chart(acumulado_mensual)

# -------------------------
# 🔮 PROYECCIÓN
# -------------------------
if len(acumulado_mensual) > 0:
    promedio = balance_año / len(acumulado_mensual)
    proyeccion = promedio * 12

    st.subheader("🔮 Proyección fin de año")
    st.metric("Proyección", f"S/ {proyeccion:,.2f}")

# -------------------------
# 📊 ACUMULADO POR CATEGORÍA
# -------------------------
st.subheader("📊 Acumulado por categoría")

acumulado_cat = df_gastos.groupby("categoria")["monto"].sum().sort_values()
st.bar_chart(acumulado_cat)

# -------------------------
# 🧭 TABS
# -------------------------
tab1, tab2 = st.tabs(["📅 Mensual", "📊 Anual"])

# =========================
# 📅 TAB MENSUAL
# =========================
with tab1:

    st.subheader(f"📂 Categorías - {mes_seleccionado}")

    gastos_categoria = df_filtrado[df_filtrado["monto"] < 0] \
        .groupby("categoria")["monto"].sum().sort_values()

    st.bar_chart(gastos_categoria)

    st.subheader("📊 Ingresos vs Gastos")

    ingresos_mes = ingresos
    gastos_mes = abs(gastos)

    df_resumen = pd.DataFrame({
        "Tipo": ["Ingresos", "Gastos"],
        "Monto": [ingresos_mes, gastos_mes]
    })

    st.bar_chart(df_resumen.set_index("Tipo"))

# =========================
# 📊 TAB ANUAL
# =========================
with tab2:
    st.subheader("📊 Evolución mensual por categoría")

    tabla = df_gastos.groupby(["mes", "categoria"])["monto"] \
        .sum().unstack(fill_value=0)

    # -------------------------
    # 🎯 FILTRO DE CATEGORÍAS
    # -------------------------
    categorias_disponibles = list(tabla.columns)

    categorias_sel = st.multiselect(
        "Selecciona categorías",
        categorias_disponibles,
        default=categorias_disponibles[:5]  # primeras 5 por defecto
    )

    tabla_filtrada = tabla[categorias_sel]

    # -------------------------
    # 📊 ORDENAR POR IMPACTO
    # -------------------------
    orden = st.selectbox(
        "Ordenar por",
        ["Mayor gasto total", "Alfabético"]
    )

    if orden == "Mayor gasto total":
        orden_cols = tabla_filtrada.sum().sort_values().index
        tabla_filtrada = tabla_filtrada[orden_cols]

    elif orden == "Alfabético":
        tabla_filtrada = tabla_filtrada[sorted(tabla_filtrada.columns)]

    # -------------------------
    # 📋 MOSTRAR
    # -------------------------
    st.dataframe(tabla_filtrada)

    # -------------------------
    # 📈 OPCIONAL: GRÁFICO
    # -------------------------
    st.line_chart(tabla_filtrada)
    


    st.subheader("📈 Tendencia por categoría")

    categoria_sel = st.selectbox(
        "Categoría",
        sorted(df_gastos["categoria"].unique())
    )

    df_cat = df_gastos[df_gastos["categoria"] == categoria_sel] \
        .groupby("mes")["monto"].sum()

    st.line_chart(df_cat)

    # -------------------------
    # 🧠 ALERTAS INTELIGENTES PRO
    # -------------------------
    st.subheader("🧠 Alertas inteligentes")

    alertas = []

    for cat in df_gastos["categoria"].unique():
        serie = df_gastos[df_gastos["categoria"] == cat] \
            .groupby("mes")["monto"].sum()

        if len(serie) >= 4:
            ultimo = serie.iloc[-1]
            baseline = serie.iloc[-4:-1].mean()

            if baseline != 0 and abs(ultimo) > abs(baseline) * 1.25:
                alertas.append(f"📈 {cat} fuera de tendencia")

    if alertas:
        for a in alertas:
            st.warning(a)
    else:
        st.success("✔️ Comportamiento estable")

# -------------------------
# 📋 MOVIMIENTOS
# -------------------------
st.subheader("📋 Movimientos")

st.dataframe(df_filtrado.sort_values(by="fecha", ascending=False))