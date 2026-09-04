import unittest

from learning.daily_plan import build_daily_plan


class DailyPlanTests(unittest.TestCase):
    def test_words_come_before_grammar(self):
        plan = build_daily_plan([{'id': 1}, {'id': 2}], [{'id': 3}], 5)
        self.assertEqual([item['kind'] for item in plan], ['word', 'word', 'grammar'])

    def test_invalid_duration_is_rejected(self):
        with self.assertRaises(ValueError):
            build_daily_plan([], [], 12)
