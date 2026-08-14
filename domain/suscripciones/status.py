from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

import pandas as pd


@dataclass(frozen=True)
class EstadoVencimiento:
    nombre: str
    icono: str
    color: str
    prioridad: int


ESTADOS = (
    EstadoVencimiento("Vencido", "⚫", "#616161", 1),
    EstadoVencimiento("Urgente", "🔴", "#D32F2F", 2),
    EstadoVencimiento("Próximo", "🟠", "#F57C00", 3),
    EstadoVencimiento("Seguimiento", "🟡", "#FBC02D", 4),
    EstadoVencimiento("Al día", "🟢", "#388E3C", 5),
)


def obtener_estado(fecha_vencimiento) -> dict:
    """
    Calcula el estado de vencimiento de una suscripción.

    Acepta fechas provenientes de Pandas (Timestamp),
    datetime o date.

    Retorna un diccionario con la información necesaria
    para la UI y los KPIs.
    """

    # ------------------------------------------------------
    # Validación de fecha
    # ------------------------------------------------------

    if pd.isna(fecha_vencimiento):
        return {
            "dias_restantes": None,
            "estado": "Sin fecha",
            "estado_ui": "⚪ Sin fecha",
            "icono": "⚪",
            "color": "#9E9E9E",
            "prioridad": 99,
        }

    # ------------------------------------------------------
    # Normalización de fecha
    # ------------------------------------------------------

    if isinstance(fecha_vencimiento, pd.Timestamp) or isinstance(
        fecha_vencimiento, datetime
    ):
        fecha_vencimiento = fecha_vencimiento.date()

    # ------------------------------------------------------
    # Cálculo
    # ------------------------------------------------------

    hoy = date.today()
    dias = (fecha_vencimiento - hoy).days

    # ------------------------------------------------------
    # Clasificación
    # ------------------------------------------------------

    if dias < 0:
        estado = ESTADOS[0]

    elif dias <= 7:
        estado = ESTADOS[1]

    elif dias <= 15:
        estado = ESTADOS[2]

    elif dias <= 30:
        estado = ESTADOS[3]

    else:
        estado = ESTADOS[4]

    # ------------------------------------------------------
    # Resultado
    # ------------------------------------------------------

    return {
        "dias_restantes": dias,
        "estado": estado.nombre,
        "estado_ui": f"{estado.icono} {estado.nombre}",
        "icono": estado.icono,
        "color": estado.color,
        "prioridad": estado.prioridad,
    }
