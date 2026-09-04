import unittest

from learning.content_models import ContentValidationError
from llm.content_generator import ContentGenerator, TranslationEvaluator, validate_word


class FakeProvider:
    def __init__(self, payload): self.payload = payload
    def generate_json(self, prompt): return self.payload


class ContentGeneratorTests(unittest.TestCase):
    def test_valid_word_is_accepted(self):
        item = {'word':'deadline','translation':'срок','example':'Meet the deadline.',
                'example_translation':'Уложитесь в срок.','cefr_level':'B1'}
        result = validate_word(item, 'B1')
        self.assertEqual(result['word'], 'deadline')

    def test_duplicate_word_is_rejected(self):
        item = {'word':'deadline','translation':'срок','example':'Meet the deadline.',
                'example_translation':'Уложитесь в срок.'}
        with self.assertRaises(ContentValidationError): validate_word(item, 'B1', ['Deadline'])

    def test_generator_collects_invalid_items(self):
        provider = FakeProvider({'items':[{'word':'x'}]})
        _, valid, rejected = ContentGenerator(provider).generate_words('Work','A2',5)
        self.assertEqual(valid, []); self.assertEqual(len(rejected), 1)

    def test_exercise_generator_returns_valid_candidate(self):
        item = {'sentence':'I ___ here.','answer':'work','hint':'base form',
                'rule':'Present Simple','exercise_type':'grammar_gap',
                'cefr_level':'A1','difficulty':0.3,'required_features':['work']}
        _, valid, rejected = ContentGenerator(FakeProvider({'items':[item]})).generate_exercises(
            'Present Simple', 'A1', 1)
        self.assertEqual(len(valid), 1); self.assertEqual(rejected, [])

    def test_translation_evaluation_is_structured(self):
        provider = FakeProvider({'is_correct':True, 'explanation':'Верно',
                                 'suggested_answer':'She works.', 'grammar_errors':[]})
        result = TranslationEvaluator(provider).evaluate('Она работает.', 'She works.', 'She works.')
        self.assertTrue(result['is_correct'])

    def test_content_recommendation_is_structured(self):
        provider = FakeProvider({'vocabulary_topic':'Travel','grammar_topic':'Past Simple',
                                 'reason':'Нужна практика прошлого времени'})
        result = ContentGenerator(provider).recommend_content({'user_level':'A2'})
        self.assertEqual(result['grammar_topic'], 'Past Simple')
