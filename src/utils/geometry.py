"""Geometric utilities for the clock.

Utilities to convert angles into Cartesian coordinates used by the UI.
"""

from math import cos, radians, sin
from typing import Tuple


def get_hand_coordinates(angle: float, radius: float, center: Tuple[float, float]) -> Tuple[float, float]:
    """Convert an angle to (x, y) coordinates at the hand tip.

    Angle is given in degrees with 0 at 12:00 and increases clockwise.

    Args:
        angle: degrees (0..360), 0 == 12:00.
        radius: distance from center to tip.
        center: (x, y) center coordinates.

    Returns:
        (x, y) coordinates of the hand tip.
    """

    rad = radians(angle - 90)
    cx, cy = center
    x = cx + radius * cos(rad)
    y = cy + radius * sin(rad)
    return x, y
