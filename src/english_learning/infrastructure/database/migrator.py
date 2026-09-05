"""Small transactional SQL migration runner with recovery backup."""

import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class MigrationRunner:
    def __init__(self, database: Path, backup_dir: Path, migrations_dir: Path):
        self.database = Path(database)
        self.backup_dir = Path(backup_dir)
        self.migrations_dir = Path(migrations_dir)

    def run(self) -> list[int]:
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup = None
        if self.database.exists() and self.database.stat().st_size:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            backup = self.backup_dir / f"learning-before-migration-{stamp}.db"
            shutil.copy2(self.database, backup)
        applied_now: list[int] = []
        connection = sqlite3.connect(self.database)
        try:
            connection.execute("""CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY, name TEXT NOT NULL, applied_at TEXT NOT NULL)""")
            applied = {row[0] for row in connection.execute("SELECT version FROM schema_migrations")}
            for path in sorted(self.migrations_dir.glob("*.sql")):
                version_text, _, name = path.stem.partition("_")
                version = int(version_text)
                if version in applied:
                    continue
                connection.executescript(path.read_text(encoding="utf-8"))
                connection.execute(
                    "INSERT INTO schema_migrations(version, name, applied_at) VALUES (?, ?, ?)",
                    (version, name, datetime.now(timezone.utc).isoformat(timespec="seconds")),
                )
                connection.commit()
                applied_now.append(version)
        except Exception:
            connection.close()
            if backup:
                shutil.copy2(backup, self.database)
            raise
        finally:
            try:
                connection.close()
            except sqlite3.Error:
                pass
        return applied_now
