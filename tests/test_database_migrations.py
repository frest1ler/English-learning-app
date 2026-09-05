import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.english_learning.infrastructure.database.migrator import MigrationRunner


class MigrationRunnerTests(unittest.TestCase):
    def test_migrations_are_applied_once(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); database = root / "app.db"; migrations = root / "migrations"
            migrations.mkdir(); (migrations / "001_create.sql").write_text(
                "CREATE TABLE example(id INTEGER PRIMARY KEY);", encoding="utf-8")
            runner = MigrationRunner(database, root / "backups", migrations)
            self.assertEqual(runner.run(), [1])
            self.assertEqual(runner.run(), [])

    def test_failed_migration_restores_database(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); database = root / "app.db"; migrations = root / "migrations"
            connection = sqlite3.connect(database)
            connection.execute("CREATE TABLE preserved(value TEXT)")
            connection.execute("INSERT INTO preserved VALUES ('safe')")
            connection.commit(); connection.close()
            migrations.mkdir(); (migrations / "001_broken.sql").write_text(
                "CREATE TABLE partial(id INTEGER); INVALID SQL;", encoding="utf-8")
            with self.assertRaises(sqlite3.Error):
                MigrationRunner(database, root / "backups", migrations).run()
            connection = sqlite3.connect(database)
            value = connection.execute("SELECT value FROM preserved").fetchone()[0]
            partial = connection.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE name='partial'").fetchone()[0]
            connection.close()
            self.assertEqual(value, 'safe')
            self.assertEqual(partial, 0)
