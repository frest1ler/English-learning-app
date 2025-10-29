"""
Вкладка упражнений
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
from config import COLORS, FONTS, EXERCISE_MIN_COUNT, EXERCISE_MAX_COUNT, EXERCISE_DEFAULT_COUNT

class ExercisesTab:
    """Класс для вкладки упражнений"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        # Переменные для упражнений
        self.selected_topics = []
        self.mixed_exercises = []
        self.current_exercise_index = 0
        self.current_exercise = None
        self.exercise_results = []
        self.answer_checked = False
        
        self.create_ui()
    
    def create_ui(self):
        """Создание интерфейса вкладки"""
        main_container = tk.Frame(self.parent, bg=COLORS['light'])
        main_container.pack(fill='both', expand=True)
        
        # Левая панель с выбором тем
        self.create_left_panel(main_container)
        
        # Правая панель с упражнениями
        self.create_right_panel(main_container)
    
    def create_left_panel(self, parent):
        """Создание левой панели с настройками"""
        left_panel = tk.Frame(parent, bg='white', relief='raised', bd=1)
        left_panel.pack(side='left', fill='y', padx=10, pady=10)
        
        tk.Label(
            left_panel,
            text="📝 Выберите темы:",
            font=FONTS['subtitle'],
            bg='white',
            fg=COLORS['dark']
        ).pack(pady=10, padx=10)
        
        # Фрейм для чекбоксов
        checkbox_frame = tk.Frame(left_panel, bg='white')
        checkbox_frame.pack(padx=10, pady=5)
        
        # Словарь для хранения переменных чекбоксов
        self.topic_vars = {}
        
        # Создаем чекбоксы для каждой темы
        for topic in self.app.exercises_data.keys():
            var = tk.BooleanVar()
            self.topic_vars[topic] = var
            
            cb = tk.Checkbutton(
                checkbox_frame,
                text=f"{topic} ({len(self.app.exercises_data[topic])})",
                variable=var,
                font=FONTS['small'],
                bg='white',
                anchor='w',
                command=self.update_selected_topics
            )
            cb.pack(fill='x', pady=3)
        
        # Кнопки выбора всех/сброса
        button_frame = tk.Frame(left_panel, bg='white')
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="✅ Выбрать все",
            command=self.select_all_topics,
            font=FONTS['tiny'],
            bg=COLORS['success'],
            fg='white',
            padx=10,
            pady=5
        ).pack(side='left', padx=3)
        
        tk.Button(
            button_frame,
            text="❌ Снять все",
            command=self.deselect_all_topics,
            font=FONTS['tiny'],
            bg=COLORS['danger'],
            fg='white',
            padx=10,
            pady=5
        ).pack(side='left', padx=3)
        
        # Информация о выбранных темах
        self.selected_info_label = tk.Label(
            left_panel,
            text="Выбрано тем: 0\nВсего упражнений: 0",
            font=FONTS['tiny'],
            bg='white',
            fg=COLORS['gray']
        )
        self.selected_info_label.pack(pady=5)
        
        # Настройки упражнений
        settings_frame = tk.Frame(left_panel, bg='white')
        settings_frame.pack(pady=10)
        
        tk.Label(
            settings_frame,
            text="Количество упражнений:",
            font=FONTS['tiny'],
            bg='white'
        ).pack()
        
        self.exercise_count_var = tk.IntVar(value=EXERCISE_DEFAULT_COUNT)
        self.exercise_count_scale = tk.Scale(
            settings_frame,
            from_=EXERCISE_MIN_COUNT,
            to=EXERCISE_MAX_COUNT,
            orient='horizontal',
            variable=self.exercise_count_var,
            bg='white',
            length=150
        )
        self.exercise_count_scale.pack(pady=5)
        
        # Кнопка начала упражнений
        tk.Button(
            left_panel,
            text="🚀 Начать упражнения",
            command=self.start_mixed_exercises,
            font=FONTS['normal'],
            bg=COLORS['primary'],
            fg='white',
            padx=20,
            pady=10
        ).pack(pady=15)
    
    def create_right_panel(self, parent):
        """Создание правой панели с упражнениями"""
        right_panel = tk.Frame(parent, bg=COLORS['light'])
        right_panel.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Фрейм для упражнения
        exercise_frame = tk.Frame(right_panel, bg='white', relief='raised', bd=2)
        exercise_frame.pack(fill='both', expand=True)
        
        # Название правила текущего упражнения
        self.current_topic_label = tk.Label(
            exercise_frame,
            text="",
            font=FONTS['small'],
            bg='white',
            fg=COLORS['purple']
        )
        self.current_topic_label.pack(pady=5)
        
        # Название правила
        self.rule_title_label = tk.Label(
            exercise_frame,
            text="Выберите темы и нажмите 'Начать упражнения'",
            font=FONTS['title'],
            bg='white',
            fg=COLORS['dark']
        )
        self.rule_title_label.pack(pady=15)
        
        # Задание
        self.exercise_instruction_label = tk.Label(
            exercise_frame,
            text="",
            font=FONTS['normal'],
            bg='white',
            fg=COLORS['gray']
        )
        self.exercise_instruction_label.pack(pady=5)
        
        # Предложение
        self.sentence_label = tk.Label(
            exercise_frame,
            text="",
            font=('Arial', 18),
            bg='white',
            fg='#34495e',
            wraplength=500
        )
        self.sentence_label.pack(pady=20, padx=20)
        
        # Подсказка
        self.hint_label = tk.Label(
            exercise_frame,
            text="",
            font=('Arial', 11, 'italic'),
            bg='white',
            fg=COLORS['gray']
        )
        self.hint_label.pack(pady=5)
        
        # Поле для ввода ответа
        answer_frame = tk.Frame(right_panel, bg=COLORS['light'])
        answer_frame.pack(pady=10)
        
        tk.Label(
            answer_frame,
            text="Ваш ответ:",
            font=FONTS['normal'],
            bg=COLORS['light']
        ).pack(side='left', padx=10)
        
        self.answer_entry = tk.Entry(
            answer_frame,
            font=('Arial', 14),
            width=20
        )
        self.answer_entry.pack(side='left', padx=10)
        self.answer_entry.bind('<Return>', lambda e: self.check_grammar_answer())
        
        tk.Button(
            answer_frame,
            text="Проверить",
            command=self.check_grammar_answer,
            font=FONTS['normal'],
            bg=COLORS['primary'],
            fg='white',
            padx=20,
            pady=5
        ).pack(side='left', padx=10)
        
        tk.Button(
            answer_frame,
            text="💡 Подсказка",
            command=self.show_hint,
            font=FONTS['small'],
            bg=COLORS['warning'],
            fg='white',
            padx=15,
            pady=5
        ).pack(side='left', padx=5)
        
        # Результат
        self.result_label = tk.Label(
            right_panel,
            text="",
            font=('Arial', 14),
            bg=COLORS['light']
        )
        self.result_label.pack(pady=10)
        
        # Кнопка следующего упражнения
        self.next_exercise_btn = tk.Button(
            right_panel,
            text="Следующее упражнение ▶",
            command=self.next_exercise,
            font=FONTS['normal'],
            bg=COLORS['primary'],
            fg='white',
            padx=20,
            pady=10,
            state='disabled'
        )
        self.next_exercise_btn.pack(pady=10)
        
        # Прогресс и счет
        progress_frame = tk.Frame(right_panel, bg=COLORS['light'])
        progress_frame.pack(pady=10)
        
        self.exercise_progress_label = tk.Label(
            progress_frame,
            text="",
            font=FONTS['small'],
            bg=COLORS['light'],
            fg=COLORS['gray']
        )
        self.exercise_progress_label.pack(side='left', padx=10)
        
        self.score_label = tk.Label(
            progress_frame,
            text="Счет: 0/0",
            font=FONTS['normal'],
            bg=COLORS['light'],
            fg=COLORS['dark']
        )
        self.score_label.pack(side='left', padx=10)
    
    def update_selected_topics(self):
        """Обновить информацию о выбранных темах"""
        selected = [topic for topic, var in self.topic_vars.items() if var.get()]
        total_exercises = sum(len(self.app.exercises_data[topic]) for topic in selected)
        
        self.selected_info_label.config(
            text=f"Выбрано тем: {len(selected)}\nВсего упражнений: {total_exercises}"
        )
        
        if total_exercises > 0:
            max_exercises = min(total_exercises, EXERCISE_MAX_COUNT)
            self.exercise_count_scale.config(to=max_exercises)
            if self.exercise_count_var.get() > max_exercises:
                self.exercise_count_var.set(max_exercises)
    
    def select_all_topics(self):
        """Выбрать все темы"""
        for var in self.topic_vars.values():
            var.set(True)
        self.update_selected_topics()
    
    def deselect_all_topics(self):
        """Снять выбор со всех тем"""
        for var in self.topic_vars.values():
            var.set(False)
        self.update_selected_topics()
    
    def start_mixed_exercises(self):
        """Начать упражнения по выбранным темам"""
        self.selected_topics = [topic for topic, var in self.topic_vars.items() if var.get()]
        
        if not self.selected_topics:
            messagebox.showwarning("Внимание", "Выберите хотя бы одну тему!")
            return
        
        # Собираем все упражнения из выбранных тем
        all_exercises = []
        for topic in self.selected_topics:
            all_exercises.extend(self.app.exercises_data[topic])
        
        # Перемешиваем и выбираем нужное количество
        random.shuffle(all_exercises)
        exercise_count = min(self.exercise_count_var.get(), len(all_exercises))
        self.mixed_exercises = all_exercises[:exercise_count]
        
        # Сбрасываем счетчики и флаги
        self.current_exercise_index = 0
        self.exercise_results = []
        self.answer_checked = False
        
        self.rule_title_label.config(text="📚 Смешанные упражнения")
        self.exercise_instruction_label.config(text="Поставьте глагол в правильную форму:")
        
        self.show_mixed_exercise()
    
    def show_mixed_exercise(self):
        """Показать текущее упражнение из смешанного списка"""
        if self.current_exercise_index >= len(self.mixed_exercises):
            self.show_mixed_results()
            return
        
        self.answer_checked = False
        self.current_exercise = self.mixed_exercises[self.current_exercise_index]
        
        self.current_topic_label.config(text=f"📌 Тема: {self.current_exercise['rule']}")
        self.sentence_label.config(text=self.current_exercise['sentence'])
        
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.config(state='normal')
        self.result_label.config(text="")
        self.hint_label.config(text="")
        self.next_exercise_btn.config(state='disabled')
        
        self.exercise_progress_label.config(
            text=f"Упражнение {self.current_exercise_index + 1} из {len(self.mixed_exercises)}"
        )
        
        self.answer_entry.focus()
    
    def show_hint(self):
        """Показать подсказку"""
        if self.current_exercise and self.current_exercise['hint']:
            self.hint_label.config(text=f"💡 {self.current_exercise['hint']}")
    
    def check_grammar_answer(self):
        """Проверка ответа в грамматическом упражнении"""
        if not self.current_exercise or self.answer_checked:
            return
        
        user_answer = self.answer_entry.get().strip()
        if not user_answer:
            messagebox.showwarning("Внимание", "Введите ответ!")
            return
        
        self.answer_checked = True
        
        # Используем улучшенную проверку с поддержкой вариантов
        from utils.helpers import check_answer_match, format_correct_answer
        
        is_correct = check_answer_match(user_answer, self.current_exercise['answer'])
        
        self.app.total_attempts += 1
        
        self.exercise_results.append({
            'exercise': self.current_exercise,
            'user_answer': user_answer,
            'is_correct': is_correct
        })
        
        if is_correct:
            self.app.score += 1
            formatted_answer = format_correct_answer(self.current_exercise['answer'])
            self.result_label.config(
                text=f"✅ Правильно! {formatted_answer}",
                fg=COLORS['success']
            )
        else:
            formatted_answer = format_correct_answer(self.current_exercise['answer'])
            self.result_label.config(
                text=f"❌ Неправильно. Правильный ответ: {formatted_answer}",
                fg=COLORS['danger']
            )
        
        self.score_label.config(text=f"Счет: {self.app.score}/{self.app.total_attempts}")
        self.next_exercise_btn.config(state='normal')
        self.answer_entry.config(state='disabled')
        
        self.app.update_stats()
        self.app.save_progress()
    
    def next_exercise(self):
        """Следующее упражнение"""
        self.answer_checked = False
        self.answer_entry.config(state='normal')
        self.current_exercise_index += 1
        self.show_mixed_exercise()
    
    def show_mixed_results(self):
        """Показать результаты смешанных упражнений"""
        if not self.mixed_exercises:
            return
        
        results_window = tk.Toplevel(self.parent)
        results_window.title("Результаты упражнений")
        results_window.geometry("700x600")
        results_window.configure(bg=COLORS['light'])
        
        tk.Label(
            results_window,
            text="📊 Результаты упражнений",
            font=('Arial', 18, 'bold'),
            bg=COLORS['light'],
            fg=COLORS['dark']
        ).pack(pady=15)
        
        # Статистика
        correct_count = sum(1 for r in self.exercise_results if r['is_correct'])
        total_count = len(self.exercise_results)
        percentage = (correct_count / total_count * 100) if total_count > 0 else 0
        
        stats_frame = tk.Frame(results_window, bg='white', relief='raised', bd=1)
        stats_frame.pack(pady=10, padx=20, fill='x')
        
        # Определяем оценку
        if percentage >= 90:
            grade, grade_color = "Отлично! 🎉", COLORS['success']
        elif percentage >= 75:
            grade, grade_color = "Хорошо! 👍", COLORS['primary']
        elif percentage >= 60:
            grade, grade_color = "Неплохо 📚", COLORS['warning']
        else:
            grade, grade_color = "Нужна практика 💪", COLORS['danger']
        
        tk.Label(stats_frame, text=grade, font=FONTS['title'], bg='white', fg=grade_color).pack(pady=10)
        tk.Label(stats_frame, text=f"Правильных ответов: {correct_count} из {total_count}", 
                font=('Arial', 14), bg='white').pack(pady=5)
        tk.Label(stats_frame, text=f"Результат: {percentage:.1f}%", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=5)
        
        # Детальные результаты
        details_frame = tk.Frame(results_window, bg='white', relief='raised', bd=1)
        details_frame.pack(pady=5, padx=20, fill='both', expand=True)
        
        text_widget = scrolledtext.ScrolledText(details_frame, font=FONTS['tiny'], 
                                                wrap=tk.WORD, height=10, bg='white')
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        for i, result in enumerate(self.exercise_results, 1):
            exercise = result['exercise']
            symbol = "✓" if result['is_correct'] else "✗"
            
            text_widget.insert(tk.END, f"{i}. [{exercise['rule']}]\n")
            text_widget.insert(tk.END, f"   {exercise['sentence']}\n")
            text_widget.insert(tk.END, f"   Правильный ответ: {exercise['answer']}\n")
            if not result['is_correct']:
                text_widget.insert(tk.END, f"   Ваш ответ: {result['user_answer']}\n")
            text_widget.insert(tk.END, f"   {symbol}\n\n")
        
        text_widget.config(state='disabled')
        
        # Кнопки
        button_frame = tk.Frame(results_window, bg=COLORS['light'])
        button_frame.pack(pady=15)
        
        tk.Button(button_frame, text="Новые упражнения", 
                 command=lambda: [results_window.destroy(), self.reset_exercises()],
                 font=FONTS['normal'], bg=COLORS['primary'], fg='white', 
                 padx=20, pady=8).pack(side='left', padx=10)
        
        tk.Button(button_frame, text="Закрыть", command=results_window.destroy,
                 font=FONTS['normal'], bg=COLORS['gray'], fg='white', 
                 padx=20, pady=8).pack(side='left', padx=10)
    
    def reset_exercises(self):
        """Сброс упражнений для новой сессии"""
        self.current_exercise_index = 0
        self.current_exercise = None
        self.mixed_exercises = []
        self.exercise_results = []
        self.answer_checked = False
        
        self.sentence_label.config(text="")
        self.exercise_progress_label.config(text="")
        self.result_label.config(text="")
        self.hint_label.config(text="")
        self.current_topic_label.config(text="")
        self.rule_title_label.config(text="Выберите темы и нажмите 'Начать упражнения'")
        self.exercise_instruction_label.config(text="")
        self.answer_entry.config(state='normal')
        self.answer_entry.delete(0, tk.END)
