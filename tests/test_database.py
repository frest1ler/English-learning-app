import tempfile
import unittest
from pathlib import Path

from data.database import LearningDatabase


class LearningDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = LearningDatabase(Path(self.temp.name) / "test.db")
        self.words = [{'word': 'go', 'translation': 'идти', 'transcription': '[gəʊ]'}]
        self.exercises = {'Past Simple': [
            {'sentence': 'I ___ home', 'answer': 'went', 'hint': 'go → went'}
        ]}
        self.rules = [{'title': 'Past Simple', 'content': 'Прошедшее время'}]
        self.db.initialize(self.words, self.exercises, self.rules)

    def tearDown(self):
        self.temp.cleanup()

    def test_seed_is_idempotent(self):
        self.db.initialize(self.words, self.exercises, self.rules)
        self.assertEqual(len(self.db.get_words()), 1)
        self.assertEqual(len(self.db.get_exercises()['Past Simple']), 1)

    def test_duplicate_source_words_are_imported_once(self):
        duplicate = dict(self.words[0])
        with tempfile.TemporaryDirectory() as folder:
            database = LearningDatabase(Path(folder) / "duplicates.db")
            database.initialize([self.words[0], duplicate], {}, [])
            self.assertEqual(len(database.get_words()), 1)
            with database.connect() as connection:
                count = connection.execute(
                    "SELECT COUNT(*) FROM word_progress"
                ).fetchone()[0]
            self.assertEqual(count, 1)

    def test_add_word_and_record_answer(self):
        word_id = self.db.add_word({'word': 'learn', 'translation': 'учиться'})
        self.db.record_answer(activity_type='word_test', item_id=word_id,
                              prompt='learn', user_answer='учиться',
                              correct_answer='учиться', is_correct=True,
                              response_ms=1200)
        with self.db.connect() as connection:
            row = connection.execute("SELECT * FROM answer_history").fetchone()
        self.assertEqual(row['is_correct'], 1)
        self.assertEqual(row['response_ms'], 1200)

    def test_stats_and_reset(self):
        exercise = self.db.get_exercises()['Past Simple'][0]
        self.db.record_answer(activity_type='grammar', item_id=exercise['id'],
                              topic_id=exercise['topic_id'], prompt='test',
                              user_answer='went', correct_answer='went',
                              is_correct=True, response_ms=60000)
        stats = self.db.get_learning_stats()
        self.assertEqual(stats['overall']['attempts'], 1)
        self.assertEqual(stats['overall']['correct'], 1)
        self.assertGreater(stats['topics'][0]['mastery'], 0)
        self.db.reset_learning_progress()
        self.assertEqual(self.db.get_learning_stats()['overall']['attempts'], 0)

    def test_backup_contains_data(self):
        destination = Path(self.temp.name) / 'backup.db'
        self.db.backup_to(destination)
        backup = LearningDatabase(destination)
        self.assertEqual(len(backup.get_words()), 1)

    def test_legacy_progress_is_imported_once(self):
        self.db.import_legacy_progress(3, 5)
        self.db.import_legacy_progress(3, 5)
        stats = self.db.get_learning_stats()['overall']
        self.assertEqual(stats['attempts'], 5)
        self.assertEqual(stats['correct'], 3)


if __name__ == '__main__':
    unittest.main()
