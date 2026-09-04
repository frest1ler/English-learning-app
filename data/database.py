"""SQLite-хранилище учебных данных и прогресса."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from config import DATABASE_PATH
from data.spaced_repetition import schedule_review


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class LearningDatabase:
    """Единая точка доступа к локальной базе приложения."""

    def __init__(self, path=DATABASE_PATH):
        self.path = str(path)

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self, words=None, exercises=None, rules=None):
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY,
                    word TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    translation TEXT NOT NULL,
                    transcription TEXT NOT NULL DEFAULT '[...]',
                    example TEXT NOT NULL DEFAULT '',
                    example_translation TEXT NOT NULL DEFAULT '',
                    cefr_level TEXT NOT NULL DEFAULT 'A2',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS grammar_topics (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    content TEXT NOT NULL DEFAULT '',
                    cefr_level TEXT NOT NULL DEFAULT 'A2'
                );
                CREATE TABLE IF NOT EXISTS exercises (
                    id INTEGER PRIMARY KEY,
                    topic_id INTEGER NOT NULL REFERENCES grammar_topics(id),
                    sentence TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    hint TEXT NOT NULL DEFAULT '',
                    difficulty REAL NOT NULL DEFAULT 0.5,
                    cefr_level TEXT NOT NULL DEFAULT 'A2',
                    UNIQUE(topic_id, sentence, answer)
                );
                CREATE TABLE IF NOT EXISTS answer_history (
                    id INTEGER PRIMARY KEY,
                    activity_type TEXT NOT NULL,
                    item_id INTEGER,
                    topic_id INTEGER REFERENCES grammar_topics(id),
                    prompt TEXT NOT NULL,
                    user_answer TEXT NOT NULL,
                    correct_answer TEXT NOT NULL,
                    is_correct INTEGER NOT NULL,
                    response_ms INTEGER,
                    hint_used INTEGER NOT NULL DEFAULT 0,
                    error_type TEXT,
                    session_id TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_history_created ON answer_history(created_at);
                CREATE INDEX IF NOT EXISTS idx_history_topic ON answer_history(topic_id);
                CREATE TABLE IF NOT EXISTS word_progress (
                    word_id INTEGER PRIMARY KEY REFERENCES words(id) ON DELETE CASCADE,
                    status TEXT NOT NULL DEFAULT 'new',
                    repetitions INTEGER NOT NULL DEFAULT 0,
                    interval_days INTEGER NOT NULL DEFAULT 0,
                    ease_factor REAL NOT NULL DEFAULT 2.5,
                    correct_count INTEGER NOT NULL DEFAULT 0,
                    incorrect_count INTEGER NOT NULL DEFAULT 0,
                    due_at TEXT NOT NULL,
                    last_reviewed_at TEXT
                );
                CREATE TABLE IF NOT EXISTS topic_progress (
                    topic_id INTEGER PRIMARY KEY REFERENCES grammar_topics(id) ON DELETE CASCADE,
                    mastery REAL NOT NULL DEFAULT 0,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    correct INTEGER NOT NULL DEFAULT 0,
                    last_practiced_at TEXT
                );
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id TEXT PRIMARY KEY,
                    session_type TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    duration_seconds INTEGER NOT NULL DEFAULT 0,
                    answers_count INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)
        self._seed(words or [], exercises or {}, rules or [])

    def _seed(self, words, exercises, rules):
        now = utc_now()

        def topic_key(title):
            key = ' '.join(title.casefold().split()).replace(' и ', ' and ')
            return key.removesuffix(' sentences')

        def topic_level(title):
            key = topic_key(title)
            return {
                'present simple': 'A1', 'past simple': 'A2', 'future simple': 'A2',
                'present continuous': 'A1', 'past continuous': 'B1',
                'present perfect': 'B1', 'gerund and infinitive': 'B1',
                'conditional': 'B1', 'modals for deduction': 'B2',
            }.get(key, 'A2')

        with self.connect() as db:
            if db.execute("SELECT COUNT(*) FROM words").fetchone()[0] == 0:
                for item in words:
                    cursor = db.execute(
                        """INSERT OR IGNORE INTO words
                           (word, translation, transcription, example, example_translation, created_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (item['word'], item['translation'], item.get('transcription', '[...]'),
                         item.get('example', ''), item.get('example_translation', ''), now),
                    )
                    if cursor.rowcount:
                        db.execute("INSERT INTO word_progress(word_id, due_at) VALUES (?, ?)",
                                   (cursor.lastrowid, now))

            if db.execute("SELECT COUNT(*) FROM grammar_topics").fetchone()[0] == 0:
                contents = {topic_key(item['title']): item['content'] for item in rules}
                titles_by_key = {topic_key(title): title for title in exercises}
                for item in rules:
                    titles_by_key.setdefault(topic_key(item['title']), item['title'])
                titles = list(titles_by_key.values())
                for title in titles:
                    cursor = db.execute(
                        "INSERT INTO grammar_topics(title, content, cefr_level) VALUES (?, ?, ?)",
                        (title, contents.get(topic_key(title), ''), topic_level(title)),
                    )
                    topic_id = cursor.lastrowid
                    db.execute("INSERT INTO topic_progress(topic_id) VALUES (?)", (topic_id,))
                    source_exercises = next(
                        (items for name, items in exercises.items()
                         if topic_key(name) == topic_key(title)), []
                    )
                    total = max(1, len(source_exercises) - 1)
                    for index, item in enumerate(source_exercises):
                        db.execute(
                            """INSERT OR IGNORE INTO exercises
                               (topic_id, sentence, answer, hint, difficulty, cefr_level)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (topic_id, item['sentence'], item['answer'], item.get('hint', ''),
                             round(0.25 + 0.55 * index / total, 2), topic_level(title)),
                        )

    @staticmethod
    def _rows(rows):
        return [dict(row) for row in rows]

    def get_words(self):
        with self.connect() as db:
            return self._rows(db.execute("SELECT * FROM words ORDER BY id"))

    def add_word(self, item):
        now = utc_now()
        with self.connect() as db:
            cursor = db.execute(
                """INSERT INTO words(word, translation, transcription, example,
                   example_translation, created_at) VALUES (?, ?, ?, ?, ?, ?)""",
                (item['word'], item['translation'], item.get('transcription', '[...]'),
                 item.get('example', ''), item.get('example_translation', ''), now),
            )
            db.execute("INSERT INTO word_progress(word_id, due_at) VALUES (?, ?)",
                       (cursor.lastrowid, now))
            return cursor.lastrowid

    def get_due_words(self, limit=50, include_new=True):
        now = utc_now()
        condition = "p.due_at <= ?" if include_new else "p.due_at <= ? AND p.status != 'new'"
        with self.connect() as db:
            return self._rows(db.execute(f"""SELECT w.*, p.status, p.repetitions,
                p.interval_days, p.ease_factor, p.due_at FROM words w
                JOIN word_progress p ON p.word_id = w.id
                WHERE {condition} ORDER BY p.due_at, w.id LIMIT ?""", (now, limit)))

    def review_word(self, word_id, rating):
        with self.connect() as db:
            row = db.execute("SELECT * FROM word_progress WHERE word_id = ?", (word_id,)).fetchone()
            if not row:
                raise ValueError("Слово не найдено в прогрессе")
            result = schedule_review(dict(row), rating)
            db.execute("""UPDATE word_progress SET status=?, repetitions=?, interval_days=?,
                ease_factor=?, due_at=?, last_reviewed_at=?,
                correct_count=correct_count+?, incorrect_count=incorrect_count+?
                WHERE word_id=?""", (
                result['status'], result['repetitions'], result['interval_days'],
                result['ease_factor'], result['due_at'], result['last_reviewed_at'],
                int(rating >= 2), int(rating < 2), word_id,
            ))
        return result

    def get_word_progress_summary(self):
        with self.connect() as db:
            rows = db.execute("SELECT status, COUNT(*) count FROM word_progress GROUP BY status").fetchall()
            due = db.execute("SELECT COUNT(*) FROM word_progress WHERE due_at <= ?", (utc_now(),)).fetchone()[0]
        result = {'new': 0, 'learning': 0, 'mastered': 0, 'due': due}
        result.update({row['status']: row['count'] for row in rows})
        return result

    def get_learning_stats(self):
        with self.connect() as db:
            overall = dict(db.execute("""SELECT COUNT(*) attempts,
                COALESCE(SUM(is_correct), 0) correct,
                COALESCE(SUM(response_ms), 0) response_ms,
                COUNT(DISTINCT substr(created_at, 1, 10)) study_days
                FROM answer_history""").fetchone())
            periods = {}
            for days in (7, 30):
                row = db.execute("""SELECT COUNT(*) attempts,
                    COALESCE(SUM(is_correct), 0) correct FROM answer_history
                    WHERE datetime(created_at) >= datetime('now', ?)""",
                    (f'-{days} days',)).fetchone()
                periods[days] = dict(row)
            topics = self._rows(db.execute("""SELECT t.title, p.mastery, p.attempts,
                p.correct, p.last_practiced_at FROM grammar_topics t
                JOIN topic_progress p ON p.topic_id=t.id
                ORDER BY p.mastery, p.attempts DESC, t.title"""))
            errors = self._rows(db.execute("""SELECT COALESCE(error_type, 'Не классифицирована') error_type,
                COUNT(*) count FROM answer_history WHERE is_correct=0
                GROUP BY COALESCE(error_type, 'Не классифицирована') ORDER BY count DESC LIMIT 5"""))
        return {'overall': overall, 'periods': periods, 'topics': topics,
                'errors': errors, 'words': self.get_word_progress_summary()}

    def reset_learning_progress(self):
        now = utc_now()
        with self.connect() as db:
            db.execute("DELETE FROM answer_history")
            db.execute("DELETE FROM study_sessions")
            db.execute("""UPDATE word_progress SET status='new', repetitions=0,
                interval_days=0, ease_factor=2.5, correct_count=0,
                incorrect_count=0, due_at=?, last_reviewed_at=NULL""", (now,))
            db.execute("""UPDATE topic_progress SET mastery=0, attempts=0,
                correct=0, last_practiced_at=NULL""")

    def start_session(self, session_id, session_type='daily'):
        with self.connect() as db:
            db.execute("""INSERT INTO study_sessions(id, session_type, started_at)
                VALUES (?, ?, ?)""", (session_id, session_type, utc_now()))

    def finish_session(self, session_id, duration_seconds, answers_count):
        with self.connect() as db:
            db.execute("""UPDATE study_sessions SET ended_at=?, duration_seconds=?,
                answers_count=? WHERE id=?""",
                (utc_now(), duration_seconds, answers_count, session_id))

    def get_session_summary(self):
        with self.connect() as db:
            row = db.execute("""SELECT COUNT(*) sessions,
                COALESCE(SUM(duration_seconds), 0) duration_seconds,
                COALESCE(SUM(answers_count), 0) answers FROM study_sessions
                WHERE ended_at IS NOT NULL""").fetchone()
        return dict(row)

    def backup_to(self, destination):
        """Создать согласованную резервную копию даже при открытой базе."""
        source = sqlite3.connect(self.path)
        target = sqlite3.connect(str(destination))
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()

    def get_rules(self):
        with self.connect() as db:
            return self._rows(db.execute(
                "SELECT id, title, content, cefr_level FROM grammar_topics ORDER BY id"))

    def get_exercises(self):
        with self.connect() as db:
            rows = self._rows(db.execute("""
                SELECT e.*, t.title AS rule FROM exercises e
                JOIN grammar_topics t ON t.id = e.topic_id ORDER BY e.id
            """))
        result = {}
        for row in rows:
            result.setdefault(row['rule'], []).append(row)
        return result

    def get_adaptive_exercises(self, count=10, user_level='A2'):
        from learning.adaptive import select_adaptive
        with self.connect() as db:
            rows = self._rows(db.execute("""SELECT e.*, t.title AS rule,
                p.mastery, p.last_practiced_at,
                CASE WHEN e.id IN (
                    SELECT item_id FROM answer_history WHERE activity_type='grammar'
                    ORDER BY id DESC LIMIT 30
                ) THEN 1 ELSE 0 END recently_seen
                FROM exercises e JOIN grammar_topics t ON t.id=e.topic_id
                JOIN topic_progress p ON p.topic_id=t.id"""))
        return select_adaptive(rows, min(count, len(rows)), user_level)

    def get_diagnostic_questions(self):
        questions = []
        with self.connect() as db:
            exercises = self._rows(db.execute("""SELECT e.*, t.title rule
                FROM exercises e JOIN grammar_topics t ON t.id=e.topic_id
                WHERE e.id IN (SELECT MIN(e2.id) FROM exercises e2 GROUP BY e2.topic_id,
                    CAST(e2.difficulty * 4 AS INTEGER)) ORDER BY e.cefr_level, e.difficulty"""))
            words = self._rows(db.execute("SELECT * FROM words ORDER BY id LIMIT 20"))
        for item in exercises:
            questions.append({
                'key': f"g:{item['id']}", 'skill': item['rule'],
                'prompt': item['sentence'], 'answer': item['answer'],
                'cefr_level': item['cefr_level'], 'difficulty': item['difficulty'],
                'item_id': item['id'], 'topic_id': item['topic_id'],
            })
        for index, item in enumerate(words):
            questions.append({
                'key': f"w:{item['id']}", 'skill': 'Словарный запас',
                'prompt': f"Переведите на русский: {item['word']}",
                'answer': item['translation'], 'cefr_level': item['cefr_level'],
                'difficulty': 0.3 + index / max(1, len(words)) * 0.5,
                'item_id': item['id'], 'topic_id': None,
            })
        return questions

    def record_answer(self, **data):
        with self.connect() as db:
            db.execute("""INSERT INTO answer_history
                (activity_type, item_id, topic_id, prompt, user_answer, correct_answer,
                 is_correct, response_ms, hint_used, error_type, session_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                data['activity_type'], data.get('item_id'), data.get('topic_id'),
                data.get('prompt', ''), data.get('user_answer', ''),
                data.get('correct_answer', ''), int(data.get('is_correct', False)),
                data.get('response_ms'), int(data.get('hint_used', False)),
                data.get('error_type'), data.get('session_id'), utc_now(),
            ))
            if data.get('topic_id'):
                db.execute("""UPDATE topic_progress SET attempts = attempts + 1,
                    correct = correct + ?,
                    mastery = MIN(1.0, MAX(0.0, mastery * 0.75 + ? * 0.25)),
                    last_practiced_at = ? WHERE topic_id = ?""",
                    (int(data.get('is_correct', False)),
                     1.0 if data.get('is_correct') else 0.0, utc_now(), data['topic_id']))

    def import_legacy_progress(self, score, total_attempts):
        """Однократно сохранить старые суммарные счётчики без выдуманных деталей."""
        score = max(0, min(int(score), int(total_attempts)))
        total_attempts = max(0, int(total_attempts))
        if not total_attempts or self.get_setting('legacy_progress_imported', False):
            return
        with self.connect() as db:
            if db.execute("SELECT COUNT(*) FROM answer_history").fetchone()[0] == 0:
                rows = []
                for index in range(total_attempts):
                    rows.append(('legacy', 'Старый прогресс', '', '', int(index < score), utc_now()))
                db.executemany("""INSERT INTO answer_history
                    (activity_type, prompt, user_answer, correct_answer, is_correct, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)""", rows)
        self.set_setting('legacy_progress_imported', True)

    def get_setting(self, key, default=None):
        with self.connect() as db:
            row = db.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return json.loads(row['value']) if row else default

    def set_setting(self, key, value):
        with self.connect() as db:
            db.execute("""INSERT INTO settings(key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
                (key, json.dumps(value, ensure_ascii=False)))
