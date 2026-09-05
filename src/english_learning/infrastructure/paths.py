"""Read-only resource and writable per-user application paths."""

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from platformdirs import PlatformDirs


APP_NAME = "EnglishLearningApp"
APP_AUTHOR = "EnglishLearningApp"


@dataclass(frozen=True)
class AppPaths:
    data_dir: Path
    state_dir: Path
    log_dir: Path
    backup_dir: Path
    database: Path
    resources: Path

    @classmethod
    def discover(cls) -> "AppPaths":
        override = os.environ.get("ENGLISH_LEARNING_DATA_DIR")
        dirs = PlatformDirs(APP_NAME, APP_AUTHOR, roaming=False)
        data_dir = Path(override).expanduser().resolve() if override else Path(dirs.user_data_path)
        state_dir = data_dir if override else Path(dirs.user_state_path)
        resource_override = os.environ.get("ENGLISH_LEARNING_RESOURCE_DIR")
        if resource_override:
            resources = Path(resource_override).expanduser().resolve()
        elif getattr(sys, "frozen", False):
            resources = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)) / "resources" / "seed"
        else:
            resources = Path(__file__).resolve().parents[3] / "data_files"
        return cls(
            data_dir=data_dir,
            state_dir=state_dir,
            log_dir=state_dir / "logs",
            backup_dir=data_dir / "backups",
            database=data_dir / "learning.db",
            resources=resources,
        )

    def ensure_writable(self) -> None:
        for directory in (self.data_dir, self.state_dir, self.log_dir, self.backup_dir):
            directory.mkdir(parents=True, exist_ok=True)
