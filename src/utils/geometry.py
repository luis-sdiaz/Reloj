"""Funciones geométricas para el reloj.

Contiene utilidades para convertir ángulos en coordenadas cartesianas
usadas por la interfaz gráfica.
"""

from math import cos, radians, sin
from typing import Tuple


def get_hand_coordinates(angle: float, radius: float, center: Tuple[float, float]) -> Tuple[float, float]:
    """Convierte un ángulo en coordenadas (x, y) del extremo de la manecilla.

    El ángulo se interpreta en grados con 0 en las 12 en punto y aumenta
    en sentido horario (como en un reloj analógico).

    Args:
        angle: ángulo en grados (0..360), 0 = 12:00.
        radius: longitud desde el centro hasta el extremo.
        center: tupla (x, y) del centro.

    Returns:
        Tupla (x, y) de coordenadas del extremo de la manecilla.
    """

    # Convertimos a radianes ajustando para que 0 grados esté en 12:00
    rad = radians(angle - 90)
    cx, cy = center
    x = cx + radius * cos(rad)
    y = cy + radius * sin(rad)
    return x, y
