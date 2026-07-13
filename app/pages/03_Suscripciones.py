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


def _mostrar_kpis(
    kpis: dict,
) -> None:
    """
    Muestra los KPIs principales.
    """

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Suscripciones",
        kpis["total"],
    )

    col2.metric(
        "Costo Mensual",
        f"S/ {kpis['costo_mensual']:,.2f}",
    )

    col3.metric(
        "Costo Anual",
        f"S/ {kpis['costo_anual']:,.2f}",
    )

    col4.metric(
        "Vence pronto",
        kpis["vence_pronto"],
    )

    col5.metric(
        "Vencidas",
        kpis["vencidas"],
    )

    st.divider()


def _aplicar_colores_vencimiento(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una tabla con etiquetas visuales según la cercanía del vencimiento."""
    tabla = df.copy()
    tabla["Estado_Visual"] = "🟢 Vigente"

    if "Dias_Vencimiento" in tabla.columns:
        tabla.loc[tabla["Dias_Vencimiento"] < 0, "Estado_Visual"] = "🔴 Vencida"
        tabla.loc[
            (tabla["Dias_Vencimiento"] >= 0) & (tabla["Dias_Vencimiento"] <= 1),
            "Estado_Visual",
        ] = "🟡 Vence mañana"
        tabla.loc[
            (tabla["Dias_Vencimiento"] > 1) & (tabla["Dias_Vencimiento"] <= 3),
            "Estado_Visual",
        ] = "🔴 Muy urgente"
        tabla.loc[
            (tabla["Dias_Vencimiento"] > 3) & (tabla["Dias_Vencimiento"] <= 7),
            "Estado_Visual",
        ] = "🟠 Próxima"

    return tabla


def _mostrar_alertas(
    alertas: dict,
) -> None:
    """
    Muestra las alertas del dashboard.
    """

    if not alertas["vencidas"].empty:
        st.error(f"Existen {len(alertas['vencidas'])} suscripciones vencidas.")

        st.dataframe(
            alertas["vencidas"][COLUMNAS_ALERTAS],
            use_container_width=True,
            hide_index=True,
        )

    if not alertas["vence_pronto"].empty:
        st.warning(
            f"Existen {len(alertas['vence_pronto'])} suscripciones próximas a vencer."
        )

        st.dataframe(
            alertas["vence_pronto"][COLUMNAS_ALERTAS],
            use_container_width=True,
            hide_index=True,
        )

    if alertas["vencidas"].empty and alertas["vence_pronto"].empty:
        st.success("No existen vencimientos próximos.")

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

_mostrar_kpis(kpis)

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
    tabla = df[COLUMNAS_TABLA].copy()
    tabla["Costo_Mensual"] = tabla["Costo_Mensual"].map(lambda x: f"S/ {x:,.2f}")
    tabla["Costo_Anual"] = tabla["Costo_Anual"].map(lambda x: f"S/ {x:,.2f}")
    tabla = _aplicar_colores_vencimiento(tabla)
    st.dataframe(tabla, use_container_width=True, hide_index=True)

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
