import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datetime import datetime
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Sistema de Gestión Personal",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------------
# Título principal
# ---------------------------------------------------------
st.title("📊 Sistema de Gestión Personal")
st.markdown(
    """
    Bienvenido a tu plataforma personal de análisis y control.

    Desde aquí puedes acceder a los distintos módulos del sistema:
    """
)

# ---------------------------------------------------------
# Información general
# ---------------------------------------------------------
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="💰 Finanzas", value="Dashboard", delta="Ingresos, gastos y ahorro")

with col2:
    st.metric(
        label="📦 Inventario", value="Dashboard", delta="Control de bienes y stock"
    )

with col3:
    st.metric(label="🔁 Suscripciones", value="Dashboard", delta="Pagos recurrentes")

# ---------------------------------------------------------
# Última actualización de archivos
# ---------------------------------------------------------
st.divider()
st.subheader("🕒 Estado de los datos")

archivos = {
    "Finanzas": Path("data/processed/datos.csv"),
    "Inventario": Path("data/processed/inventario.csv"),
    "Suscripciones": Path("data/processed/suscripciones.csv"),
}

for nombre, archivo in archivos.items():
    if archivo.exists():
        fecha_mod = datetime.fromtimestamp(archivo.stat().st_mtime)
        st.success(
            f"✅ {nombre}: actualizado el {fecha_mod.strftime('%d/%m/%Y %H:%M:%S')}"
        )
    else:
        st.warning(f"⚠️ {nombre}: archivo no encontrado")

# ---------------------------------------------------------
# Instrucciones
# ---------------------------------------------------------
st.divider()
st.info(
    """
    Utiliza el menú lateral de Streamlit para navegar entre los módulos:

    - 💰 Finanzas
    - 📦 Inventario
    - 🔁 Suscripciones
    """
)

# ---------------------------------------------------------
# Pie de página
# ---------------------------------------------------------
st.divider()
st.caption("Desarrollado en Python + Streamlit + Notion API")
