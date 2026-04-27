"""Factory for clock hands and simple movement logic.

Creates `ClockHand` instances (Hour/Minute/Second) linked to `ClockStructure`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.core.clock_structure import ClockStructure


class ClockHand(ABC):
    """Abstract base class for a clock hand.

    Attributes:
        length: visual length of the hand.
        color: hand color (hex or name).
        current_point: linked `_TimePoint` in `ClockStructure`.
        current_value: current integer value (0..59).
    """

    def __init__(self, length: int, color: str, clock_structure: ClockStructure, start_value: int = 0) -> None:
        self.length: int = length
        self.color: str = color
        self.current_point = clock_structure.get_point(start_value)
        self.current_value: int = self.current_point.value

    @abstractmethod
    def move(self, steps: int = 1) -> bool:
        """Advance the hand by `steps` points.

        Returns True when the hand completes a full rotation.
        """


class SecondHand(ClockHand):
    """Second hand.

    Returns True when a full rotation occurs (minute should advance).
    """

    def move(self, steps: int = 1) -> bool:
        overflow = False
        for _ in range(steps):
            # advance one point in the circular list
            self.current_point = self.current_point.next_point  # type: ignore[attr-defined]
            self.current_value = self.current_point.value
            # full rotation when value is 0
            if self.current_value == 0:
                overflow = True
        return overflow


class MinuteHand(ClockHand):
    """Minute hand.

    Returns True when a full rotation occurs (hour should advance).
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
    """Hour hand.

    In this design the hour hand advances externally when minute overflows.
    """

    def move(self, steps: int = 1) -> bool:
        # hour hand does not propagate overflow
        for _ in range(steps):
            self.current_point = self.current_point.next_point  # type: ignore[attr-defined]
            self.current_value = self.current_point.value
        return False


class HandFactory:
    """Factory to create hand instances.

    Usage:
        hand = HandFactory.create_hand("second", clock_structure, start_value=0, length=90, color="#ff0000")
    """

    @staticmethod
    def create_hand(hand_type: str, clock_structure: ClockStructure, start_value: int = 0, **kwargs: Any) -> ClockHand:
        """Create a hand of the requested type.

        Args:
            hand_type: 'hour' | 'minute' | 'second'.
            clock_structure: ClockStructure instance to bind the hand.
            start_value: initial point (0..59).
            kwargs: optional args like `length` and `color`.

        Returns:
            ClockHand instance.
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
