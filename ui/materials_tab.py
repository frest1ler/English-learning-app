"""Поиск и просмотр локальной библиотеки материалов."""

import tkinter as tk
from tkinter import ttk

from config import COLORS, FONTS


class MaterialsTab:
    def __init__(self, parent, app):
        self.parent, self.app = parent, app
        self.items = []
        controls = tk.Frame(parent, bg=COLORS['light']); controls.pack(fill='x', padx=12, pady=10)
        self.search = tk.StringVar(); self.kind = tk.StringVar(value='all'); self.level = tk.StringVar(value='all')
        tk.Label(controls, text='Поиск:', bg=COLORS['light']).pack(side='left')
        entry = tk.Entry(controls, textvariable=self.search, width=25); entry.pack(side='left', padx=5)
        entry.bind('<Return>', lambda event: self.refresh())
        ttk.Combobox(controls, textvariable=self.kind, state='readonly', width=13,
                     values=('all', 'words', 'exercises')).pack(side='left', padx=5)
        ttk.Combobox(controls, textvariable=self.level, state='readonly', width=7,
                     values=('all', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2')).pack(side='left', padx=5)
        tk.Button(controls, text='Найти', command=self.refresh, bg=COLORS['primary'],
                  fg='white').pack(side='left', padx=5)
        self.count = tk.Label(controls, bg=COLORS['light'], fg=COLORS['gray']); self.count.pack(side='right')
        tk.Button(controls, text='✨ Qwen', command=self.open_generator,
                  bg=COLORS['purple'], fg='white').pack(side='right', padx=6)
        body = tk.Frame(parent, bg=COLORS['light']); body.pack(fill='both', expand=True, padx=12, pady=8)
        self.listbox = tk.Listbox(body, width=50, font=FONTS['tiny'])
        self.listbox.pack(side='left', fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.show_selected)
        self.detail = tk.Text(body, width=45, font=FONTS['small'], wrap=tk.WORD,
                              bg='white', state='disabled')
        self.detail.pack(side='right', fill='both', expand=True, padx=(10, 0))
        self.refresh()

    def open_generator(self):
        from ui.generator_window import GeneratorWindow
        GeneratorWindow(self.parent, self.app)

    def refresh(self):
        self.items = self.app.db.search_materials(
            self.kind.get(), self.search.get(), self.level.get())
        self.listbox.delete(0, tk.END)
        for item in self.items:
            marker = '📖' if item['kind'] == 'word' else '✏'
            self.listbox.insert(tk.END, f"{marker} [{item['cefr_level']}] {item['title'][:70]}")
        self.count.config(text=f"Найдено: {len(self.items)}")
        self.detail.config(state='normal'); self.detail.delete('1.0', tk.END); self.detail.config(state='disabled')

    def show_selected(self, event=None):
        selection = self.listbox.curselection()
        if not selection: return
        item = self.items[selection[0]]
        lines = [item['title'], '', f"Ответ / перевод: {item['detail']}",
                 f"Уровень: {item['cefr_level']}", f"Источник: {item['source']}",
                 f"Статус: {item['review_status']}"]
        if item.get('rule'): lines.append(f"Тема: {item['rule']}")
        if item.get('exercise_type'): lines.append(f"Тип: {item['exercise_type']}")
        self.detail.config(state='normal'); self.detail.delete('1.0', tk.END)
        self.detail.insert('1.0', '\n'.join(lines)); self.detail.config(state='disabled')
