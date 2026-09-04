import unittest

from learning.exercise_modes import instruction_for_type, topic_text


class ExerciseModeTests(unittest.TestCase):
    def test_hidden_topic_is_not_leaked_before_answer(self):
        self.assertNotIn('Past Simple', topic_text('Past Simple', False, False))

    def test_hidden_topic_is_revealed_after_answer(self):
        self.assertIn('Past Simple', topic_text('Past Simple', False, True))

    def test_visible_topic_is_shown_immediately(self):
        self.assertIn('Past Simple', topic_text('Past Simple', True, False))

    def test_translation_has_specific_instruction(self):
        self.assertIn('Переведите', instruction_for_type('translation_ru_en'))
