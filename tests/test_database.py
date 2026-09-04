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

    def test_translation_exercises_use_verified_examples(self):
        with self.db.connect() as connection:
            connection.execute("""UPDATE words SET example='I go home.',
                example_translation='Я иду домой.' WHERE word='go'""")
        exercise = self.db.get_translation_exercises()[0]
        self.assertEqual(exercise['sentence'], 'Я иду домой.')
        self.assertEqual(exercise['answer'], 'I go home.')
        self.assertEqual(exercise['exercise_type'], 'translation_ru_en')

    def test_material_search_filters_kind_and_level(self):
        words = self.db.search_materials('words', 'go', 'A2')
        self.assertEqual(len(words), 1)
        self.assertEqual(words[0]['kind'], 'word')
        exercises = self.db.search_materials('exercises', 'Past Simple', 'A2')
        self.assertEqual(len(exercises), 1)
        self.assertEqual(exercises[0]['kind'], 'exercise')

    def test_generated_exercise_requires_approval(self):
        item = {'sentence':'She ___ every day.','answer':'works','hint':'he/she/it',
                'rule':'Present Simple','exercise_type':'grammar_gap','cefr_level':'A1',
                'difficulty':0.4,'required_features':['works']}
        candidate_id = self.db.stage_generated('exercise', [item], 'qwen3:4b', 'prompt')[0]
        before = len(self.db.get_exercises().get('Present Simple', []))
        self.db.review_generated_exercise(candidate_id, True)
        after = len(self.db.get_exercises()['Present Simple'])
        self.assertEqual(after, before + 1)
        adaptive_ids = {row['id'] for row in self.db.get_adaptive_exercises(200)}
        with self.db.connect() as connection:
            generated_id = connection.execute(
                "SELECT id FROM exercises WHERE source='qwen'"
            ).fetchone()[0]
        self.assertIn(generated_id, adaptive_ids)

    def test_generated_word_is_linked_to_topic_after_approval(self):
        item = {'word':'deadline','translation':'срок','transcription':'[deadline]',
                'example':'Meet the deadline.','example_translation':'Уложитесь в срок.',
                'cefr_level':'B1','topic':'Work'}
        candidate_id = self.db.stage_generated('word', [item], 'qwen3:4b', 'prompt')[0]
        self.db.review_generated_word(candidate_id, True)
        with self.db.connect() as connection:
            link = connection.execute("""SELECT vt.title FROM word_topic_links l
                JOIN vocabulary_topics vt ON vt.id=l.topic_id
                JOIN words w ON w.id=l.word_id WHERE w.word='deadline'""").fetchone()
        self.assertEqual(link['title'], 'Work')

    def test_recommendation_context_contains_no_answer_text(self):
        context = self.db.get_recommendation_context()
        self.assertIn('weak_grammar_topics', context)
        self.assertNotIn('answer_history', context)


if __name__ == '__main__':
    unittest.main()
