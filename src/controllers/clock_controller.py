"""Controller que une el modelo (ClockStructure) con la vista (ClockFace).

La clase `ClockController` consulta la hora del sistema, mapea los
valores a los puntos de la `ClockStructure` y actualiza la `ClockFace`.
Las explicaciones están en español; el código y los identificadores en
inglés según la convención del proyecto.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from config.settings import ClockSettings
from src.core.clock_structure import ClockStructure
from src.services.database_service import DatabaseService
from src.ui.clock_face import ClockFace


class ClockController:
    """Controlador principal del reloj.

    Args:
        model: instancia de `ClockStructure` que contiene los `_TimePoint`.
        view: instancia de `ClockFace` encargada del dibujo.
        settings: instancia de `ClockSettings` con parámetros de refresco.
    """

    def __init__(self, model: ClockStructure, view: ClockFace, settings: ClockSettings) -> None:
        self.model = model
        self.view = view
        self.settings = settings
        # Inicializar servicio de base de datos (singleton)
        self.db = DatabaseService()
        # Asegurarse de que las tablas existen y registrar inicio
        try:
            self.db.create_tables()
            self.db.save_log("Clock System Started")
        except Exception:
            # No detener la aplicación si la BD falla; en producción registrar el error
            pass

        # Histórico del valor de hora para detectar ciclo completo (wrap-around)
        self._prev_hour_value: int | None = None

    def update_time(self) -> None:
        """Advance hands using their `move()` methods and handle overflows.

        The visual movement is driven by stepping the `SecondHand` each
        tick. Overflows propagate to `MinuteHand` and `HourHand` via their
        `move()` return values and the circular `ClockStructure`. No digital
        labels are produced; positions come solely from the circular list.
        """

        # Resolve references to hands by type
        second_hand = None
        minute_hand = None
        hour_hand = None
        for hand in getattr(self.view, "hands", []):
            cls_name = hand.__class__.__name__.lower()
            if "second" in cls_name:
                second_hand = hand
            elif "minute" in cls_name:
                minute_hand = hand
            elif "hour" in cls_name:
                hour_hand = hand

        # Step the second hand one tick; propagate overflow to minute
        second_overflow = False
        if second_hand is not None:
            try:
                second_overflow = second_hand.move(1)
            except Exception:
                second_overflow = False

        minute_overflow = False
        if second_overflow and minute_hand is not None:
            try:
                minute_overflow = minute_hand.move(1)
            except Exception:
                minute_overflow = False

        if minute_overflow and hour_hand is not None:
            # detect previous hour value to identify wrap-around
            prev_hour = hour_hand.current_value
            try:
                hour_hand.move(1)
            except Exception:
                pass
            try:
                if prev_hour is not None and hour_hand.current_value < prev_hour:
                    # full 12-hour cycle completed
                    try:
                        self.db.save_log("Full 12-hour cycle completed")
                    except Exception:
                        pass
            except Exception:
                pass

        # Redraw view according to updated hand positions
        try:
            self.view.update_clock_graphics()
        except Exception:
            pass

        # Schedule next update
        refresh_ms = int(self.settings.REFRESH_RATE)
        self.view.after(refresh_ms, self.update_time)

    def start(self) -> None:
        """Inicia el bucle de actualización del reloj."""

        # Llamada inicial para comenzar el ciclo
        self.update_time()
