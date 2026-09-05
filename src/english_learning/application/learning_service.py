"""UI-facing use cases; presentation never executes SQL directly."""

import random
import uuid
from pathlib import Path

from data.database import LearningDatabase
from learning.daily_plan import build_daily_plan
from utils.helpers import check_answer_match


class LearningService:
    def __init__(self, database: LearningDatabase):
        self.database = database

    def dashboard(self):
        return {
            "words": self.database.get_word_progress_summary(),
            "sessions": self.database.get_session_summary(),
            "level": self.database.get_setting("user_level", "A2"),
        }

    def daily_plan(self, minutes: int):
        words = self.database.get_due_words(limit=minutes)
        exercises = self.database.get_adaptive_exercises(
            minutes, self.database.get_setting("user_level", "A2")
        )
        return build_daily_plan(words, exercises, minutes)

    def words(self, search: str = ""):
        words = self.database.get_words()
        term = search.casefold().strip()
        return [item for item in words if not term or term in item["word"].casefold()
                or term in item["translation"].casefold()]

    def add_word(self, item):
        return self.database.add_word(item)

    def due_words(self):
        return self.database.get_due_words()

    def review_word(self, word_id: int, rating: int):
        return self.database.review_word(word_id, rating)

    def exercises(self, topic: str | None = None, mode: str = "grammar"):
        if mode == "translation":
            result = self.database.get_translation_exercises()
        else:
            groups = self.database.get_exercises()
            result = list(groups.get(topic, [])) if topic else [x for values in groups.values() for x in values]
        random.shuffle(result)
        return result

    def topics(self):
        return list(self.database.get_exercises())

    def rules(self):
        return self.database.get_rules()

    def materials(self, kind="all", search="", level="all"):
        return self.database.search_materials(kind, search, level)

    def stats(self):
        return self.database.get_learning_stats()

    def setting(self, key, default=None):
        return self.database.get_setting(key, default)

    def save_setting(self, key, value):
        self.database.set_setting(key, value)

    def backup(self, destination: Path):
        self.database.backup_to(destination)

    @staticmethod
    def answer_matches(user_answer, correct_answer):
        return check_answer_match(user_answer, correct_answer)
