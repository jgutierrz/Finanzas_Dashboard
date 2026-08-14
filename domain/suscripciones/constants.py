from __future__ import annotations

# ==========================================================
# MODELO DE DATOS
# ==========================================================

COLUMNAS_MODELO = [
    "Nombre",
    "Proveedor",
    "Estado",
    "Grupo",
    "Costo_Mensual",
    "Fecha_Vencimiento",
    "Descripcion",
    "Observaciones",
]

# ==========================================================
# COLUMNAS UI
# ==========================================================

COLUMNAS_ALERTAS = [
    "Nombre",
    "Proveedor",
    "Fecha_Vencimiento",
    "Dias_Vencimiento",
    "Costo_Mensual",
]

COLUMNAS_TABLA = [
    "Nombre",
    "Proveedor",
    "Estado",  # Estado de la suscripción
    "Grupo",
    "Fecha_Vencimiento",
    "Dias_Restantes",
    "Estado_UI",  # Estado del vencimiento
    "Costo_Mensual",
    "Costo_Anual",
]

# ==========================================================
# ESTADOS DE VENCIMIENTO
# ==========================================================

ESTADO_VENCIDO = "Vencido"
ESTADO_URGENTE = "Urgente"
ESTADO_PROXIMO = "Próximo"
ESTADO_SEGUIMIENTO = "Seguimiento"
ESTADO_AL_DIA = "Al día"

ESTADOS_VENCIMIENTO = [
    ESTADO_VENCIDO,
    ESTADO_URGENTE,
    ESTADO_PROXIMO,
    ESTADO_SEGUIMIENTO,
    ESTADO_AL_DIA,
]

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

DIAS_ALERTA = 7

DIAS_PROXIMO = 30

# ==========================================================
# MESES
# ==========================================================

MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}
