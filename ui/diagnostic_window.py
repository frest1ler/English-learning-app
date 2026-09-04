"""Окно входной адаптивной диагностики."""

import tkinter as tk
from tkinter import messagebox

from config import COLORS, FONTS
from learning.diagnostic import DiagnosticEngine
from utils.helpers import check_answer_match, format_correct_answer


class DiagnosticWindow:
    def __init__(self, parent, app, on_finish=None):
        self.app, self.on_finish = app, on_finish
        self.engine = DiagnosticEngine(app.db.get_diagnostic_questions(), limit=30)
        self.current = None
        self.checked = False
        self.window = tk.Toplevel(parent)
        self.window.title('Входная диагностика')
        self.window.geometry('700x500')
        self.window.configure(bg=COLORS['light'])
        tk.Label(self.window, text='Диагностика уровня', font=FONTS['header'],
                 bg=COLORS['light'], fg=COLORS['dark']).pack(pady=20)
        self.progress = tk.Label(self.window, bg=COLORS['light'], font=FONTS['small'])
        self.progress.pack()
        self.prompt = tk.Label(self.window, bg='white', font=FONTS['title'],
                               wraplength=620, fg=COLORS['dark'])
        self.prompt.pack(fill='both', expand=True, padx=30, pady=20)
        self.entry = tk.Entry(self.window, font=FONTS['input'], justify='center', width=35)
        self.entry.pack(pady=8); self.entry.bind('<Return>', lambda event: self.submit())
        self.feedback = tk.Label(self.window, bg=COLORS['light'], font=FONTS['normal'])
        self.feedback.pack(pady=5)
        self.button = tk.Button(self.window, text='Проверить', command=self.submit,
                                bg=COLORS['primary'], fg='white', font=FONTS['normal'],
                                padx=20, pady=8)
        self.button.pack(pady=12)
        self.show_next()

    def show_next(self):
        self.current = self.engine.next_question()
        if not self.current:
            self.finish(); return
        self.checked = False
        self.progress.config(text=f"Вопрос {len(self.engine.results) + 1} из {self.engine.limit}")
        self.prompt.config(text=self.current['prompt'])
        self.entry.config(state='normal'); self.entry.delete(0, tk.END); self.entry.focus()
        self.feedback.config(text=''); self.button.config(text='Проверить')

    def submit(self):
        if self.checked:
            self.show_next(); return
        answer = self.entry.get().strip()
        if not answer:
            return
        correct = check_answer_match(answer, self.current['answer'])
        self.engine.submit(self.current, correct)
        self.app.db.record_answer(
            activity_type='diagnostic', item_id=self.current['item_id'],
            topic_id=self.current['topic_id'], prompt=self.current['prompt'],
            user_answer=answer, correct_answer=self.current['answer'], is_correct=correct)
        self.checked = True; self.entry.config(state='disabled')
        self.feedback.config(
            text='✅ Правильно' if correct else
                 f"❌ Ответ: {format_correct_answer(self.current['answer'])}",
            fg=COLORS['success'] if correct else COLORS['danger'])
        self.button.config(text='Далее')

    def finish(self):
        result = self.engine.summary()
        self.app.db.set_setting('user_level', result['estimated_level'])
        self.app.db.set_setting('diagnostic_result', result)
        if self.on_finish: self.on_finish()
        self.window.destroy()
        lines = [f"Ориентировочный уровень: {result['estimated_level']}"]
        for skill, value in result['skills'].items():
            accuracy = value['correct'] / value['attempts'] * 100 if value['attempts'] else 0
            lines.append(f"{skill}: {accuracy:.0f}%")
        messagebox.showinfo('Результат диагностики', '\n'.join(lines))
