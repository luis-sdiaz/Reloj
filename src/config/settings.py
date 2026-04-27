"""Project settings for the clock application.

Defines `ClockSettings` containing configuration constants.
"""

from typing import Dict, Final, Tuple


class ClockSettings:
    """Constant settings for the clock.

    Attributes:
        WINDOW_SIZE: tuple (width, height) in pixels.
        CLOCK_RADIUS: clock radius in pixels.
        HAND_COLORS: dict with colors for hour, minute, second.
        CENTER: (x, y) center coordinates.
        REFRESH_RATE: GUI refresh interval in milliseconds.
    """

    # window size (width, height)
    WINDOW_SIZE: Final[Tuple[int, int]] = (500, 500)
    # clock radius in pixels
    CLOCK_RADIUS: Final[int] = 200
    # hand colors: hour, minute, second
    HAND_COLORS: Final[Dict[str, str]] = {
        "hour": "#2E4057",
        "minute": "#6C7A89",
        "second": "#B03A2E",
    }
    # center coordinates (x, y)
    CENTER: Final[Tuple[int, int]] = (
        WINDOW_SIZE[0] // 2,
        WINDOW_SIZE[1] // 2,
    )
    # refresh time in milliseconds
    REFRESH_RATE: Final[int] = 1000

    @classmethod
    def get_default_theme(cls) -> Dict[str, object]:

        """Return default theme configuration as a dictionary."""

        return {
            "window_size": cls.WINDOW_SIZE,
            "clock_radius": cls.CLOCK_RADIUS,
            "hand_colors": cls.HAND_COLORS,
            "center": cls.CENTER,
            "refresh_rate": cls.REFRESH_RATE,
        }
