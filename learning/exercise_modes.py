"""Правила представления упражнений в разных режимах."""


def topic_text(topic, show_topic, answered=False):
    if show_topic or answered:
        prefix = '📌 Тема' if show_topic else '✅ Использованная тема'
        return f'{prefix}: {topic}'
    return 'Определите грамматическое время самостоятельно'


def instruction_for_type(exercise_type):
    return {
        'grammar_gap': 'Поставьте слово в правильную форму:',
        'translation_ru_en': 'Переведите предложение на английский:',
        'find_tense': 'Определите грамматическое время:',
        'correct_error': 'Исправьте ошибку в предложении:',
        'build_sentence': 'Составьте правильное предложение:',
    }.get(exercise_type, 'Выполните задание:')
