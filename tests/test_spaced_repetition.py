import unittest
from datetime import datetime, timezone

from data.spaced_repetition import schedule_review


class SpacedRepetitionTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.progress = {'repetitions': 0, 'interval_days': 0, 'ease_factor': 2.5}

    def test_forgotten_word_returns_in_ten_minutes(self):
        result = schedule_review(self.progress, 0, self.now)
        self.assertEqual(result['repetitions'], 0)
        self.assertIn('2026-01-01T00:10:00', result['due_at'])

    def test_good_answers_increase_interval(self):
        first = schedule_review(self.progress, 2, self.now)
        second = schedule_review(first, 2, self.now)
        self.assertEqual(first['interval_days'], 1)
        self.assertEqual(second['interval_days'], 3)

    def test_invalid_rating_is_rejected(self):
        with self.assertRaises(ValueError):
            schedule_review(self.progress, 4, self.now)
