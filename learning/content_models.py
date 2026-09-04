"""Единый формат и валидация расширяемого учебного контента."""

EXERCISE_TYPES = {
    'grammar_gap', 'translation_ru_en', 'find_tense',
    'correct_error', 'build_sentence',
}
CEFR_LEVELS = {'A1', 'A2', 'B1', 'B2', 'C1', 'C2'}


class ContentValidationError(ValueError):
    pass


def validate_exercise(item):
    result = dict(item)
    result.setdefault('exercise_type', 'grammar_gap')
    result.setdefault('hint', '')
    result.setdefault('cefr_level', 'A2')
    result.setdefault('difficulty', 0.5)
    result.setdefault('required_features', [])
    result.setdefault('source', 'built_in')
    required = ('sentence', 'answer', 'rule')
    if any(not str(result.get(field, '')).strip() for field in required):
        raise ContentValidationError('Упражнение должно содержать условие, ответ и тему')
    if result['exercise_type'] not in EXERCISE_TYPES:
        raise ContentValidationError('Неизвестный тип упражнения')
    if result['cefr_level'] not in CEFR_LEVELS:
        raise ContentValidationError('Неизвестный уровень CEFR')
    difficulty = float(result['difficulty'])
    if not 0 <= difficulty <= 1:
        raise ContentValidationError('Сложность должна быть от 0 до 1')
    result['difficulty'] = difficulty
    if isinstance(result['required_features'], str):
        result['required_features'] = [
            value.strip() for value in result['required_features'].split(',') if value.strip()]
    return result
