"""
Основной класс приложения
"""

import tkinter as tk
from tkinter import ttk
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, COLORS, FONTS
from data.loader import DataLoader
from data.progress import ProgressManager
from ui.words_tab import WordsTab
from ui.exercises_tab import ExercisesTab
from ui.rules_tab import RulesTab
from ui.stats_tab import StatsTab

class EnglishLearningApp:
    """Главный класс приложения для изучения английского"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Загрузка данных
        self.words_data = DataLoader.load_words()
        self.exercises_data = DataLoader.load_exercises()
        self.rules_data = DataLoader.load_rules()
        
        # Загрузка прогресса
        self.progress_data = ProgressManager.load()
        self.score = self.progress_data.get('score', 0)
        self.total_attempts = self.progress_data.get('total_attempts', 0)
        
        # Создание интерфейса
        self.create_widgets()
        
        # Сохранение прогресса при закрытии
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Привязка горячих клавиш
        self.bind_hotkeys()
    
    def setup_window(self):
        """Настройка главного окна"""
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=COLORS['light'])
    
    def bind_hotkeys(self):
        """Привязка горячих клавиш"""
        self.root.bind('<Control-s>', lambda e: self.save_progress())
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        self.save_progress()
        self.root.destroy()
    
    def save_progress(self):
        """Сохранение прогресса"""
        ProgressManager.save(self.score, self.total_attempts)
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Стиль
        style = ttk.Style()
        style.theme_use('clam')
        
        # Заголовок
        self.create_header()
        
        # Notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создание вкладок
        self.create_tabs()
    
    def create_header(self):
        """Создание заголовка приложения"""
        header_frame = tk.Frame(self.root, bg=COLORS['dark'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="📚 English Learning Application",
            font=FONTS['header'],
            bg=COLORS['dark'],
            fg='white'
        ).pack(pady=15)
    
    def create_tabs(self):
        """Создание всех вкладок"""
        # Вкладка изучения слов (с встроенным тестом)
        words_frame = tk.Frame(self.notebook, bg=COLORS['light'])
        self.notebook.add(words_frame, text='📖 Словарь')
        self.words_tab = WordsTab(words_frame, self)
        
        # Вкладка упражнений
        exercises_frame = tk.Frame(self.notebook, bg=COLORS['light'])
        self.notebook.add(exercises_frame, text='✏️ Упражнения')
        self.exercises_tab = ExercisesTab(exercises_frame, self)
        
        # Вкладка правил
        rules_frame = tk.Frame(self.notebook, bg=COLORS['light'])
        self.notebook.add(rules_frame, text='📋 Правила')
        self.rules_tab = RulesTab(rules_frame, self)
        
        # Вкладка статистики
        stats_frame = tk.Frame(self.notebook, bg=COLORS['light'])
        self.notebook.add(stats_frame, text='📊 Статистика')
        self.stats_tab = StatsTab(stats_frame, self)
    
    def update_stats(self):
        """Обновление статистики"""
        self.stats_tab.update()