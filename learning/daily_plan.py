"""Формирование компактного занятия на сегодня."""


def build_daily_plan(due_words, exercises, duration_minutes):
    if duration_minutes not in (5, 10, 15, 20):
        raise ValueError("Поддерживаются занятия на 5, 10, 15 или 20 минут")
    target = max(4, duration_minutes)
    word_count = min(len(due_words), max(2, round(target * 0.45)))
    exercise_count = min(len(exercises), target - word_count)
    return [
        *[{'kind': 'word', 'data': item} for item in due_words[:word_count]],
        *[{'kind': 'grammar', 'data': item} for item in exercises[:exercise_count]],
    ]
