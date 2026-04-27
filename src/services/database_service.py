"""Simple SQLite persistence service.

Provides `DatabaseService` singleton for a local DB at `src/data/clock_data.db`.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


class DatabaseService:
    """Singleton managing a SQLite connection and simple log table."""

    _instance: Optional["DatabaseService"] = None

    def __new__(cls, db_path: Optional[str] = None) -> "DatabaseService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: Optional[str] = None) -> None:
        if getattr(self, "_initialized", False):
            return

        # DB file path (default: src/data/clock_data.db)
        if db_path:
            base = Path(db_path)
        else:
            base = Path(__file__).resolve().parents[1] / "data" / "clock_data.db"

        base.parent.mkdir(parents=True, exist_ok=True)
        self.db_path: Path = base

        # Connect to SQLite (allow access from other threads if needed)
        self.conn: sqlite3.Connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        self._initialized = True

    def create_tables(self) -> None:
        """Create required tables (simple `logs` table)."""

        sql = """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_description TEXT NOT NULL
        );
        """
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def save_log(self, description: str) -> int:
        """Insert an event log and return its id."""

        ts = datetime.utcnow().isoformat()
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO logs (timestamp, event_description) VALUES (?, ?)",
            (ts, description),
        )
        self.conn.commit()
        return cur.lastrowid

    def close(self) -> None:
        """Close the database connection."""

        try:
            self.conn.close()
        except Exception:
            pass
