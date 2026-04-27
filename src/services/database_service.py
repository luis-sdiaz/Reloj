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
        cur = self.conn.cursor()
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_description TEXT NOT NULL
        );
        """
        )
        # settings table for simple key/value pairs
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
        )
        self.conn.commit()

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Return the string value for `key` or `default` if missing."""

        cur = self.conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cur.fetchone()
        if row:
            return row[0]
        return default

    def set_setting(self, key: str, value: str) -> None:
        """Insert or update a setting key/value pair."""

        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
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
