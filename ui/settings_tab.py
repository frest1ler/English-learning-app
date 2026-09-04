"""Локальные настройки и резервное копирование."""

import tkinter as tk
from tkinter import filedialog, messagebox

from config import COLORS, FONTS
from llm.providers import ExplanationService, OllamaProvider


class SettingsTab:
    def __init__(self, parent, app):
        self.parent, self.app = parent, app
        frame = tk.Frame(parent, bg='white', relief='raised', bd=2)
        frame.pack(fill='both', expand=True, padx=35, pady=30)
        tk.Label(frame, text='⚙ Настройки', bg='white', font=FONTS['header'],
                 fg=COLORS['dark']).pack(pady=20)
        self.theme = tk.StringVar(value=app.db.get_setting('theme', 'light'))
        self.model = tk.StringVar(value=app.db.get_setting('ollama_model', 'qwen3:4b'))
        self.duration = tk.IntVar(value=app.db.get_setting('lesson_duration', 15))
        tk.Label(frame, text='Тема интерфейса', bg='white', font=FONTS['normal']).pack(pady=4)
        theme_frame = tk.Frame(frame, bg='white'); theme_frame.pack()
        for value, title in (('light', 'Светлая'), ('dark', 'Тёмная')):
            tk.Radiobutton(theme_frame, text=title, value=value, variable=self.theme,
                           bg='white', font=FONTS['small']).pack(side='left', padx=10)
        tk.Label(frame, text='Локальная модель Ollama', bg='white',
                 font=FONTS['normal']).pack(pady=(18, 4))
        tk.Entry(frame, textvariable=self.model, font=FONTS['normal'], width=25,
                 justify='center').pack()
        tk.Label(frame, text='Длительность занятия по умолчанию', bg='white',
                 font=FONTS['normal']).pack(pady=(18, 4))
        duration_frame = tk.Frame(frame, bg='white'); duration_frame.pack()
        for value in (5, 10, 15, 20):
            tk.Radiobutton(duration_frame, text=f'{value} мин', value=value,
                           variable=self.duration, bg='white').pack(side='left', padx=7)
        tk.Button(frame, text='Сохранить настройки', command=self.save,
                  font=FONTS['normal'], bg=COLORS['success'], fg='white',
                  padx=20, pady=8).pack(pady=22)
        tk.Button(frame, text='Создать резервную копию', command=self.backup,
                  font=FONTS['normal'], bg=COLORS['primary'], fg='white',
                  padx=20, pady=8).pack()

    def save(self):
        model = self.model.get().strip() or 'qwen3:4b'
        self.app.db.set_setting('theme', self.theme.get())
        self.app.db.set_setting('ollama_model', model)
        self.app.db.set_setting('lesson_duration', self.duration.get())
        self.app.explanation_service = ExplanationService(OllamaProvider(model=model))
        self.app.today_tab.duration.set(self.duration.get())
        self.app.apply_theme(self.theme.get())
        messagebox.showinfo('Настройки', 'Настройки сохранены.')

    def backup(self):
        path = filedialog.asksaveasfilename(
            title='Сохранить резервную копию', defaultextension='.db',
            filetypes=[('SQLite database', '*.db'), ('Все файлы', '*.*')])
        if path:
            try:
                self.app.db.backup_to(path)
                messagebox.showinfo('Резервная копия', 'Копия успешно создана.')
            except Exception as error:
                messagebox.showerror('Ошибка', f'Не удалось создать копию: {error}')
