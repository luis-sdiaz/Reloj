"""ClockStructure: circular doubly linked list for time points.

This module provides `ClockStructure`, a singleton that contains 60
linked `_TimePoint` objects representing seconds/minutes (0..59).
"""

from __future__ import annotations

from typing import Optional


class ClockStructure:
    """Singleton circular doubly linked list with 60 time points.

    The structure initializes 60 `_TimePoint` nodes (values 0..59)
    and links them in a circular doubly linked fashion.
    """

    _instance: Optional["ClockStructure"] = None

    class _TimePoint:
        """Nodo interno que representa un punto de tiempo.

        Attributes:
            value: integer value of the time point (0..59).
            next_point: reference to the next _TimePoint.
            previous_point: reference to the previous _TimePoint.
        """

        __slots__ = ("value", "next_point", "previous_point")

        def __init__(self, value: int) -> None:
            self.value: int = value
            self.next_point: Optional["ClockStructure._TimePoint"] = None
            self.previous_point: Optional["ClockStructure._TimePoint"] = None

        def __repr__(self) -> str:
            return f"<TimePoint {self.value}>"

    def __new__(cls) -> "ClockStructure":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Avoid re-initialization for the singleton
        if getattr(self, "_initialized", False):
            return

        # Create 60 time points (0..59)
        self._points: list[ClockStructure._TimePoint] = [
            self._TimePoint(i) for i in range(60)
        ]

        # Link each point to form a circular doubly linked list
        for index, node in enumerate(self._points):
            node.next_point = self._points[(index + 1) % 60]
            node.previous_point = self._points[(index - 1) % 60]

        # Head reference (value 0)
        self._head: ClockStructure._TimePoint = self._points[0]

        self._initialized = True

    def get_point(self, value: int) -> "ClockStructure._TimePoint":
        """Traverse the list and return the _TimePoint with the given value.

        Args:
            value: integer in range 0..59 representing the requested point.

        Returns:
            The matching `_TimePoint` instance.

        Raises:
            TypeError: if `value` is not an int.
            ValueError: if `value` is outside 0..59.
            LookupError: if the value is not found after a full traversal.
        """

        if not isinstance(value, int):
            raise TypeError("value must be an int")

        if not 0 <= value < 60:
            raise ValueError("value must be in range 0..59")

        current: ClockStructure._TimePoint = self._head
        for _ in range(60):
            if current.value == value:
                return current
            # type: ignore[assignment]
            current = current.next_point  # safe: list is circular

        raise LookupError(f"TimePoint with value {value} not found")
