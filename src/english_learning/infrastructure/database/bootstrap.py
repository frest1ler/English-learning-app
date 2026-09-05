"""Safely prepare a per-user database from bundled seed resources."""

import shutil
from pathlib import Path

from data.database import LearningDatabase
from data.loader import DataLoader

from ..paths import AppPaths
from .migrator import MigrationRunner


def bootstrap_database(paths: AppPaths, legacy_database: Path | None = None) -> LearningDatabase:
    paths.ensure_writable()
    if not paths.database.exists() and legacy_database and legacy_database.exists():
        shutil.copy2(legacy_database, paths.database)
    database = LearningDatabase(paths.database)
    database.initialize(
        DataLoader.load_words(paths.resources / "words.txt"),
        DataLoader.load_exercises(paths.resources / "exercises.txt"),
        DataLoader.load_rules(paths.resources / "rules.txt"),
    )
    migrations = Path(__file__).with_name("migrations")
    MigrationRunner(paths.database, paths.backup_dir, migrations).run()
    return database
