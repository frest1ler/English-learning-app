"""
Вкладка правил
"""

import tkinter as tk
from tkinter import scrolledtext
from config import COLORS, FONTS

class RulesTab:
    """Класс для вкладки правил"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_ui()
    
    def create_ui(self):
        """Создание интерфейса вкладки"""
        # Список правил
        list_frame = tk.Frame(self.parent, bg=COLORS['light'])
        list_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        tk.Label(
            list_frame,
            text="Выберите правило:",
            font=FONTS['normal'],
            bg=COLORS['light']
        ).pack(pady=5)
        
        # Listbox для выбора правила
        self.rules_listbox = tk.Listbox(
            list_frame,
            font=FONTS['small'],
            width=30,
            height=20
        )
        self.rules_listbox.pack(pady=5)
        self.rules_listbox.bind('<<ListboxSelect>>', self.show_rule)
        
        # Заполнение списка правил
        for rule in self.app.rules_data:
            self.rules_listbox.insert(tk.END, rule['title'])
        
        # Область отображения правила
        content_frame = tk.Frame(self.parent, bg='white', relief='raised', bd=2)
        content_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.rules_title_label = tk.Label(
            content_frame,
            text="Выберите правило из списка",
            font=FONTS['title'],
            bg='white',
            fg=COLORS['dark']
        )
        self.rules_title_label.pack(pady=10)
        
        self.rules_text_widget = scrolledtext.ScrolledText(
            content_frame,
            font=FONTS['small'],
            wrap=tk.WORD,
            width=60,
            height=25,
            bg='white'
        )
        self.rules_text_widget.pack(padx=10, pady=10, fill='both', expand=True)
    
    def show_rule(self, event):
        """Отображение выбранного правила"""
        selection = self.rules_listbox.curselection()
        if selection:
            index = selection[0]
            rule = self.app.rules_data[index]
            self.rules_title_label.config(text=rule['title'])
            self.rules_text_widget.delete('1.0', tk.END)
            self.rules_text_widget.insert('1.0', rule['content'])
