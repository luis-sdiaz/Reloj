"""Fábrica de manecillas y lógica de movimiento.

Este módulo implementa el patrón Factory Method para crear
manecillas (`ClockHand`) y sus subclases (`HourHand`, `MinuteHand`,
`SecondHand`). Las manecillas se integran con `ClockStructure` apuntando
cada una a un `_TimePoint` de la lista circular.

Las explicaciones están en español; nombres de clases y variables en
inglés según la convención del proyecto.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.core.clock_structure import ClockStructure


class ClockHand(ABC):
    """Clase base abstracta para una manecilla del reloj.

    Atributos:
        length: longitud visual de la manecilla.
        color: color de la manecilla (hex o nombre).
        current_point: referencia al `_TimePoint` dentro de `ClockStructure`.
        current_value: valor entero actual (0..59) obtenido de `current_point`.
    """

    def __init__(self, length: int, color: str, clock_structure: ClockStructure, start_value: int = 0) -> None:
        self.length: int = length
        self.color: str = color
        # `current_point` apunta a un _TimePoint dentro de ClockStructure
        self.current_point = clock_structure.get_point(start_value)
        self.current_value: int = self.current_point.value

    @abstractmethod
    def move(self, steps: int = 1) -> bool:
        """Avanza la manecilla `steps` pasos.

        Retorna True si la manecilla completa una vuelta y debe notificar
        al siguiente nivel (ej. seconds -> minutes).
        """


class SecondHand(ClockHand):
    """Manecilla de segundos.

    Cada vez que completa una vuelta (vuelve a 0) retorna True para indicar
    que el minuto debe avanzar.
    """

    def move(self, steps: int = 1) -> bool:
        overflow = False
        for _ in range(steps):
            # Avanza un punto en la lista circular
            self.current_point = self.current_point.next_point  # type: ignore[attr-defined]
            self.current_value = self.current_point.value
            # Si devuelve a 0, se completó una vuelta
            if self.current_value == 0:
                overflow = True
        return overflow


class MinuteHand(ClockHand):
    """Manecilla de minutos.

    Cuando completa una vuelta (vuelve a 0) retorna True para indicar que
    la hora debe avanzar.
    """

    def move(self, steps: int = 1) -> bool:
        overflow = False
        for _ in range(steps):
            self.current_point = self.current_point.next_point  # type: ignore[attr-defined]
            self.current_value = self.current_point.value
            if self.current_value == 0:
                overflow = True
        return overflow


class HourHand(ClockHand):
    """Manecilla de horas.

    En este diseño simple la `HourHand` avanza un punto por cada 60 minutos
    (es decir, es avanzada externamente cuando `MinuteHand` retorna overflow).
    Dado que la estructura tiene 60 puntos, el movimiento de hora será
    visualmente acorde si se mueve 1/5 de vuelta por cada 12 horas en una
    representación más completa; aquí mantenemos un avance por overflow.
    """

    def move(self, steps: int = 1) -> bool:
        # HourHand no propaga un overflow superior en este diseño.
        for _ in range(steps):
            self.current_point = self.current_point.next_point  # type: ignore[attr-defined]
            self.current_value = self.current_point.value
        return False


class HandFactory:
    """Factory para crear instancias de manecillas.

    Uso:
        hand = HandFactory.create_hand("second", clock_structure, start_value=0, length=90, color="#ff0000")
    """

    @staticmethod
    def create_hand(hand_type: str, clock_structure: ClockStructure, start_value: int = 0, **kwargs: Any) -> ClockHand:
        """Crea una manecilla del tipo solicitado.

        Args:
            hand_type: 'hour' | 'minute' | 'second' (case-insensitive).
            clock_structure: instancia de `ClockStructure` para enlazar la manecilla.
            start_value: punto inicial (0..59) dentro de la estructura.
            kwargs: parámetros opcionales como `length` y `color`.

        Returns:
            Instancia de `ClockHand` correspondiente.
        """

        t = hand_type.strip().lower()
        length = int(kwargs.get("length", 100))
        color = str(kwargs.get("color", "#000000"))

        if t == "second":
            return SecondHand(length=length, color=color, clock_structure=clock_structure, start_value=start_value)
        if t == "minute":
            return MinuteHand(length=length, color=color, clock_structure=clock_structure, start_value=start_value)
        if t == "hour":
            return HourHand(length=length, color=color, clock_structure=clock_structure, start_value=start_value)

        raise ValueError(f"Unknown hand_type: {hand_type}")
