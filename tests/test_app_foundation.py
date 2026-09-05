import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.english_learning.infrastructure.paths import AppPaths
from src.english_learning.infrastructure.settings import AppConfig


class AppFoundationTests(unittest.TestCase):
    def test_data_directory_override_is_writable(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict(os.environ, {"ENGLISH_LEARNING_DATA_DIR": folder}):
                paths = AppPaths.discover()
                paths.ensure_writable()
            self.assertEqual(paths.database, Path(folder).resolve() / "learning.db")
            self.assertTrue(paths.backup_dir.is_dir())
            self.assertTrue(paths.log_dir.is_dir())

    def test_environment_config(self):
        values = {
            "ENGLISH_LEARNING_OLLAMA_URL": "http://ollama:11434/",
            "ENGLISH_LEARNING_OLLAMA_MODEL": "qwen3:8b",
            "ENGLISH_LEARNING_LOG_LEVEL": "debug",
        }
        with patch.dict(os.environ, values):
            config = AppConfig.from_environment()
        self.assertEqual(config.ollama_url, "http://ollama:11434")
        self.assertEqual(config.ollama_model, "qwen3:8b")
        self.assertEqual(config.log_level, "DEBUG")
