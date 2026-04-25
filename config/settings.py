# """Configuraciones del proyecto Reloj.
#
# Este módulo define la clase `ClockSettings` que contiene constantes
# de configuración para la aplicación de reloj.
# """

from typing import Dict, Final, Tuple


class ClockSettings:
	"""Ajustes constantes para el reloj (POO).

	Atributos (comentarios en español):
	- WINDOW_SIZE: tupla (ancho, alto) de la ventana en píxeles.
	- CLOCK_RADIUS: radio del círculo del reloj en píxeles.
	- HAND_COLORS: diccionario con colores para hour, minute, second.
	- CENTER: coordenadas (x, y) del centro del reloj.
	- REFRESH_RATE: tiempo en milisegundos para refrescar la GUI.
	"""

	# Tamaño de la ventana (ancho, alto)
	WINDOW_SIZE: Final[Tuple[int, int]] = (500, 500)

	# Radio del reloj en píxeles
	CLOCK_RADIUS: Final[int] = 200

	# Colores elegantes para las manecillas: hour, minute, second
	HAND_COLORS: Final[Dict[str, str]] = {
		"hour": "#2E4057",    # azul oscuro grisáceo
		"minute": "#6C7A89",  # gris azulado
		"second": "#B03A2E",  # rojo ladrillo elegante
	}

	# Coordenadas del centro del reloj (x, y)
	CENTER: Final[Tuple[int, int]] = (
		WINDOW_SIZE[0] // 2,
		WINDOW_SIZE[1] // 2,
	)

	# Tiempo de refresco en milisegundos
	REFRESH_RATE: Final[int] = 1000

	@classmethod
	def get_default_theme(cls) -> Dict[str, object]:
		"""Retorna la configuración básica (tema) del reloj.

		Devuelve un diccionario con los valores principales que pueden
		usarse para inicializar la UI o pasar la configuración a
		componentes de presentación.
		"""

		return {
			"window_size": cls.WINDOW_SIZE,
			"clock_radius": cls.CLOCK_RADIUS,
			"hand_colors": cls.HAND_COLORS,
			"center": cls.CENTER,
			"refresh_rate": cls.REFRESH_RATE,
		}

