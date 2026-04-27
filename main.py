"""Entry point for the clock project.

Initializes the model, view and controller and launches the Tkinter app.
"""

from __future__ import annotations

import os
import sys
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True

from datetime import datetime
from pathlib import Path
import signal
import traceback

def _signal_handler(signum, frame):
    try:
        Path("src/data").mkdir(parents=True, exist_ok=True)
        with open("src/data/clock_runtime.log", "a", encoding="utf-8") as fh:
            fh.write(f"[SIGNAL] Received signal: {signum}\n")
            fh.write("[SIGNAL] Stack at signal:\n")
            fh.write("".join(traceback.format_stack(frame)))
            fh.write("\n")
    except Exception:
        pass

    try:
        signal.signal(signal.SIGINT, _signal_handler)
        try:
            signal.signal(signal.SIGTERM, _signal_handler)
        except Exception:
            pass
    except Exception:
        pass
import tkinter as tk
from typing import List

from src.config.settings import ClockSettings
from src.core.clock_structure import ClockStructure
from src.core.hand_factory import HandFactory
from src.services.database_service import DatabaseService
from src.ui.clock_face import ClockFace
from src.controllers.clock_controller import ClockController


def main() -> None:
    """Initialize components and start the Tkinter application.

    Creates model, hands, view and controller and enters mainloop.
    """

    runtime_log = Path("src/data/clock_runtime.log")
    try:
        runtime_log.parent.mkdir(parents=True, exist_ok=True)
        with runtime_log.open("a", encoding="utf-8") as fh:
            fh.write("[MAIN] Starting main()\n")
    except Exception:
        pass

    settings = ClockSettings()

    model = ClockStructure()

    now = datetime.now()
    second_start = now.second
    minute_start = now.minute
    hour_pos = (now.hour % 12) * 5 + (now.minute / 60.0) * 5
    hour_start = int(round(hour_pos)) % 60

    # create hands via HandFactory
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

    # initialize DB before UI
    try:
        DatabaseService().create_tables()
        DatabaseService().save_log("Clock System Started")
    except Exception:
        pass

    root = tk.Tk()
    root.title("Clock Project")
    # fixed initial window size
    root.geometry("600x600")
    root.minsize(600, 600)

    view = ClockFace(root, settings, hands)
    view.pack(expand=True, fill=tk.BOTH)

    try:
        with runtime_log.open("a", encoding="utf-8") as fh:
            fh.write("[MAIN] View packed\n")
    except Exception:
        pass

    controller = ClockController(model=model, view=view, settings=settings)
    controller.start()

    try:
        with runtime_log.open("a", encoding="utf-8") as fh:
            fh.write("[MAIN] Controller started\n")
    except Exception:
        pass

    def _on_destroy(evt: tk.Event) -> None:
        try:
            with runtime_log.open("a", encoding="utf-8") as fh:
                fh.write(f"[MAIN] Destroy event: widget={evt.widget} obj={repr(evt)}\n")
        except Exception:
            pass

    root.bind("<Destroy>", _on_destroy)
    view.canvas.bind("<Destroy>", _on_destroy)

    def on_close() -> None:
        import traceback
        try:
            DatabaseService().close()
        except Exception:
            pass
        try:
            with runtime_log.open("a", encoding="utf-8") as fh:
                fh.write("[MAIN] on_close invoked\n")
                fh.write("[MAIN] on_close stack:\n")
                fh.write("".join(traceback.format_stack()))
                fh.write("\n")
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    try:
        with runtime_log.open("a", encoding="utf-8") as fh:
            fh.write("[MAIN] Entering mainloop\n")
    except Exception:
        pass
    root.mainloop()
    try:
        with runtime_log.open("a", encoding="utf-8") as fh:
            fh.write("[MAIN] mainloop exited\n")
    except Exception:
        pass


if __name__ == '__main__':
    import traceback
    try:
        main()
    except KeyboardInterrupt:
        # log KeyboardInterrupt for diagnostics
        try:
            Path("src/data").mkdir(parents=True, exist_ok=True)
            with open("src/data/clock_runtime.log", "a", encoding="utf-8") as fh:
                fh.write("[MAIN] KeyboardInterrupt caught\n")
                import traceback

                fh.write(traceback.format_exc())
                fh.write("\n")
        except Exception:
            pass
        # tidy shutdown when user interrupts from terminal
        try:
            DatabaseService().close()
        except Exception:
            pass
        print("Interrupted by user, exiting.")
    except Exception:
        # write traceback to file for diagnostics and re-raise
        try:
            Path("src/data").mkdir(parents=True, exist_ok=True)
            with open("src/data/clock_error.log", "a", encoding="utf-8") as fh:
                fh.write("--- Exception on startup ---\n")
                fh.write(traceback.format_exc())
                fh.write("\n")
        except Exception:
            pass
        raise
