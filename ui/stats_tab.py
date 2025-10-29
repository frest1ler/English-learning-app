"""
Вкладка статистики
"""

import tkinter as tk
from tkinter import messagebox
from config import COLORS, FONTS

class StatsTab:
    """Класс для вкладки статистики"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.create_ui()
    
    def create_ui(self):
        """Создание интерфейса вкладки"""
        stats_container = tk.Frame(self.parent, bg='white', relief='raised', bd=2)
        stats_container.pack(pady=20, padx=20, fill='both', expand=True)
        
        tk.Label(
            stats_container,
            text="📊 Ваша статистика",
            font=('Arial', 20, 'bold'),
            bg='white',
            fg=COLORS['dark']
        ).pack(pady=20)
        
        # Статистика по словам
        words_frame = tk.Frame(stats_container, bg=COLORS['light'], relief='raised', bd=1)
        words_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(
            words_frame,
            text="📖 Словарь",
            font=FONTS['subtitle'],
            bg=COLORS['light']
        ).pack(pady=5)
        
        tk.Label(
            words_frame,
            text=f"Всего слов: {len(self.app.words_data)}",
            font=FONTS['normal'],
            bg=COLORS['light']
        ).pack(pady=3)
        
        # Подсчет слов с примерами
        words_with_examples = sum(1 for word in self.app.words_data if word.get('example'))
        tk.Label(
            words_frame,
            text=f"Слов с примерами: {words_with_examples}",
            font=FONTS['small'],
            bg=COLORS['light'],
            fg=COLORS['gray']
        ).pack(pady=2)
        
        # Статистика по упражнениям
        exercises_frame = tk.Frame(stats_container, bg=COLORS['light'], relief='raised', bd=1)
        exercises_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(
            exercises_frame,
            text="✏️ Упражнения",
            font=FONTS['subtitle'],
            bg=COLORS['light']
        ).pack(pady=5)
        
        self.stats_score_label = tk.Label(
            exercises_frame,
            text=f"✅ Правильных ответов: {self.app.score}",
            font=FONTS['normal'],
            bg=COLORS['light'],
            fg=COLORS['success']
        )
        self.stats_score_label.pack(pady=3)
        
        self.stats_total_label = tk.Label(
            exercises_frame,
            text=f"📝 Всего попыток: {self.app.total_attempts}",
            font=FONTS['normal'],
            bg=COLORS['light']
        )
        self.stats_total_label.pack(pady=3)
        
        self.accuracy_label = tk.Label(
            exercises_frame,
            text="📈 Точность: 0%",
            font=FONTS['normal'],
            bg=COLORS['light'],
            fg=COLORS['primary']
        )
        self.accuracy_label.pack(pady=3)
        
        # Последняя сессия
        if 'last_session' in self.app.progress_data:
            tk.Label(
                stats_container,
                text=f"🕒 Последняя сессия: {self.app.progress_data['last_session']}",
                font=FONTS['small'],
                bg='white',
                fg=COLORS['gray']
            ).pack(pady=10)
        
        # Кнопки
        button_frame = tk.Frame(stats_container, bg='white')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="🔄 Сбросить статистику",
            command=self.reset_stats,
            font=FONTS['normal'],
            bg=COLORS['danger'],
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="💾 Сохранить прогресс",
            command=self.save_progress,
            font=FONTS['normal'],
            bg=COLORS['success'],
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=5)
        
        # Обновляем статистику
        self.update()
    
    def update(self):
        """Обновление статистики"""
        self.stats_score_label.config(text=f"✅ Правильных ответов: {self.app.score}")
        self.stats_total_label.config(text=f"📝 Всего попыток: {self.app.total_attempts}")
        
        if self.app.total_attempts > 0:
            accuracy = (self.app.score / self.app.total_attempts) * 100
            self.accuracy_label.config(text=f"📈 Точность: {accuracy:.1f}%")
    
    def reset_stats(self):
        """Сброс статистики"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите сбросить статистику?"):
            self.app.score = 0
            self.app.total_attempts = 0
            self.update()
            self.app.save_progress()
            messagebox.showinfo("Успешно", "Статистика сброшена!")
    
    def save_progress(self):
        """Сохранение прогресса"""
        self.app.save_progress()
        messagebox.showinfo("Успешно", "Прогресс сохранен!")
