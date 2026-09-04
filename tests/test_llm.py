import io
import json
import unittest
from unittest.mock import patch

from llm.providers import ExplanationService, LLMUnavailableError, OllamaProvider, RuleBasedProvider
from learning.error_analysis import classify_error


class FakeResponse(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()


class LLMTests(unittest.TestCase):
    def test_ollama_json_response(self):
        content = {key: 'value' for key in
                   ('error_type', 'explanation', 'rule', 'example', 'mini_exercise')}
        response = FakeResponse(json.dumps({'message': {'content': json.dumps(content)}}).encode())
        with patch('llm.providers.urlopen', return_value=response):
            result = OllamaProvider().explain_error({'correct_answer': 'went'})
        self.assertEqual(result['source'], 'Ollama · qwen3:4b')

    def test_service_falls_back(self):
        class Broken:
            def explain_error(self, context): raise LLMUnavailableError('offline')
        result = ExplanationService(Broken(), RuleBasedProvider()).explain_error(
            {'correct_answer': 'went', 'sentence': 'I went', 'error_type': 'verb'})
        self.assertEqual(result['source'], 'Встроенное объяснение')

    def test_error_classification(self):
        self.assertEqual(classify_error('Past Simple', 'goed', 'went'), 'Неправильный глагол')
