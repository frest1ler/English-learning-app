import unittest

from learning.diagnostic import DiagnosticEngine


class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.questions = [
            {'key': str(index), 'skill': 'grammar', 'cefr_level': level,
             'difficulty': 0.5, 'answer': 'x', 'prompt': 'x'}
            for index, level in enumerate(('A1', 'A2', 'B1', 'B2', 'C1', 'C2'))
        ]

    def test_correct_answers_raise_level(self):
        engine = DiagnosticEngine(self.questions, 4)
        for _ in range(4):
            question = engine.next_question(); engine.submit(question, True)
        self.assertIn(engine.summary()['estimated_level'], ('B1', 'B2'))

    def test_question_is_not_repeated(self):
        engine = DiagnosticEngine(self.questions, 3)
        keys = []
        for _ in range(3):
            question = engine.next_question(); keys.append(question['key']); engine.submit(question, True)
        self.assertEqual(len(keys), len(set(keys)))
