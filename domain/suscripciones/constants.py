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
    "Estado",
    "Grupo",
    "Fecha_Vencimiento",
    "Dias_Vencimiento",
    "Costo_Mensual",
    "Costo_Anual",
    "Estado_Vencimiento",
]

# ==========================================================
# ESTADOS DE VENCIMIENTO
# ==========================================================

ESTADO_VIGENTE = "Vigente"
ESTADO_PROXIMA = "Próxima"
ESTADO_VENCE_PRONTO = "Vence pronto"
ESTADO_VENCIDA = "Vencida"

ESTADOS_VENCIMIENTO = [
    ESTADO_VIGENTE,
    ESTADO_PROXIMA,
    ESTADO_VENCE_PRONTO,
    ESTADO_VENCIDA,
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
