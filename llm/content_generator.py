"""Генерация кандидатов с обязательной локальной проверкой."""

from learning.content_models import CEFR_LEVELS, ContentValidationError, validate_exercise


def validate_word(item, expected_level, existing_words=()):
    required = ('word', 'translation', 'example', 'example_translation')
    if any(not str(item.get(field, '')).strip() for field in required):
        raise ContentValidationError('У слова заполнены не все обязательные поля')
    word = item['word'].strip()
    if word.casefold() in {value.casefold() for value in existing_words}:
        raise ContentValidationError(f'Дубликат слова: {word}')
    if word.casefold() not in item['example'].casefold():
        raise ContentValidationError(f'Слово {word} отсутствует в примере')
    level = item.get('cefr_level', expected_level)
    if level not in CEFR_LEVELS:
        raise ContentValidationError('Неизвестный уровень CEFR')
    return {
        'word': word, 'translation': item['translation'].strip(),
        'transcription': item.get('transcription', '[требует проверки]').strip() or '[требует проверки]',
        'example': item['example'].strip(),
        'example_translation': item['example_translation'].strip(),
        'cefr_level': level, 'topic': item.get('topic', '').strip(),
    }


class ContentGenerator:
    def __init__(self, provider):
        self.provider = provider

    def generate_words(self, topic, level, count, existing_words=()):
        prompt = (
            f"Создай {count} английских слов уровня {level} по теме «{topic}» для русскоязычного ученика. "
            "Верни только JSON: {\"items\": [{\"word\": ..., \"translation\": ..., "
            "\"transcription\": ..., \"example\": ..., \"example_translation\": ..., "
            "\"cefr_level\": ..., \"topic\": ...}]}. Пример должен содержать само слово. "
            "Не используй имена собственные и не повторяй слова."
        )
        payload = self.provider.generate_json(prompt)
        items = payload.get('items')
        if not isinstance(items, list):
            raise ContentValidationError('Модель не вернула список items')
        valid, rejected, known = [], [], set(existing_words)
        for item in items[:count]:
            try:
                candidate = validate_word(item, level, known)
                valid.append(candidate); known.add(candidate['word'])
            except (ContentValidationError, AttributeError, TypeError) as error:
                rejected.append(str(error))
        return prompt, valid, rejected

    def generate_exercises(self, topic, level, count, exercise_type='grammar_gap'):
        prompt = (
            f"Создай {count} упражнений уровня {level} по теме {topic}, тип {exercise_type}. "
            "Верни JSON с массивом items. У каждого: sentence, answer, hint, rule, "
            "exercise_type, cefr_level, difficulty от 0 до 1, required_features."
        )
        payload = self.provider.generate_json(prompt)
        items = payload.get('items')
        if not isinstance(items, list):
            raise ContentValidationError('Модель не вернула список items')
        valid, rejected, seen = [], [], set()
        for item in items[:count]:
            try:
                candidate = validate_exercise(item)
                if candidate['exercise_type'] != exercise_type:
                    raise ContentValidationError('Тип упражнения не совпадает с запросом')
                if candidate['cefr_level'] != level:
                    raise ContentValidationError('Уровень упражнения не совпадает с запросом')
                key = (candidate['sentence'].casefold(), candidate['answer'].casefold())
                if key in seen: raise ContentValidationError('Дубликат упражнения')
                seen.add(key); valid.append(candidate)
            except (ContentValidationError, AttributeError, TypeError) as error:
                rejected.append(str(error))
        return prompt, valid, rejected

    def recommend_content(self, context):
        prompt = (
            "Выбери следующее полезное направление для русскоязычного ученика английского. "
            "Верни только JSON: vocabulary_topic, grammar_topic, reason. "
            "Не предлагай уровень выше чем на один CEFR шаг. Контекст: " + str(context)
        )
        result = self.provider.generate_json(prompt)
        required = ('vocabulary_topic', 'grammar_topic', 'reason')
        if not all(isinstance(result.get(key), str) and result[key].strip() for key in required):
            raise ContentValidationError('Qwen вернула неполную рекомендацию')
        return {key: result[key].strip() for key in required}


class TranslationEvaluator:
    def __init__(self, provider):
        self.provider = provider

    def evaluate(self, russian, user_answer, reference):
        prompt = (
            "Оцени перевод русского предложения на английский. Допускай естественные варианты, "
            "но не пропускай смысловые и грамматические ошибки. Верни только JSON с полями "
            "is_correct (boolean), explanation (string), suggested_answer (string), "
            "grammar_errors (array строк).\n"
            f"Русский текст: {russian}\nОтвет ученика: {user_answer}\nЭталон: {reference}"
        )
        result = self.provider.generate_json(prompt)
        if not isinstance(result.get('is_correct'), bool) or not isinstance(result.get('explanation'), str):
            raise ContentValidationError('Модель вернула некорректную оценку перевода')
        result.setdefault('suggested_answer', reference)
        result.setdefault('grammar_errors', [])
        return result
