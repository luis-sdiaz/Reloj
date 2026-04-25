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
        """Actualizar la posición de las manecillas según la hora actual.

        Pasos:
        1. Obtener la hora actual con `datetime.now()`.
        2. Mapear segundos, minutos y horas a valores 0..59.
        3. Obtener los `_TimePoint` correspondientes desde `ClockStructure`.
        4. Actualizar `current_point` y `current_value` de cada `ClockHand` en la vista.
        5. Llamar a la vista para redibujar (`update_clock_graphics`).
        6. Reprogramar la siguiente actualización usando `after`.
        """

        now = datetime.now()

        # Valores directos
        second_value: int = now.second
        minute_value: int = now.minute

        # Mapear horas a la escala 0..59: cada hora = 5 unidades, además
        # incorporamos el avance por minutos (fraccional).
        hour_position = (now.hour % 12) * 5 + (now.minute / 60.0) * 5
        # Convertir a entero cercano y asegurarnos rango 0..59
        hour_value: int = int(round(hour_position)) % 60

        # Detectar wrap-around de la manecilla de la hora (final de ciclo de 12 horas)
        if getattr(self, "_prev_hour_value", None) is not None:
            if self._prev_hour_value > hour_value:
                try:
                    self.db.save_log("Full 12-hour cycle completed")
                except Exception:
                    pass

        # Actualizar las manecillas en la vista
        for hand in getattr(self.view, "hands", []):
            name = hand.__class__.__name__.lower()
            if "second" in name:
                tp = self.model.get_point(second_value)
            elif "minute" in name:
                tp = self.model.get_point(minute_value)
            elif "hour" in name:
                tp = self.model.get_point(hour_value)
            else:
                # Si no reconocemos el tipo, saltamos
                continue

            # Enlazar la manecilla al TimePoint correspondiente
            hand.current_point = tp
            hand.current_value = tp.value

        # Actualizar histórico de hora
        self._prev_hour_value = hour_value

        # Pedir a la vista que redibuje
        self.view.update_clock_graphics()

        # Reprogramar la siguiente actualización
        refresh_ms = int(self.settings.REFRESH_RATE)
        # `after` acepta milisegundos; usamos la vista (frame) para programar
        self.view.after(refresh_ms, self.update_time)

    def start(self) -> None:
        """Inicia el bucle de actualización del reloj."""

        # Llamada inicial para comenzar el ciclo
        self.update_time()
