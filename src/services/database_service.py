"""Servicio de persistencia usando SQLite.

Este módulo expone `DatabaseService`, un singleton que gestiona la
conexión a la base de datos `data/clock_data.db` y ofrece métodos para
crear tablas e insertar logs de eventos.

Las explicaciones están en español; los identificadores en inglés.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


class DatabaseService:
    """Singleton que gestiona la conexión a SQLite.

    Atributos:
        db_path: ruta al archivo de base de datos.
        conn: objeto sqlite3.Connection.
    """

    _instance: Optional["DatabaseService"] = None

    def __new__(cls, db_path: Optional[str] = None) -> "DatabaseService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: Optional[str] = None) -> None:
        if getattr(self, "_initialized", False):
            return

        # Determinar la ruta de la base de datos (data/clock_data.db)
        base = Path(db_path) if db_path else Path("data") / "clock_data.db"
        base.parent.mkdir(parents=True, exist_ok=True)
        self.db_path: Path = base

        # Conectar a SQLite (check_same_thread=False permite uso desde hilos distintos si fuera necesario)
        self.conn: sqlite3.Connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        self._initialized = True

    def create_tables(self) -> None:
        """Crea las tablas necesarias en la base de datos.

        Crea la tabla `logs` con columnas: id (PK), timestamp y event_description.
        """

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
        """Inserta un registro en la tabla `logs`.

        Args:
            description: descripción del evento a almacenar.

        Returns:
            El id del registro insertado.
        """

        ts = datetime.utcnow().isoformat()
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO logs (timestamp, event_description) VALUES (?, ?)",
            (ts, description),
        )
        self.conn.commit()
        return cur.lastrowid

    def close(self) -> None:
        """Cierra la conexión a la base de datos."""

        try:
            self.conn.close()
        except Exception:
            pass
