"""Последовательная сессия слов и адаптивной грамматики."""

import time
import tkinter as tk
import uuid
from tkinter import messagebox

from config import COLORS, FONTS
from learning.daily_plan import build_daily_plan
from utils.helpers import check_answer_match, format_correct_answer


class DailyLessonWindow:
    def __init__(self, parent, app, duration_minutes, on_finish=None):
        self.app = app
        self.on_finish = on_finish
        self.session_id = str(uuid.uuid4())
        self.started_at = time.monotonic()
        words = app.db.get_due_words(limit=duration_minutes)
        exercises = app.db.get_adaptive_exercises(duration_minutes, app.db.get_setting('user_level', 'A2'))
        self.tasks = build_daily_plan(words, exercises, duration_minutes)
        self.index = 0
        self.answers = 0
        self.revealed = False
        self.answer_checked = False
        app.db.start_session(self.session_id)

        self.window = tk.Toplevel(parent)
        self.window.title("Занятие на сегодня")
        self.window.geometry("720x560")
        self.window.configure(bg=COLORS['light'])
        self.window.protocol('WM_DELETE_WINDOW', self.finish)
        self.progress = tk.Label(self.window, bg=COLORS['light'], font=FONTS['normal'])
        self.progress.pack(pady=15)
        self.title = tk.Label(self.window, bg='white', fg=COLORS['dark'],
                              font=FONTS['title'], wraplength=650)
        self.title.pack(fill='both', expand=True, padx=25, pady=10)
        self.detail = tk.Label(self.window, bg='white', fg=COLORS['success'],
                               font=FONTS['normal'], wraplength=650)
        self.detail.pack(fill='x', padx=25, pady=8)
        self.entry = tk.Entry(self.window, font=FONTS['input'], justify='center')
        self.entry.bind('<Return>', lambda event: self.submit())
        self.action = tk.Button(self.window, font=FONTS['normal'], bg=COLORS['primary'],
                                fg='white', padx=20, pady=8, command=self.submit)
        self.rating = tk.Frame(self.window, bg=COLORS['light'])
        for value, text, color in ((0, 'Не помню', COLORS['danger']), (1, 'Трудно', COLORS['warning']),
                                   (2, 'Нормально', COLORS['primary']), (3, 'Легко', COLORS['success'])):
            tk.Button(self.rating, text=text, bg=color, fg='white',
                      command=lambda rating=value: self.rate_word(rating)).pack(side='left', padx=4)
        self.show_task()

    def show_task(self):
        self.entry.pack_forget(); self.action.pack_forget(); self.rating.pack_forget()
        self.detail.config(text='')
        if self.index >= len(self.tasks):
            self.finish()
            return
        task = self.tasks[self.index]
        item = task['data']
        self.progress.config(text=f"Задание {self.index + 1} из {len(self.tasks)}")
        self.revealed = self.answer_checked = False
        if task['kind'] == 'word':
            self.title.config(text=f"Вспомните перевод:\n\n{item['word']}  {item['transcription']}")
            self.action.config(text='Показать ответ')
        else:
            self.title.config(text=f"{item['rule']}\n\n{item['sentence']}")
            self.entry.delete(0, tk.END); self.entry.pack(pady=10); self.entry.focus()
            self.action.config(text='Проверить')
        self.action.pack(pady=12)

    def submit(self):
        task = self.tasks[self.index]
        item = task['data']
        if task['kind'] == 'word':
            if self.revealed:
                return
            self.revealed = True
            self.detail.config(text=f"{item['translation']}\n{item.get('example', '')}")
            self.action.pack_forget(); self.rating.pack(pady=12)
            return
        if self.answer_checked:
            self.index += 1; self.show_task(); return
        answer = self.entry.get().strip()
        if not answer:
            return
        correct = check_answer_match(answer, item['answer'])
        self.answer_checked = True; self.answers += 1
        from learning.error_analysis import classify_error
        error_type = None if correct else classify_error(item['rule'], answer, item['answer'])
        self.app.db.record_answer(
            activity_type='grammar', item_id=item['id'], topic_id=item['topic_id'],
            prompt=item['sentence'], user_answer=answer, correct_answer=item['answer'],
            is_correct=correct, error_type=error_type, session_id=self.session_id)
        self.detail.config(text=('✅ Правильно' if correct else
                           f"❌ Правильный ответ: {format_correct_answer(item['answer'])}"))
        self.action.config(text='Далее')

    def rate_word(self, rating):
        item = self.tasks[self.index]['data']
        self.app.db.review_word(item['id'], rating)
        self.app.db.record_answer(
            activity_type='word_review', item_id=item['id'], prompt=item['word'],
            user_answer=str(rating), correct_answer=item['translation'],
            is_correct=rating >= 2, session_id=self.session_id)
        self.answers += 1; self.index += 1; self.show_task()

    def finish(self):
        duration = max(1, int(time.monotonic() - self.started_at))
        self.app.db.finish_session(self.session_id, duration, self.answers)
        if self.on_finish:
            self.on_finish()
        if self.window.winfo_exists():
            self.window.destroy()
        if self.index >= len(self.tasks):
            messagebox.showinfo("Занятие завершено", f"Выполнено заданий: {self.answers}")
