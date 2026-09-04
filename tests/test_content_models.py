import sqlite3
import tempfile
import unittest
from pathlib import Path

from data.database import LearningDatabase
from learning.content_models import ContentValidationError, validate_exercise


class ContentModelTests(unittest.TestCase):
    def test_defaults_create_universal_exercise(self):
        result = validate_exercise({'sentence': 'I ___', 'answer': 'work', 'rule': 'Present Simple'})
        self.assertEqual(result['exercise_type'], 'grammar_gap')
        self.assertEqual(result['source'], 'built_in')

    def test_unknown_type_is_rejected(self):
        with self.assertRaises(ContentValidationError):
            validate_exercise({'sentence': 'x', 'answer': 'x', 'rule': 'x',
                               'exercise_type': 'unknown'})

    def test_existing_database_is_migrated(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'old.db'
            connection = sqlite3.connect(path)
            connection.execute("CREATE TABLE exercises(id INTEGER PRIMARY KEY, topic_id INTEGER, sentence TEXT, answer TEXT, hint TEXT, difficulty REAL, cefr_level TEXT)")
            connection.commit(); connection.close()
            database = LearningDatabase(path)
            database.initialize([], {}, [])
            with database.connect() as connection:
                columns = {row['name'] for row in connection.execute('PRAGMA table_info(exercises)')}
            self.assertIn('exercise_type', columns)
            self.assertIn('required_features', columns)
