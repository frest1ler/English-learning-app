"""Окно интервального повторения слов."""

import random
import tkinter as tk
from tkinter import messagebox

from config import COLORS, FONTS


class ReviewWindow:
    def __init__(self, parent, app):
        self.app = app
        self.words = app.db.get_due_words()
        random.shuffle(self.words)
        self.index = 0
        self.revealed = False

        if not self.words:
            messagebox.showinfo("Повторение", "На сегодня слов для повторения нет.")
            return

        self.window = tk.Toplevel(parent)
        self.window.title("Интервальное повторение")
        self.window.geometry("650x520")
        self.window.configure(bg=COLORS['light'])
        self.progress = tk.Label(self.window, font=FONTS['small'], bg=COLORS['light'])
        self.progress.pack(pady=15)
        self.word = tk.Label(self.window, font=FONTS['word'], bg='white', fg=COLORS['dark'])
        self.word.pack(fill='both', expand=True, padx=25, pady=10)
        self.translation = tk.Label(self.window, font=FONTS['translation'], bg='white', fg=COLORS['success'])
        self.translation.pack(fill='x', padx=25)
        self.example = tk.Label(self.window, font=FONTS['example'], bg='white', fg=COLORS['primary'], wraplength=560)
        self.example.pack(fill='x', padx=25, pady=10)
        self.reveal_button = tk.Button(self.window, text="Показать ответ", command=self.reveal,
                                       font=FONTS['normal'], bg=COLORS['primary'], fg='white')
        self.reveal_button.pack(pady=15)
        self.rating_frame = tk.Frame(self.window, bg=COLORS['light'])
        for rating, text, color in (
            (0, 'Не помню', COLORS['danger']), (1, 'Трудно', COLORS['warning']),
            (2, 'Нормально', COLORS['primary']), (3, 'Легко', COLORS['success'])):
            tk.Button(self.rating_frame, text=text, command=lambda value=rating: self.rate(value),
                      font=FONTS['small'], bg=color, fg='white', padx=12, pady=7).pack(side='left', padx=4)
        self.show_word()

    def show_word(self):
        if self.index >= len(self.words):
            messagebox.showinfo("Готово", f"Повторено слов: {len(self.words)}")
            self.app.update_stats()
            self.window.destroy()
            return
        item = self.words[self.index]
        self.revealed = False
        self.progress.config(text=f"Слово {self.index + 1} из {len(self.words)}")
        self.word.config(text=f"{item['word']}\n{item['transcription']}")
        self.translation.config(text='')
        self.example.config(text='')
        self.rating_frame.pack_forget()
        self.reveal_button.pack(pady=15)

    def reveal(self):
        if self.revealed:
            return
        item = self.words[self.index]
        self.revealed = True
        self.translation.config(text=item['translation'])
        self.example.config(text=item.get('example', ''))
        self.reveal_button.pack_forget()
        self.rating_frame.pack(pady=15)

    def rate(self, rating):
        if not self.revealed:
            return
        item = self.words[self.index]
        self.app.db.review_word(item['id'], rating)
        self.app.db.record_answer(
            activity_type='word_review', item_id=item['id'], prompt=item['word'],
            user_answer=('remembered' if rating >= 2 else 'forgotten'),
            correct_answer=item['translation'], is_correct=rating >= 2,
        )
        self.index += 1
        self.show_word()
