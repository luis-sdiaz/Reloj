"""Interfaz del reloj usando Tkinter.

La clase `ClockFace` dibuja un reloj circular y redibuja las manecillas
utilizando los valores definidos en `config/settings.py`.
"""

from __future__ import annotations

import tkinter as tk
from typing import Iterable, Tuple

from config.settings import ClockSettings
from src.utils.geometry import get_hand_coordinates


class ClockFace(tk.Frame):
    """Frame que contiene el canvas y lógica de dibujo del reloj.

    Explicación en español: esta clase crea un `tk.Canvas` de dimensiones
    definidas en `ClockSettings.WINDOW_SIZE` y dibuja un círculo central
    con manecillas cuya posición se calcula a partir del valor actual de
    cada `ClockHand`.
    """

    def __init__(self, master: tk.Misc, settings: ClockSettings, hands: Iterable, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self.settings = settings
        self.hands = list(hands)

        self.width, self.height = self.settings.WINDOW_SIZE
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="white")
        self.canvas.pack()

        # Centro y radio extraído de settings
        self.center: Tuple[float, float] = (float(self.settings.CENTER[0]), float(self.settings.CENTER[1]))
        self.clock_radius: float = float(self.settings.CLOCK_RADIUS)

        # Dibujar fondo del reloj (círculo)
        self._draw_face()

    def _draw_face(self) -> None:
        """Dibuja la esfera del reloj usando valores de `ClockSettings`."""

        cx, cy = self.center
        r = self.clock_radius
        # Borde exterior
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#FFFFFF", outline="#333333", width=2)

        # Dibujar marcas cada 5 unidades (marca de hora)
        for i in range(0, 60, 5):
            angle = (i / 60) * 360
            outer = get_hand_coordinates(angle, r, self.center)
            inner = get_hand_coordinates(angle, r * 0.9, self.center)
            self.canvas.create_line(inner[0], inner[1], outer[0], outer[1], fill="#333333", width=3)

    def draw_hand(self, angle: float, length: float, color: str, width: int = 2) -> int:
        """Dibuja una manecilla desde el centro hacia `angle`.

        Args:
            angle: ángulo en grados con 0 = 12:00 y sentido horario.
            length: longitud en píxeles de la manecilla.
            color: color de la línea.
            width: ancho de la línea en píxeles.

        Returns:
            id del elemento creado en el canvas.
        """

        x, y = get_hand_coordinates(angle, length, self.center)
        cx, cy = self.center
        return self.canvas.create_line(cx, cy, x, y, fill=color, width=width, capstyle=tk.ROUND, tags=("hands",))

    def update_clock_graphics(self) -> None:
        """Borra las manecillas actuales y las redibuja según `self.hands`.

        Cada `hand` debe tener los atributos `current_value`, `length` y `color`.
        `length` se interpreta como porcentaje del `CLOCK_RADIUS`.
        """

        # Borrar elementos anteriores con la etiqueta 'hands'
        self.canvas.delete("hands")

        for hand in self.hands:
            # Calcular ángulo desde el valor (0..59)
            angle = (hand.current_value / 60.0) * 360.0

            # Interpretar hand.length como porcentaje (0..100)
            length_pixels = (hand.length / 100.0) * self.clock_radius

            # Determinar ancho visual según tipo
            cls_name = hand.__class__.__name__.lower()
            if "hour" in cls_name:
                width = 6
            elif "minute" in cls_name:
                width = 4
            else:
                width = 2

            self.draw_hand(angle=angle, length=length_pixels, color=hand.color, width=width)
