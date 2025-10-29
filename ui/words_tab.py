"""
Вкладка словаря с встроенным тестом
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
from config import COLORS, FONTS, TEST_MIN_WORDS, TEST_MAX_WORDS, TEST_DEFAULT_WORDS
from data.loader import DataLoader
from utils.helpers import normalize_answer

class WordsTab:
    """Класс для вкладки словаря"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_word_index = 0
        
        # Переменные для теста
        self.test_mode = False
        self.test_words = []
        self.test_current_index = 0
        self.test_score = 0
        self.test_answers = []
        self.test_type = "eng_to_rus"
        self.test_answer_checked = False
        self.current_correct_answer = ""
        self.current_question_type = ""
        
        self.create_ui()
    
    def create_ui(self):
        """Создание интерфейса вкладки"""
        # Главный контейнер
        self.container = tk.Frame(self.parent, bg=COLORS['light'])
        self.container.pack(fill='both', expand=True)
        
        # Фрейм выбора режима
        self.create_mode_buttons()
        
        # Панель поиска
        self.create_search_panel()
        
        # Контейнер для режима изучения
        self.study_container = tk.Frame(self.container, bg=COLORS['light'])
        self.study_container.pack(fill='both', expand=True)
        
        # Создаем карточку слова
        self.create_word_card()
        
        # Создаем кнопки управления
        self.create_control_buttons()
        
        # Кнопки для примеров
        self.create_example_buttons()
        
        # Прогресс
        self.word_progress_label = tk.Label(
            self.study_container,
            text="",
            font=FONTS['small'],
            bg=COLORS['light'],
            fg=COLORS['gray']
        )
        self.word_progress_label.pack()
        
        # Контейнер для режима теста (изначально скрыт)
        self.test_container = tk.Frame(self.container, bg=COLORS['light'])
        
        # Показываем первое слово
        self.show_word()
    
    def create_mode_buttons(self):
        """Создание кнопок выбора режима"""
        mode_frame = tk.Frame(self.container, bg=COLORS['light'])
        mode_frame.pack(pady=10)
        
        tk.Button(
            mode_frame,
            text="📖 Режим изучения",
            command=self.switch_to_study_mode,
            font=FONTS['normal'],
            bg=COLORS['primary'],
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            mode_frame,
            text="🎯 Режим теста",
            command=self.show_test_setup,
            font=FONTS['normal'],
            bg=COLORS['orange'],
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            mode_frame,
            text="➕ Добавить слово",
            command=self.show_add_word_dialog,
            font=FONTS['normal'],
            bg=COLORS['success'],
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
    
    def create_search_panel(self):
        """Создание панели поиска"""
        search_frame = tk.Frame(self.container, bg=COLORS['light'])
        search_frame.pack(pady=10)
        
        tk.Label(
            search_frame,
            text="🔍 Поиск:",
            font=FONTS['small'],
            bg=COLORS['light']
        ).pack(side='left', padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=FONTS['small'], width=20)
        self.search_entry.pack(side='left', padx=5)
        
        tk.Button(
            search_frame,
            text="Найти",
            command=self.search_word,
            font=FONTS['tiny'],
            bg=COLORS['primary'],
            fg='white',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
    
    def create_word_card(self):
        """Создание карточки слова"""
        card_frame = tk.Frame(self.study_container, bg='white', relief='raised', bd=2)
        card_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Слово
        self.word_label = tk.Label(
            card_frame,
            text="",
            font=FONTS['word'],
            bg='white',
            fg=COLORS['dark']
        )
        self.word_label.pack(pady=20)
        
        # Транскрипция
        self.transcription_label = tk.Label(
            card_frame,
            text="",
            font=FONTS['transcription'],
            bg='white',
            fg=COLORS['gray']
        )
        self.transcription_label.pack(pady=10)
        
        # Перевод
        self.translation_label = tk.Label(
            card_frame,
            text="",
            font=FONTS['translation'],
            bg='white',
            fg=COLORS['success']
        )
        self.translation_label.pack(pady=20)
        
        # Пример использования
        self.example_label = tk.Label(
            card_frame,
            text="",
            font=FONTS['example'],
            bg='white',
            fg=COLORS['primary'],
            wraplength=600
        )
        self.example_label.pack(pady=10)
        
        # Перевод примера
        self.example_translation_label = tk.Label(
            card_frame,
            text="",
            font=('Arial', 13),
            bg='white',
            fg=COLORS['gray'],
            wraplength=600
        )
        self.example_translation_label.pack(pady=5)
    
    def create_control_buttons(self):
        """Создание кнопок управления"""
        control_frame = tk.Frame(self.study_container, bg=COLORS['light'])
        control_frame.pack(pady=20)
        
        tk.Button(
            control_frame,
            text="◀ Предыдущее",
            command=self.prev_word,
            font=FONTS['normal'],
            bg=COLORS['primary'],
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        tk.Button(
            control_frame,
            text="Показать перевод",
            command=self.show_translation,
            font=FONTS['normal'],
            bg=COLORS['danger'],
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        tk.Button(
            control_frame,
            text="Следующее ▶",
            command=self.next_word,
            font=FONTS['normal'],
            bg=COLORS['primary'],
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        tk.Button(
            control_frame,
            text="🔀 Случайное",
            command=self.random_word,
            font=FONTS['normal'],
            bg=COLORS['purple'],
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
    
    def create_example_buttons(self):
        """Создание кнопок для примеров"""
        example_frame = tk.Frame(self.study_container, bg=COLORS['light'])
        example_frame.pack(pady=10)
        
        tk.Button(
            example_frame,
            text="📝 Показать пример",
            command=self.show_example,
            font=FONTS['small'],
            bg=COLORS['teal'],
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            example_frame,
            text="🔄 Перевод примера",
            command=self.show_example_translation,
            font=FONTS['small'],
            bg=COLORS['info'],
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
    
    # ==================== МЕТОДЫ ДЛЯ РЕЖИМА ИЗУЧЕНИЯ ====================
    
    def show_word(self):
        """Отображение текущего слова"""
        if self.app.words_data:
            word_data = self.app.words_data[self.current_word_index]
            self.word_label.config(text=word_data['word'])
            self.transcription_label.config(text=word_data['transcription'])
            self.translation_label.config(text="")
            self.example_label.config(text="")
            self.example_translation_label.config(text="")
            
            self.word_progress_label.config(
                text=f"Слово {self.current_word_index + 1} из {len(self.app.words_data)}"
            )
    
    def show_translation(self):
        """Показать перевод текущего слова"""
        if self.app.words_data:
            word_data = self.app.words_data[self.current_word_index]
            self.translation_label.config(text=word_data['translation'])
    
    def show_example(self):
        """Показать пример использования слова"""
        if self.test_mode and self.test_words:
            word_data = self.test_words[self.test_current_index]
            label = self.test_example_label
        elif self.app.words_data:
            word_data = self.app.words_data[self.current_word_index]
            label = self.example_label
        else:
            return
        
        if word_data.get('example'):
            label.config(text=f"💡 {word_data['example']}")
        else:
            label.config(text="💡 Пример недоступен")
    
    def show_example_translation(self):
        """Показать перевод примера"""
        if self.test_mode and self.test_words:
            word_data = self.test_words[self.test_current_index]
            label = self.test_example_translation_label
        elif self.app.words_data:
            word_data = self.app.words_data[self.current_word_index]
            label = self.example_translation_label
        else:
            return
        
        if word_data.get('example_translation'):
            label.config(text=f"📖 {word_data['example_translation']}")
        else:
            label.config(text="📖 Перевод недоступен")
    
    def next_word(self):
        """Следующее слово"""
        if self.app.words_data:
            self.current_word_index = (self.current_word_index + 1) % len(self.app.words_data)
            self.show_word()
    
    def prev_word(self):
        """Предыдущее слово"""
        if self.app.words_data:
            self.current_word_index = (self.current_word_index - 1) % len(self.app.words_data)
            self.show_word()
    
    def random_word(self):
        """Случайное слово"""
        if self.app.words_data:
            self.current_word_index = random.randint(0, len(self.app.words_data) - 1)
            self.show_word()
    
    def search_word(self):
        """Поиск слова в словаре"""
        from utils.helpers import search_in_list
        
        search_term = self.search_entry.get().strip()
        if not search_term:
            return
        
        index = search_in_list(search_term, self.app.words_data, ['word', 'translation'])
        if index >= 0:
            self.current_word_index = index
            self.show_word()
            messagebox.showinfo("Найдено", f"Слово найдено: {self.app.words_data[index]['word']}")
        else:
            messagebox.showinfo("Не найдено", "Слово не найдено в словаре")
    
    def show_add_word_dialog(self):
        """Диалог добавления нового слова"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Добавить новое слово")
        dialog.geometry("500x450")
        dialog.configure(bg=COLORS['light'])
        
        tk.Label(
            dialog,
            text="Добавить новое слово",
            font=FONTS['subtitle'],
            bg=COLORS['light']
        ).pack(pady=15)
        
        # Поля ввода
        entries = {}
        fields = [
            ('word', 'Английское слово:'),
            ('translation', 'Перевод:'),
            ('transcription', 'Транскрипция:'),
            ('example', 'Пример использования (опционально):'),
            ('example_translation', 'Перевод примера (опционально):')
        ]
        
        for field_name, label_text in fields:
            tk.Label(dialog, text=label_text, bg=COLORS['light']).pack(pady=5)
            entry = tk.Entry(dialog, font=FONTS['normal'], width=40)
            entry.pack(pady=5)
            entries[field_name] = entry
        
        def add_word():
            word_data = {
                'word': entries['word'].get().strip(),
                'translation': entries['translation'].get().strip(),
                'transcription': entries['transcription'].get().strip() or '[...]',
                'example': entries['example'].get().strip(),
                'example_translation': entries['example_translation'].get().strip()
            }
            
            if not word_data['word'] or not word_data['translation']:
                messagebox.showwarning("Внимание", "Заполните обязательные поля!")
                return
            
            self.app.words_data.append(word_data)
            
            if DataLoader.save_word(word_data):
                messagebox.showinfo("Успешно", "Слово добавлено!")
                dialog.destroy()
                self.show_word()
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить слово")
        
        tk.Button(
            dialog,
            text="✅ Добавить",
            command=add_word,
            font=FONTS['normal'],
            bg=COLORS['success'],
            fg='white',
            padx=20,
            pady=8
        ).pack(pady=15)
        
        tk.Button(
            dialog,
            text="Отмена",
            command=dialog.destroy,
            font=FONTS['small'],
            bg=COLORS['gray'],
            fg='white',
            padx=15,
            pady=5
        ).pack()
    
    # ==================== МЕТОДЫ ДЛЯ РЕЖИМА ТЕСТА ====================
    
    def show_test_setup(self):
        """Показать настройки теста"""
        setup_window = tk.Toplevel(self.parent)
        setup_window.title("Настройки теста")
        setup_window.geometry("400x350")
        setup_window.configure(bg=COLORS['light'])
        
        tk.Label(
            setup_window,
            text="⚙️ Настройки теста",
            font=FONTS['title'],
            bg=COLORS['light'],
            fg=COLORS['dark']
        ).pack(pady=15)
        
        # Выбор типа теста
        tk.Label(
            setup_window,
            text="Тип теста:",
            font=FONTS['normal'],
            bg=COLORS['light']
        ).pack(pady=5)
        
        test_type_var = tk.StringVar(value="eng_to_rus")
        
        tk.Radiobutton(
            setup_window,
            text="Английский → Русский",
            variable=test_type_var,
            value="eng_to_rus",
            font=FONTS['small'],
            bg=COLORS['light']
        ).pack(pady=5)
        
        tk.Radiobutton(
            setup_window,
            text="Русский → Английский",
            variable=test_type_var,
            value="rus_to_eng",
            font=FONTS['small'],
            bg=COLORS['light']
        ).pack(pady=5)
        
        tk.Radiobutton(
            setup_window,
            text="Смешанный",
            variable=test_type_var,
            value="mixed",
            font=FONTS['small'],
            bg=COLORS['light']
        ).pack(pady=5)
        
        # Выбор количества слов
        tk.Label(
            setup_window,
            text="Количество слов:",
            font=FONTS['normal'],
            bg=COLORS['light']
        ).pack(pady=10)
        
        words_count_var = tk.IntVar(value=TEST_DEFAULT_WORDS)
        words_scale = tk.Scale(
            setup_window,
            from_=TEST_MIN_WORDS,
            to=min(len(self.app.words_data), TEST_MAX_WORDS),
            orient='horizontal',
            variable=words_count_var,
            bg=COLORS['light'],
            length=200
        )
        words_scale.pack(pady=5)
        
        # Кнопка начала теста
        tk.Button(
            setup_window,
            text="🚀 Начать тест",
            command=lambda: self.start_test(test_type_var.get(), words_count_var.get(), setup_window),
            font=FONTS['normal'],
            bg=COLORS['success'],
            fg='white',
            padx=20,
            pady=10
        ).pack(pady=20)
        
        tk.Button(
            setup_window,
            text="Отмена",
            command=setup_window.destroy,
            font=FONTS['small'],
            bg=COLORS['gray'],
            fg='white',
            padx=15,
            pady=5
        ).pack()
    
    def start_test(self, test_type, words_count, setup_window):
        """Начать тест"""
        setup_window.destroy()
        
        self.test_mode = True
        self.test_type = test_type
        self.test_score = 0
        self.test_current_index = 0
        self.test_answers = []
        self.test_answer_checked = False
        
        # Выбираем случайные слова для теста
        self.test_words = random.sample(self.app.words_data, min(words_count, len(self.app.words_data)))
        
        # Скрываем режим изучения и показываем режим теста
        self.study_container.pack_forget()
        self.create_test_interface()
        self.show_test_question()
    
    def switch_to_study_mode(self):
        """Переключиться в режим изучения"""
        self.test_mode = False
        if self.test_container:
            self.test_container.pack_forget()
        self.study_container.pack(fill='both', expand=True)
        self.show_word()
    
    def create_test_interface(self):
        """Создание интерфейса теста"""
        # Очищаем контейнер теста
        for widget in self.test_container.winfo_children():
            widget.destroy()
        
        self.test_container.pack(fill='both', expand=True)
        
        # Прогресс теста
        self.test_progress_label = tk.Label(
            self.test_container,
            text="",
            font=FONTS['normal'],
            bg=COLORS['light'],
            fg=COLORS['dark']
        )
        self.test_progress_label.pack(pady=10)
        
        # Карточка вопроса
        question_frame = tk.Frame(self.test_container, bg='white', relief='raised', bd=2)
        question_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Инструкция
        self.test_instruction_label = tk.Label(
            question_frame,
            text="",
            font=FONTS['normal'],
            bg='white',
            fg=COLORS['gray']
        )
        self.test_instruction_label.pack(pady=10)
        
        # Вопрос
        self.test_question_label = tk.Label(
            question_frame,
            text="",
            font=FONTS['translation'],
            bg='white',
            fg=COLORS['dark'],
            wraplength=600
        )
        self.test_question_label.pack(pady=30)
        
        # Подсказка (транскрипция)
        self.test_hint_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 14),
            bg='white',
            fg=COLORS['gray']
        )
        self.test_hint_label.pack(pady=10)
        
        # Пример использования в режиме теста
        self.test_example_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 13, 'italic'),
            bg='white',
            fg=COLORS['primary'],
            wraplength=600
        )
        self.test_example_label.pack(pady=5)
        
        # Перевод примера в режиме теста
        self.test_example_translation_label = tk.Label(
            question_frame,
            text="",
            font=FONTS['normal'],
            bg='white',
            fg=COLORS['gray'],
            wraplength=600
        )
        self.test_example_translation_label.pack(pady=5)
        
        # Фрейм для ввода ответа
        answer_input_frame = tk.Frame(question_frame, bg='white')
        answer_input_frame.pack(pady=20)
        
        tk.Label(
            answer_input_frame,
            text="Ваш ответ:",
            font=FONTS['subtitle'],
            bg='white',
            fg=COLORS['dark']
        ).pack(pady=5)
        
        # Поле ввода ответа
        self.test_answer_entry = tk.Entry(
            answer_input_frame,
            font=FONTS['input'],
            width=30,
            justify='center'
        )
        self.test_answer_entry.pack(pady=10)
        self.test_answer_entry.bind('<Return>', lambda e: self.check_test_answer_input())
        
        # Результат проверки
        self.test_result_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 14, 'bold'),
            bg='white'
        )
        self.test_result_label.pack(pady=10)
        
        # Показать правильный ответ
        self.test_correct_answer_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 13),
            bg='white',
            fg=COLORS['success']
        )
        self.test_correct_answer_label.pack(pady=5)
        
        # Кнопки управления
        buttons_frame = tk.Frame(self.test_container, bg=COLORS['light'])
        buttons_frame.pack(pady=15)
        
        # Кнопка проверки
        self.test_check_button = tk.Button(
            buttons_frame,
            text="✓ Проверить",
            command=self.check_test_answer_input,
            font=FONTS['normal'],
            bg=COLORS['primary'],
            fg='white',
            padx=20,
            pady=10
        )
        self.test_check_button.pack(side='left', padx=5)
        
        # Кнопка следующего вопроса
        self.test_next_button = tk.Button(
            buttons_frame,
            text="Следующий вопрос →",
            command=self.next_test_question,
            font=FONTS['normal'],
            bg=COLORS['success'],
            fg='white',
            padx=20,
            pady=10,
            state='disabled'
        )
        self.test_next_button.pack(side='left', padx=5)
        
        # Кнопка пропуска
        self.test_skip_button = tk.Button(
            buttons_frame,
            text="Пропустить →",
            command=self.skip_question,
            font=FONTS['small'],
            bg=COLORS['gray'],
            fg='white',
            padx=15,
            pady=8
        )
        self.test_skip_button.pack(side='left', padx=5)
        
        # Кнопки для примеров в режиме теста
        example_buttons_frame = tk.Frame(self.test_container, bg=COLORS['light'])
        example_buttons_frame.pack(pady=10)
        
        tk.Button(
            example_buttons_frame,
            text="📝 Показать пример",
            command=self.show_example,
            font=FONTS['small'],
            bg=COLORS['teal'],
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            example_buttons_frame,
            text="🔄 Перевод примера",
            command=self.show_example_translation,
            font=FONTS['small'],
            bg=COLORS['info'],
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        # Счетчик правильных ответов
        self.test_score_label = tk.Label(
            self.test_container,
            text="Правильных ответов: 0",
            font=FONTS['normal'],
            bg=COLORS['light'],
            fg=COLORS['success']
        )
        self.test_score_label.pack(pady=5)
    
    def show_test_question(self):
        """Показать вопрос теста"""
        if self.test_current_index >= len(self.test_words):
            self.show_test_results()
            return
        
        self.test_answer_checked = False
        current_word = self.test_words[self.test_current_index]
        
        self.test_progress_label.config(
            text=f"Вопрос {self.test_current_index + 1} из {len(self.test_words)}"
        )
        
        # Определяем тип вопроса
        if self.test_type == "mixed":
            question_type = random.choice(["eng_to_rus", "rus_to_eng"])
        else:
            question_type = self.test_type
        
        self.current_question_type = question_type
        
        # Формируем вопрос
        if question_type == "eng_to_rus":
            self.test_instruction_label.config(text="Переведите на русский:")
            self.test_question_label.config(text=current_word['word'])
            self.test_hint_label.config(text=current_word['transcription'])
            self.current_correct_answer = current_word['translation']
        else:
            self.test_instruction_label.config(text="Переведите на английский:")
            self.test_question_label.config(text=current_word['translation'])
            self.test_hint_label.config(text="")
            self.current_correct_answer = current_word['word']
        
        # ИСПРАВЛЕНИЕ: Очищаем поле ввода и результаты
        # Сначала включаем, потом очищаем
        self.test_answer_entry.config(state='normal')
        self.test_answer_entry.delete(0, tk.END)
        self.test_answer_entry.config(bg='white')
        
        self.test_result_label.config(text="")
        self.test_correct_answer_label.config(text="")
        
        # Очищаем примеры
        self.test_example_label.config(text="")
        self.test_example_translation_label.config(text="")
        
        # Настраиваем кнопки
        self.test_check_button.config(state='normal')
        self.test_next_button.config(state='disabled')
        self.test_skip_button.config(state='normal')
        
        # Фокус на поле ввода
        self.test_answer_entry.focus()
        
        self.test_score_label.config(
            text=f"Правильных ответов: {self.test_score}/{self.test_current_index}"
        )
    
    def check_test_answer_input(self):
        """Проверка введенного ответа в тесте"""
        if self.test_answer_checked:
            return
        
        user_answer = self.test_answer_entry.get().strip()
        
        if not user_answer:
            messagebox.showwarning("Внимание", "Введите ответ!")
            return
        
        self.test_answer_checked = True
        
        # Используем улучшенную проверку с поддержкой вариантов
        from utils.helpers import check_answer_match, format_correct_answer
        
        is_correct = check_answer_match(user_answer, self.current_correct_answer)
        
        self.test_answers.append({
            'word': self.test_words[self.test_current_index],
            'user_answer': user_answer,
            'correct_answer': self.current_correct_answer,
            'is_correct': is_correct,
            'question_type': self.current_question_type
        })
        
        if is_correct:
            self.test_score += 1
            self.test_result_label.config(text="✅ Правильно!", fg=COLORS['success'])
            self.test_answer_entry.config(bg='#d4edda')
        else:
            self.test_result_label.config(text="❌ Неправильно", fg=COLORS['danger'])
            # Используем форматирование для отображения всех вариантов
            formatted_answer = format_correct_answer(self.current_correct_answer)
            self.test_correct_answer_label.config(
                text=f"Правильный ответ: {formatted_answer}"
            )
            self.test_answer_entry.config(bg='#f8d7da')
        
        self.test_score_label.config(
            text=f"Правильных ответов: {self.test_score}/{self.test_current_index + 1}"
        )
        
        self.test_answer_entry.config(state='disabled')
        self.test_check_button.config(state='disabled')
        self.test_skip_button.config(state='disabled')
        
        self.test_next_button.config(state='normal')
        self.test_next_button.focus()
    
    def skip_question(self):
        """Пропустить вопрос"""
        if self.test_answer_checked:
            return
        
        self.test_answer_checked = True
        
        self.test_answers.append({
            'word': self.test_words[self.test_current_index],
            'user_answer': '',
            'correct_answer': self.current_correct_answer,
            'is_correct': False,
            'question_type': self.current_question_type
        })
        
        self.test_result_label.config(text="⏭️ Вопрос пропущен", fg=COLORS['warning'])
        self.test_correct_answer_label.config(
            text=f"Правильный ответ: {self.current_correct_answer}"
        )
        
        self.parent.after(2000, self.next_test_question)
    
    def next_test_question(self):
        """Следующий вопрос теста"""
        # Сбрасываем флаг
        self.test_answer_checked = False
        
        # ИСПРАВЛЕНИЕ: Сначала включаем поле, потом очищаем
        self.test_answer_entry.config(state='normal')  # Включаем поле
        self.test_answer_entry.delete(0, tk.END)       # Очищаем содержимое
        self.test_answer_entry.config(bg='white')      # Сбрасываем цвет
        
        self.test_current_index += 1
        self.show_test_question()
    
    def show_test_results(self):
        """Показать результаты теста"""
        # Очищаем контейнер
        for widget in self.test_container.winfo_children():
            widget.destroy()
        
        # Заголовок результатов
        tk.Label(
            self.test_container,
            text="📊 Результаты теста",
            font=('Arial', 20, 'bold'),
            bg=COLORS['light'],
            fg=COLORS['dark']
        ).pack(pady=20)
        
        # Статистика
        percentage = (self.test_score / len(self.test_words)) * 100 if len(self.test_words) > 0 else 0
        
        result_frame = tk.Frame(self.test_container, bg='white', relief='raised', bd=2)
        result_frame.pack(pady=10, padx=20, fill='x')
        
        # Определяем цвет и эмодзи в зависимости от результата
        if percentage >= 90:
            color, emoji, message = COLORS['success'], '🎉', 'Превосходно!'
        elif percentage >= 80:
            color, emoji, message = '#2ecc71', '🌟', 'Отлично!'
        elif percentage >= 70:
            color, emoji, message = COLORS['primary'], '👍', 'Хорошо!'
        elif percentage >= 60:
            color, emoji, message = COLORS['warning'], '📚', 'Неплохо!'
        else:
            color, emoji, message = COLORS['danger'], '💪', 'Нужно больше практики!'
        
        tk.Label(
            result_frame,
            text=f"{emoji} {message}",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg=color
        ).pack(pady=10)
        
        tk.Label(
            result_frame,
            text=f"Правильных ответов: {self.test_score} из {len(self.test_words)}",
            font=FONTS['title'],
            bg='white'
        ).pack(pady=5)
        
        tk.Label(
            result_frame,
            text=f"Результат: {percentage:.1f}%",
            font=FONTS['title'],
            bg='white',
            fg=color
        ).pack(pady=5)
        
        # Детальные результаты
        tk.Label(
            self.test_container,
            text="📝 Подробные результаты:",
            font=FONTS['subtitle'],
            bg=COLORS['light'],
            fg=COLORS['dark']
        ).pack(pady=10)
        
        # Создаем область с прокруткой для детальных результатов
        details_frame = tk.Frame(self.test_container, bg='white', relief='raised', bd=1)
        details_frame.pack(pady=5, padx=20, fill='both', expand=True)
        
        text_widget = scrolledtext.ScrolledText(
            details_frame,
            font=FONTS['small'],
            wrap=tk.WORD,
            height=12,
            bg='white'
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Заполняем детальными результатами
        for i, result in enumerate(self.test_answers, 1):
            word_data = result['word']
            symbol = "✅" if result['is_correct'] else "❌"
            
            if result['question_type'] == 'eng_to_rus':
                question = f"{word_data['word']} {word_data['transcription']}"
            else:
                question = word_data['translation']
            
            text_widget.insert(tk.END, f"{i}. {question}\n", "question")
            
            if result['is_correct']:
                text_widget.insert(tk.END, f"   {symbol} Ваш ответ: {result['user_answer']}\n", "correct")
            else:
                if result['user_answer']:
                    text_widget.insert(tk.END, f"   {symbol} Ваш ответ: {result['user_answer']}\n", "wrong")
                else:
                    text_widget.insert(tk.END, f"   {symbol} Вопрос пропущен\n", "skipped")
                text_widget.insert(tk.END, f"   ✓ Правильный ответ: {result['correct_answer']}\n", "correct_answer")
            
            # Показываем примеры в результатах
            if word_data.get('example'):
                text_widget.insert(tk.END, f"   💡 Пример: {word_data['example']}\n", "example")
                if word_data.get('example_translation'):
                    text_widget.insert(tk.END, f"   📖 Перевод: {word_data['example_translation']}\n", "example_trans")
            
            text_widget.insert(tk.END, "\n")
        
        # Настройка тегов для цветного текста
        text_widget.tag_config("question", foreground=COLORS['dark'], font=(FONTS['small'][0], FONTS['small'][1], 'bold'))
        text_widget.tag_config("correct", foreground=COLORS['success'])
        text_widget.tag_config("wrong", foreground=COLORS['danger'])
        text_widget.tag_config("skipped", foreground=COLORS['warning'])
        text_widget.tag_config("correct_answer", foreground=COLORS['success'], font=(FONTS['small'][0], FONTS['small'][1], 'italic'))
        text_widget.tag_config("example", foreground=COLORS['primary'], font=(FONTS['tiny'][0], FONTS['tiny'][1], 'italic'))
        text_widget.tag_config("example_trans", foreground=COLORS['gray'], font=FONTS['tiny'])
        
        text_widget.config(state='disabled')
        
        # Кнопки действий
        button_frame = tk.Frame(self.test_container, bg=COLORS['light'])
        button_frame.pack(pady=15)
        
        tk.Button(
            button_frame,
            text="🔄 Пройти тест заново",
            command=self.restart_test,
            font=FONTS['normal'],
            bg=COLORS['primary'],
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="🎯 Новый тест",
            command=self.show_test_setup,
            font=FONTS['normal'],
            bg=COLORS['orange'],
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="📖 Вернуться к изучению",
            command=self.switch_to_study_mode,
            font=FONTS['normal'],
            bg=COLORS['purple'],
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        # Обновляем общую статистику
        self.app.total_attempts += len(self.test_words)
        self.app.score += self.test_score
        self.app.update_stats()
        self.app.save_progress()
    
    def restart_test(self):
        """Перезапустить тот же тест"""
        self.test_current_index = 0
        self.test_score = 0
        self.test_answers = []
        self.test_answer_checked = False
        random.shuffle(self.test_words)
        self.create_test_interface()
        self.show_test_question()