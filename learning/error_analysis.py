"""Быстрая локальная классификация распространённых ошибок."""


def classify_error(topic, user_answer, correct_answer):
    user, correct = user_answer.lower().strip(), correct_answer.lower().strip()
    if user == correct:
        return None
    if topic == 'Present Simple' and correct.endswith(('s', 'es', 'ies')):
        return 'Окончание -s в Present Simple'
    if topic == 'Past Simple' and not correct.endswith('ed'):
        return 'Неправильный глагол'
    if topic == 'Present Perfect' and ('have' in correct or 'has' in correct):
        return 'Форма Present Perfect'
    if 'ing' in correct:
        return 'Форма -ing'
    if any(value in correct.split() for value in ('will', 'would', 'could', 'might', 'must')):
        return 'Модальный или вспомогательный глагол'
    return 'Грамматическая форма'
