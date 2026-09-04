"""Стартовая вкладка с планом занятия."""

import tkinter as tk

from config import COLORS, FONTS
from ui.daily_lesson import DailyLessonWindow


class TodayTab:
    def __init__(self, parent, app):
        self.parent, self.app = parent, app
        self.duration = tk.IntVar(value=app.db.get_setting('lesson_duration', 15))
        frame = tk.Frame(parent, bg='white', relief='raised', bd=2)
        frame.pack(fill='both', expand=True, padx=30, pady=30)
        tk.Label(frame, text="🎯 Занятие на сегодня", font=FONTS['header'],
                 bg='white', fg=COLORS['dark']).pack(pady=25)
        self.summary = tk.Label(frame, font=FONTS['normal'], bg='white',
                                fg=COLORS['gray'], justify='center')
        self.summary.pack(pady=15)
        tk.Label(frame, text="Продолжительность:", font=FONTS['normal'], bg='white').pack()
        choices = tk.Frame(frame, bg='white'); choices.pack(pady=10)
        for value in (5, 10, 15, 20):
            tk.Radiobutton(choices, text=f"{value} мин", variable=self.duration,
                           value=value, bg='white', font=FONTS['small']).pack(side='left', padx=8)
        tk.Button(frame, text="▶ Начать занятие", command=self.start,
                  font=FONTS['subtitle'], bg=COLORS['success'], fg='white',
                  padx=30, pady=12).pack(pady=25)
        tk.Button(frame, text="📋 Пройти входную диагностику", command=self.diagnostic,
                  font=FONTS['normal'], bg=COLORS['primary'], fg='white',
                  padx=20, pady=8).pack(pady=5)
        self.refresh()

    def refresh(self):
        words = self.app.db.get_word_progress_summary()
        sessions = self.app.db.get_session_summary()
        self.summary.config(text=(f"К повторению: {words['due']} слов\n"
                                  f"Завершено занятий: {sessions['sessions']}\n"
                                  f"Текущий уровень: {self.app.db.get_setting('user_level', 'A2')}"))

    def start(self):
        DailyLessonWindow(self.parent, self.app, self.duration.get(), self.refresh)

    def diagnostic(self):
        from ui.diagnostic_window import DiagnosticWindow
        DiagnosticWindow(self.parent, self.app, self.refresh)
