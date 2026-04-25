"""Entry point for the Reloj project.

Este módulo integra el modelo (`ClockStructure`), la vista
(`ClockFace`) y el controlador (`ClockController`) para ejecutar
la aplicación de reloj usando Tkinter.
"""

from __future__ import annotations

from datetime import datetime
import tkinter as tk
from typing import List

from config.settings import ClockSettings
from src.core.clock_structure import ClockStructure
from src.core.hand_factory import HandFactory
from src.services.database_service import DatabaseService
from src.ui.clock_face import ClockFace
from src.controllers.clock_controller import ClockController


def main() -> None:
    """Inicializa componentes y arranca la aplicación Tkinter.

    Pasos:
    - Crear `ClockStructure` (modelo).
    - Crear manecillas usando `HandFactory`.
    - Crear `ClockFace` (vista) y empaquetarla en la ventana principal.
    - Crear `ClockController` y arrancar el ciclo de actualización.
    """

    settings = ClockSettings()

    # Modelo
    model = ClockStructure()

    # Valores iniciales basados en la hora actual
    now = datetime.now()
    second_start = now.second
    minute_start = now.minute
    hour_pos = (now.hour % 12) * 5 + (now.minute / 60.0) * 5
    hour_start = int(round(hour_pos)) % 60

    # Crear manecillas con HandFactory; usamos longitudes relativas y colores
    second_hand = HandFactory.create_hand(
        "second",
        model,
        start_value=second_start,
        length=100,
        color=settings.HAND_COLORS.get("second", "#FF0000"),
    )

    minute_hand = HandFactory.create_hand(
        "minute",
        model,
        start_value=minute_start,
        length=90,
        color=settings.HAND_COLORS.get("minute", "#000000"),
    )

    hour_hand = HandFactory.create_hand(
        "hour",
        model,
        start_value=hour_start,
        length=70,
        color=settings.HAND_COLORS.get("hour", "#000000"),
    )

    hands: List = [hour_hand, minute_hand, second_hand]

    # Vista
    root = tk.Tk()
    root.title("Proyecto Reloj")
    w, h = settings.WINDOW_SIZE
    root.geometry(f"{w}x{h}")

    view = ClockFace(root, settings, hands)
    view.pack(expand=True, fill=tk.BOTH)

    # Controlador
    controller = ClockController(model=model, view=view, settings=settings)
    controller.start()

    # Handler para cierre ordenado: cerrar DatabaseService antes de destruir la ventana
    def on_close() -> None:
        try:
            DatabaseService().close()
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # Ejecutar la interfaz
    root.mainloop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # Cierre ordenado si el usuario interrumpe desde la terminal
        try:
            DatabaseService().close()
        except Exception:
            pass
        print("Interrupted by user, exiting.")
