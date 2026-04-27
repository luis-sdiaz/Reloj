"""Main controller: advance hands and update the view."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pathlib import Path
import traceback

from src.config.settings import ClockSettings
from src.core.clock_structure import ClockStructure
from src.services.database_service import DatabaseService
from src.ui.clock_face import ClockFace


class ClockController:
    """Main clock controller.

    Args:
        model: ClockStructure instance containing the `_TimePoint`s.
        view: ClockFace instance responsible for rendering.
        settings: ClockSettings instance with refresh parameters.
    """

    def __init__(self, model: ClockStructure, view: ClockFace, settings: ClockSettings) -> None:
        self.model = model
        self.view = view
        self.settings = settings
        self.db = DatabaseService()
        # ensure tables exist and log startup
        try:
            self.db.create_tables()
            self.db.save_log("Clock System Started")
        except Exception:
            # Do not stop the app if DB fails; in production log this error
            pass

        # previous hour value for detecting wrap-around
        self._prev_hour_value: int | None = None

    def update_time(self) -> None:
        """Step second hand, propagate overflows, redraw view."""

        # resolve references to hands by type
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

        # step the second hand one tick; propagate overflow to minute
        second_overflow = False
        if second_hand is not None:
            try:
                second_overflow = second_hand.move(1)
            except Exception:
                try:
                    Path("src/data").mkdir(parents=True, exist_ok=True)
                    with open("src/data/clock_runtime.log", "a", encoding="utf-8") as fh:
                        fh.write("[CONTROLLER] Exception in second_hand.move:\n")
                        fh.write(traceback.format_exc())
                        fh.write("\n")
                except Exception:
                    pass
                second_overflow = False

        minute_overflow = False
        if second_overflow and minute_hand is not None:
            try:
                minute_overflow = minute_hand.move(1)
            except Exception:
                try:
                    Path("src/data").mkdir(parents=True, exist_ok=True)
                    with open("src/data/clock_runtime.log", "a", encoding="utf-8") as fh:
                        fh.write("[CONTROLLER] Exception in minute_hand.move:\n")
                        fh.write(traceback.format_exc())
                        fh.write("\n")
                except Exception:
                    pass
                minute_overflow = False

        if minute_overflow and hour_hand is not None:
            # detect previous hour value to identify wrap-around
            prev_hour = hour_hand.current_value
            try:
                hour_hand.move(1)
            except Exception:
                try:
                    Path("src/data").mkdir(parents=True, exist_ok=True)
                    with open("src/data/clock_runtime.log", "a", encoding="utf-8") as fh:
                        fh.write("[CONTROLLER] Exception in hour_hand.move:\n")
                        fh.write(traceback.format_exc())
                        fh.write("\n")
                except Exception:
                    pass
            try:
                if prev_hour is not None and hour_hand.current_value < prev_hour:
                    # full 12-hour cycle completed
                    try:
                        self.db.save_log("Full 12-hour cycle completed")
                    except Exception:
                        try:
                            with open("src/data/clock_runtime.log", "a", encoding="utf-8") as fh:
                                fh.write("[CONTROLLER] Failed to save full-cycle log\n")
                        except Exception:
                            pass
            except Exception:
                try:
                    with open("src/data/clock_runtime.log", "a", encoding="utf-8") as fh:
                        fh.write("[CONTROLLER] Exception detecting hour wrap:\n")
                        fh.write(traceback.format_exc())
                        fh.write("\n")
                except Exception:
                    pass

        # redraw view according to updated hand positions
        try:
            self.view.update_clock_graphics()
        except Exception:
            try:
                with open("src/data/clock_runtime.log", "a", encoding="utf-8") as fh:
                    fh.write("[CONTROLLER] Exception in update_clock_graphics:\n")
                    fh.write(traceback.format_exc())
                    fh.write("\n")
            except Exception:
                pass

        # Schedule next update
        refresh_ms = int(self.settings.REFRESH_RATE)
        self.view.after(refresh_ms, self.update_time)

    def start(self) -> None:
        """Start the clock update loop."""

        # initial call to begin the update cycle
        self.update_time()
