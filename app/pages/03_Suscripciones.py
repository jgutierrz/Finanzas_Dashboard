from __future__ import annotations

import sys

# ==========================================================
# IMPORTACIONES
# ==========================================================
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

DATA_DIR = ROOT / "data" / "processed"

from domain.suscripciones.constants import (
    COLUMNAS_ALERTAS,
    COLUMNAS_TABLA,
    ESTADOS_VENCIMIENTO,
)
from exporters.suscripciones_excel import exportar_suscripciones_excel
from services.suscripciones_service import (
    actualizar_suscripciones,
    aplicar_filtros,
    calcular_dashboard,
    cargar_suscripciones,
)

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

st.set_page_config(
    page_title="Suscripciones",
    page_icon="💳",
    layout="wide",
)

st.title("💳 Suscripciones")

st.caption("Administración y seguimiento de vencimientos de suscripciones.")

if st.sidebar.button("🔄 Actualizar desde Notion", use_container_width=True):
    with st.spinner("Sincronizando suscripciones desde Notion..."):
        try:
            actualizar_suscripciones(DATA_DIR / "suscripciones.csv")
            st.success("Suscripciones actualizadas correctamente.")
            st.rerun()
        except Exception as exc:
            st.error(f"No se pudieron actualizar las suscripciones: {exc}")

st.sidebar.divider()

# ==========================================================
# FUNCIONES PRIVADAS
# ==========================================================


def _cargar_datos() -> pd.DataFrame:
    """
    Carga las suscripciones procesadas.
    """

    try:
        return cargar_suscripciones()

    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

    except Exception as e:
        st.exception(e)
        st.stop()


def _crear_filtro(
    df: pd.DataFrame,
    columna: str,
    titulo: str,
    opcion_todos: str = "Todos",
) -> str:
    """
    Crea un filtro genérico para el sidebar.
    """

    opciones = sorted(df[columna].dropna().unique())

    return st.sidebar.selectbox(
        titulo,
        [
            opcion_todos,
            *opciones,
        ],
    )


def _crear_filtro_mes(
    df: pd.DataFrame,
) -> tuple[str, dict[str, int]]:
    """
    Crea el filtro de meses respetando
    el orden cronológico.
    """

    meses = (
        df[
            [
                "Mes_Vencimiento",
                "Mes_Nombre",
            ]
        ]
        .drop_duplicates()
        .sort_values(by="Mes_Vencimiento")
    )

    meses_dict = {
        fila["Mes_Nombre"]: fila["Mes_Vencimiento"] for _, fila in meses.iterrows()
    }

    seleccion = st.sidebar.selectbox(
        "Mes",
        [
            "Todos",
            *meses_dict.keys(),
        ],
    )

    return seleccion, meses_dict


def _formatear_dias(dias: int) -> str:
    if dias < 0:
        return f"Hace {abs(dias)} días"
    elif dias == 0:
        return "Hoy"
    elif dias == 1:
        return "1 día"
    else:
        return f"{dias} días"


def _mostrar_kpis(
    kpis: dict,
) -> None:
    """
    Muestra los KPIs generales y el estado de vencimientos.
    """

    # ======================================================
    # RESUMEN GENERAL
    # ======================================================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Suscripciones",
        kpis["total"],
    )

    col2.metric(
        "Costo mensual",
        f"S/ {kpis['costo_mensual']:,.2f}",
    )

    col3.metric(
        "Costo anual",
        f"S/ {kpis['costo_anual']:,.2f}",
    )

    st.markdown("### Estado de vencimientos")

    # ======================================================
    # ESTADOS DE VENCIMIENTO
    # ======================================================

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "⚫ Vencido",
        kpis["vencido"],
    )

    col2.metric(
        "🔴 Urgente",
        kpis["urgente"],
    )

    col3.metric(
        "🟠 Próximo",
        kpis["proximo"],
    )

    col4.metric(
        "🟡 Seguimiento",
        kpis["seguimiento"],
    )

    col5.metric(
        "🟢 Al día",
        kpis["al_dia"],
    )

    st.divider()


def _mostrar_sin_fecha(df: pd.DataFrame) -> None:
    """
    Muestra las suscripciones que no tienen fecha de vencimiento.
    Se utiliza como alerta de calidad de datos.
    """

    if df.empty:
        return

    sin_fecha = df[df["Fecha_Vencimiento"].isna()].copy()

    if sin_fecha.empty:
        return

    st.warning(f"⚠️ Hay {len(sin_fecha)} suscripciones sin fecha de vencimiento.")

    columnas = [
        "Nombre",
        "Proveedor",
        "Estado",
        "Costo_Mensual",
        "Descripcion",
    ]

    tabla = sin_fecha[columnas].copy()

    tabla = tabla.rename(
        columns={
            "Nombre": "Suscripción",
            "Proveedor": "Proveedor",
            "Estado": "Estado",
            "Costo_Mensual": "Costo mensual",
            "Descripcion": "Periodicidad",
        }
    )

    tabla["Costo mensual"] = tabla["Costo mensual"].map(lambda x: f"S/ {x:,.2f}")

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Completa la fecha de vencimiento en Notion para incluir "
        "estas suscripciones en el seguimiento de vencimientos."
    )


