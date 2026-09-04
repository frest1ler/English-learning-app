"""Оценка полезности грамматических упражнений."""

from datetime import datetime, timezone

CEFR_ORDER = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}


def exercise_priority(exercise, mastery=0.0, user_level='A2', recently_seen=False,
                      now=None, last_practiced_at=None):
    """Чем выше результат, тем полезнее упражнение показать сейчас."""
    now = now or datetime.now(timezone.utc)
    weakness = 1.0 - float(mastery)
    target = CEFR_ORDER.get(user_level, 2)
    level = CEFR_ORDER.get(exercise.get('cefr_level', 'A2'), 2)
    level_fit = max(0.0, 1.0 - abs(level - target) * 0.35)
    challenge = max(0.0, 1.0 - abs(float(exercise.get('difficulty', 0.5)) - 0.65))
    overdue = 1.0
    if last_practiced_at:
        try:
            practiced = datetime.fromisoformat(last_practiced_at)
            overdue = min(1.0, max(0.1, (now - practiced).days / 14))
        except (ValueError, TypeError):
            pass
    score = weakness * 0.50 + overdue * 0.25 + level_fit * 0.15 + challenge * 0.10
    if recently_seen:
        score *= 0.08
    return score


def select_adaptive(exercises, count, user_level='A2'):
    ranked = sorted(
        exercises,
        key=lambda item: exercise_priority(
            item, item.get('mastery', 0), user_level,
            bool(item.get('recently_seen')), last_practiced_at=item.get('last_practiced_at')),
        reverse=True,
    )
    # Сначала берём лучшие, но чередуем темы, чтобы тренировка не была монотонной.
    selected, topic_counts, type_counts = [], {}, {}
    while ranked and len(selected) < count:
        best_index = min(
            range(len(ranked)),
            key=lambda index: (topic_counts.get(ranked[index]['rule'], 0) * 2 +
                               type_counts.get(ranked[index].get('exercise_type', 'grammar_gap'), 0)) -
                              exercise_priority(ranked[index], ranked[index].get('mastery', 0), user_level,
                                                bool(ranked[index].get('recently_seen')),
                                                last_practiced_at=ranked[index].get('last_practiced_at')),
        )
        item = ranked.pop(best_index)
        selected.append(item)
        topic_counts[item['rule']] = topic_counts.get(item['rule'], 0) + 1
        kind = item.get('exercise_type', 'grammar_gap')
        type_counts[kind] = type_counts.get(kind, 0) + 1
    return selected
