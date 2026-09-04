"""Адаптивная входная диагностика без обращения к LLM."""

from collections import defaultdict

from learning.adaptive import CEFR_ORDER

LEVELS = ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')


class DiagnosticEngine:
    def __init__(self, questions, limit=30):
        self.questions = list(questions)
        self.limit = min(limit, len(self.questions))
        self.ability = 2.0
        self.results = []
        self.seen = set()

    def next_question(self):
        if len(self.results) >= self.limit:
            return None
        candidates = [item for item in self.questions if item['key'] not in self.seen]
        if not candidates:
            return None
        item = min(candidates, key=lambda question: (
            abs(CEFR_ORDER.get(question.get('cefr_level', 'A2'), 2) - self.ability),
            abs(question.get('difficulty', 0.5) - 0.55), question['key']))
        self.seen.add(item['key'])
        return item

    def submit(self, question, is_correct):
        self.results.append({**question, 'is_correct': bool(is_correct)})
        self.ability = min(6.0, max(1.0, self.ability + (0.28 if is_correct else -0.22)))

    def summary(self):
        groups = defaultdict(lambda: {'correct': 0, 'attempts': 0})
        for result in self.results:
            group = groups[result.get('skill', 'grammar')]
            group['attempts'] += 1
            group['correct'] += int(result['is_correct'])
        level = LEVELS[min(len(LEVELS) - 1, max(0, round(self.ability) - 1))]
        return {'estimated_level': level, 'ability': round(self.ability, 2),
                'answers': len(self.results), 'skills': dict(groups)}