def _mostrar_alertas(
    alertas: dict,
) -> None:
    """
    Muestra las suscripciones que requieren atención.
    """

    hay_alertas = False

    # -------------------------------------------------
    # VENCIDOS
    # -------------------------------------------------

    if not alertas["vencidas"].empty:
        hay_alertas = True

        st.error(f"⚫ Existen {len(alertas['vencidas'])} suscripciones vencidas.")

        st.dataframe(
            alertas["vencidas"][COLUMNAS_ALERTAS],
            use_container_width=True,
            hide_index=True,
        )

    # -------------------------------------------------
    # URGENTES
    # -------------------------------------------------

    if not alertas["vence_pronto"].empty:
        hay_alertas = True

        st.warning(
            f"🔴 Existen {len(alertas['vence_pronto'])} "
            "suscripciones que vencen en los próximos 7 días."
        )

        st.dataframe(
            alertas["vence_pronto"][COLUMNAS_ALERTAS],
            use_container_width=True,
            hide_index=True,
        )

    # -------------------------------------------------
    # PRÓXIMOS
    # -------------------------------------------------

    if not alertas["proximas"].empty:
        hay_alertas = True

        st.info(
            f"🟠 Existen {len(alertas['proximas'])} "
            "suscripciones que vencen entre 8 y 15 días."
        )

        st.dataframe(
            alertas["proximas"][COLUMNAS_ALERTAS],
            use_container_width=True,
            hide_index=True,
        )

    # -------------------------------------------------
    # SIN ALERTAS
    # -------------------------------------------------

    if not hay_alertas:
        st.success("🟢 No existen vencimientos que requieran atención.")

    st.divider()


# ==========================================================
# FLUJO PRINCIPAL
# ==========================================================

df = _cargar_datos()

st.sidebar.header("Filtros")

proveedor = _crear_filtro(
    df=df,
    columna="Proveedor",
    titulo="Proveedor",
)

estado = _crear_filtro(
    df=df,
    columna="Estado",
    titulo="Estado",
)

grupo = _crear_filtro(
    df=df,
    columna="Grupo",
    titulo="Grupo",
)

estado_vencimiento = st.sidebar.selectbox(
    "Estado de Vencimiento",
    [
        "Todos",
        *ESTADOS_VENCIMIENTO,
    ],
)

mes, meses_dict = _crear_filtro_mes(df)

df = aplicar_filtros(
    df=df,
    proveedor=proveedor,
    estado=estado,
    grupo=grupo,
    estado_vencimiento=estado_vencimiento,
    mes=None if mes == "Todos" else meses_dict[mes],
)

dashboard = calcular_dashboard(df)

kpis = dashboard["kpis"]

alertas = dashboard["alertas"]

df_proveedores = dashboard["proveedores"]

df_vencimientos = dashboard["vencimientos"]

df_proximos = dashboard["proximos"]

# -------------------------------------------------
# Control de calidad de datos
# -------------------------------------------------

_mostrar_sin_fecha(df)

# -------------------------------------------------
# KPIs
# -------------------------------------------------

_mostrar_kpis(kpis)

# -------------------------------------------------
# Alertas de vencimiento
# -------------------------------------------------

_mostrar_alertas(alertas)

st.subheader("Resumen por proveedor")
if not df_proveedores.empty:
    st.dataframe(
        df_proveedores.rename(
            columns={"Proveedor": "Proveedor", "Costo_Mensual": "Costo mensual"}
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No hay información de proveedores para mostrar.")

st.subheader("Próximos vencimientos")
if not df_proximos.empty:
    st.dataframe(
        df_proximos[
            [
                "Nombre",
                "Proveedor",
                "Fecha_Vencimiento",
                "Dias_Vencimiento",
                "Costo_Mensual",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No hay vencimientos próximos para mostrar.")

st.subheader("Detalle de suscripciones")
if not df.empty:
    # tabla = df[COLUMNAS_TABLA].copy()
    tabla = df[COLUMNAS_TABLA + ["Color"]].copy()
    # ==========================================================
    # Formato de fecha
    # ==========================================================

    tabla["Fecha_Vencimiento"] = (
        pd.to_datetime(tabla["Fecha_Vencimiento"]).dt.strftime("%d-%b-%Y").str.lower()
    )

    # -------------------------------------------------
    # Formatos monetarios
    # -------------------------------------------------

    tabla["Costo_Mensual"] = tabla["Costo_Mensual"].map(lambda x: f"S/ {x:,.2f}")

    tabla["Costo_Anual"] = tabla["Costo_Anual"].map(lambda x: f"S/ {x:,.2f}")

    # -------------------------------------------------
    # Mostrar estado visual
    # -------------------------------------------------

    tabla = tabla.rename(
        columns={
            "Fecha_Vencimiento": "Vence",
            "Dias_Restantes": "Días",
            "Estado_UI": "Vencimiento",
            "Costo_Mensual": "Costo mensual",
            "Costo_Anual": "Costo anual",
        }
    )

    # -------------------------------------------------
    # Formato visual de fecha
    # -------------------------------------------------

    tabla["Vence"] = pd.to_datetime(tabla["Vence"]).dt.strftime("%d/%m/%Y")

    # -------------------------------------------------
    # Color de vencimiento
    # -------------------------------------------------

    colores_vencimiento = tabla["Color"].copy()

    tabla = tabla.drop(columns=["Color"])

    def _estilizar_vencimiento(row):
        color = colores_vencimiento.loc[row.name]

        estilos = [""] * len(row)

        indice_vencimiento = row.index.get_loc("Vencimiento")

        estilos[indice_vencimiento] = f"color: {color}; font-weight: 600;"

        return estilos

    tabla_estilizada = tabla.style.apply(_estilizar_vencimiento, axis=1).format(
        {"Días": "{:.0f}"}
    )

    st.dataframe(
        tabla_estilizada,
        use_container_width=True,
        hide_index=True,
    )

    archivo_excel = exportar_suscripciones_excel(df)
    with open(archivo_excel, "rb") as fh:
        st.download_button(
            label="📥 Descargar Excel profesional",
            data=fh.read(),
            file_name="suscripciones_reporte.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
else:
    st.info("No hay suscripciones para mostrar.")
