from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class SqliteDatabase:
    """Offline sqlite handle. No product or civic DDL in this story."""

    connection: sqlite3.Connection

    @classmethod
    def from_memory(cls) -> SqliteDatabase:
        """Open an in-process database. No DATABASE_URL / AppConfig field required."""
        connection = sqlite3.connect(":memory:", check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return cls(connection=connection)

    def healthcheck(self) -> bool:
        try:
            self.connection.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def close(self) -> None:
        self.connection.close()
