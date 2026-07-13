from __future__ import annotations

from dataclasses import dataclass
from datetime import date


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


def obtener_estado(fecha_vencimiento: date) -> dict:
    """
    Calcula el estado de vencimiento de una suscripción.

    Retorna un diccionario con toda la información necesaria
    para la UI y los KPIs.
    """

    hoy = date.today()
    dias = (fecha_vencimiento - hoy).days

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

    return {
        "dias_restantes": dias,
        "estado": estado.nombre,
        "estado_ui": f"{estado.icono} {estado.nombre}",
        "icono": estado.icono,
        "color": estado.color,
        "prioridad": estado.prioridad,
    }
