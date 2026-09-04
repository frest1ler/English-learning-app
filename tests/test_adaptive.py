import unittest

from learning.adaptive import exercise_priority, select_adaptive


class AdaptiveSelectionTests(unittest.TestCase):
    def test_weak_topic_has_higher_priority(self):
        exercise = {'cefr_level': 'A2', 'difficulty': 0.6}
        weak = exercise_priority(exercise, mastery=0.1)
        strong = exercise_priority(exercise, mastery=0.9)
        self.assertGreater(weak, strong)

    def test_recent_exercise_is_penalized(self):
        exercise = {'cefr_level': 'A2', 'difficulty': 0.6}
        fresh = exercise_priority(exercise)
        recent = exercise_priority(exercise, recently_seen=True)
        self.assertGreater(fresh, recent)

    def test_selection_respects_count(self):
        items = [
            {'id': index, 'rule': f'Topic {index % 2}', 'mastery': index / 10,
             'cefr_level': 'A2', 'difficulty': 0.5}
            for index in range(10)
        ]
        self.assertEqual(len(select_adaptive(items, 4)), 4)
