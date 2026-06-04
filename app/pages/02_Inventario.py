#1.Importaciones
import streamlit as st
import pandas as pd

#2.Configuración página
st.set_page_config(
    page_title="Inventario",
    page_icon="💻",
    layout="wide"
)

#3.Cargar CSV
df = pd.read_csv(
    "data/processed/inventario.csv"
)

#4.Filtros
st.sidebar.header("Filtros")

    #Filtro Tipo
tipos = sorted(
    df["Tipo"]
    .dropna()
    .unique()
)
tipo_seleccionado = st.sidebar.selectbox(
    "Tipo",
    ["Todos"] + list(tipos)
)

    #Filtro Marca
marcas = sorted(
    df["Marca"]
    .dropna()
    .unique()
)
marca_seleccionada = st.sidebar.selectbox(
    "Marca",
    ["Todas"] + list(marcas)
)

#Aplicar filtros
df_filtrado = df.copy()
if tipo_seleccionado != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["Tipo"]
        == tipo_seleccionado
    ]

if marca_seleccionada != "Todas":

    df_filtrado = df_filtrado[
        df_filtrado["Marca"]
        == marca_seleccionada
    ]


#5.KPIs iniciales
total_equipos = len(df_filtrado)

    #Equipos Sin Asignar
equipos_asignados = (
    df_filtrado["Asignado"]
    .fillna("")
    .astype(str)
    .str.strip()
    != ""
).sum()

    #Equipos sin asignar
sin_asignar = total_equipos - equipos_asignados

    #Total Marcas
total_marcas = df["Marca"].nunique()

#6.Mostrar KPIs
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Equipos",
    total_equipos
)

col2.metric(
    "Asignados",
    equipos_asignados
)

col3.metric(
    "Disponibles",
    sin_asignar
)

col4.metric(
    "Marcas",
    total_marcas
)

#7.Tabla principal
st.subheader("Inventario")

st.dataframe(
    df_filtrado,
    use_container_width=True
)

#8.Primer gráfico
    #Equipos por tipo
st.subheader("Equipos por Tipo")

tipo_chart = (
    df["Tipo"]
    .value_counts()
)

st.bar_chart(tipo_chart)

#9.Alertas simples
    #Equipos sin serie
sin_serie = df_filtrado[
    df_filtrado["Serie"]
    .fillna("")
    .astype(str)
    .str.strip()
    == ""
]

#10.Mostrar Alertas
if len(sin_serie) > 0:

    st.warning(
        f"Hay {len(sin_serie)} equipos sin serie."
    )

