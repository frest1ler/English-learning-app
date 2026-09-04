"""Предсказуемый алгоритм интервального повторения слов."""

from datetime import datetime, timedelta, timezone


def schedule_review(progress, rating, now=None):
    """Вернуть новые параметры повторения для оценки 0..3."""
    if rating not in (0, 1, 2, 3):
        raise ValueError("Оценка повторения должна быть от 0 до 3")
    now = now or datetime.now(timezone.utc)
    repetitions = int(progress.get('repetitions', 0))
    interval = int(progress.get('interval_days', 0))
    ease = float(progress.get('ease_factor', 2.5))

    if rating == 0:
        repetitions, interval, ease = 0, 0, max(1.3, ease - 0.2)
        due = now + timedelta(minutes=10)
    elif rating == 1:
        repetitions += 1
        interval = max(1, round(max(interval, 1) * 1.2))
        ease = max(1.3, ease - 0.15)
        due = now + timedelta(days=interval)
    elif rating == 2:
        repetitions += 1
        interval = 1 if repetitions == 1 else 3 if repetitions == 2 else max(4, round(interval * ease))
        due = now + timedelta(days=interval)
    else:
        repetitions += 1
        interval = 3 if repetitions == 1 else 7 if repetitions == 2 else max(8, round(interval * ease * 1.3))
        ease = min(3.0, ease + 0.1)
        due = now + timedelta(days=interval)

    status = 'mastered' if repetitions >= 5 and interval >= 21 else 'learning'
    return {
        'status': status,
        'repetitions': repetitions,
        'interval_days': interval,
        'ease_factor': ease,
        'due_at': due.isoformat(timespec='seconds'),
        'last_reviewed_at': now.isoformat(timespec='seconds'),
    }
