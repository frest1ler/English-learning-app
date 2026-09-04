"""Локальные провайдеры объяснений без внешних Python-зависимостей."""

import json
from urllib.error import URLError
from urllib.request import Request, urlopen


class LLMUnavailableError(RuntimeError):
    pass


class RuleBasedProvider:
    def explain_error(self, context):
        hint = context.get('hint') or 'Сравните форму глагола с указанным временем.'
        return {
            'error_type': context.get('error_type', 'grammar'),
            'explanation': hint,
            'rule': f"Правильный вариант: {context['correct_answer']}.",
            'example': context.get('sentence', ''),
            'mini_exercise': 'Составьте ещё одно предложение с правильной формой.',
            'source': 'Встроенное объяснение',
        }


class OllamaProvider:
    def __init__(self, model='qwen3:4b', base_url='http://127.0.0.1:11434', timeout=45):
        self.model, self.base_url, self.timeout = model, base_url.rstrip('/'), timeout

    def explain_error(self, context):
        prompt = (
            "Ты преподаватель английского для русскоязычного ученика. "
            "Кратко и точно объясни ошибку. Не придумывай отсутствующий контекст. "
            "Верни JSON с полями error_type, explanation, rule, example, mini_exercise.\n"
            f"Тема: {context.get('topic', '')}\nЗадание: {context.get('sentence', '')}\n"
            f"Ответ ученика: {context.get('user_answer', '')}\n"
            f"Правильный ответ: {context.get('correct_answer', '')}\n"
            f"Подсказка автора: {context.get('hint', '')}"
        )
        body = json.dumps({
            'model': self.model, 'messages': [{'role': 'user', 'content': prompt}],
            'stream': False, 'format': 'json', 'options': {'temperature': 0.2},
        }).encode('utf-8')
        request = Request(f'{self.base_url}/api/chat', data=body,
                          headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode('utf-8'))
            result = json.loads(payload['message']['content'])
        except (URLError, TimeoutError, OSError, KeyError, ValueError, json.JSONDecodeError) as error:
            raise LLMUnavailableError(str(error)) from error
        required = ('error_type', 'explanation', 'rule', 'example', 'mini_exercise')
        if not all(isinstance(result.get(key), str) for key in required):
            raise LLMUnavailableError('Модель вернула неполный ответ')
        result['source'] = f'Ollama · {self.model}'
        return result


class ExplanationService:
    def __init__(self, primary=None, fallback=None):
        self.primary = primary or OllamaProvider()
        self.fallback = fallback or RuleBasedProvider()

    def explain_error(self, context):
        try:
            return self.primary.explain_error(context)
        except LLMUnavailableError:
            return self.fallback.explain_error(context)
