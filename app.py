"""
Основной класс приложения
"""

import tkinter as tk
from tkinter import ttk
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, COLORS, FONTS
from data.loader import DataLoader
from data.progress import ProgressManager
from data.database import LearningDatabase
from ui.words_tab import WordsTab
from ui.exercises_tab import ExercisesTab
from ui.rules_tab import RulesTab
from ui.stats_tab import StatsTab
from ui.today_tab import TodayTab
from llm.providers import ExplanationService, OllamaProvider
from ui.settings_tab import SettingsTab

class EnglishLearningApp:
    """Главный класс приложения для изучения английского"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Загрузка данных
        source_words = DataLoader.load_words()
        source_exercises = DataLoader.load_exercises()
        source_rules = DataLoader.load_rules()
        self.db = LearningDatabase()
        self.db.initialize(source_words, source_exercises, source_rules)
        self.words_data = self.db.get_words()
        self.exercises_data = self.db.get_exercises()
        self.rules_data = self.db.get_rules()
        self.explanation_service = ExplanationService(OllamaProvider(
            model=self.db.get_setting('ollama_model', 'qwen3:4b')
        ))
        
        # Загрузка прогресса
        self.progress_data = ProgressManager.load()
        self.db.import_legacy_progress(
            self.progress_data.get('score', 0), self.progress_data.get('total_attempts', 0))
        overall = self.db.get_learning_stats()['overall']
        self.score = overall['correct']
        self.total_attempts = overall['attempts']
        
        # Создание интерфейса
        self.create_widgets()
        self.apply_theme(self.db.get_setting('theme', 'light'))
        
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
        self.header_frame = tk.Frame(self.root, bg=COLORS['dark'], height=60)
        self.header_frame.pack(fill='x')
        self.header_frame.pack_propagate(False)
        
        self.header_label = tk.Label(
            self.header_frame,
            text="📚 English Learning Application",
            font=FONTS['header'],
            bg=COLORS['dark'],
            fg='white'
        )
        self.header_label.pack(pady=15)
    
    def create_tabs(self):
        """Создание всех вкладок"""
        today_frame = tk.Frame(self.notebook, bg=COLORS['light'])
        self.notebook.add(today_frame, text='🎯 Сегодня')
        self.today_tab = TodayTab(today_frame, self)

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

        settings_frame = tk.Frame(self.notebook, bg=COLORS['light'])
        self.notebook.add(settings_frame, text='⚙ Настройки')
        self.settings_tab = SettingsTab(settings_frame, self)
    
    def update_stats(self):
        """Обновление статистики"""
        self.stats_tab.update()
        self.today_tab.refresh()

    def apply_theme(self, theme):
        """Применить палитру к уже созданным стандартным Tk-виджетам."""
        dark = theme == 'dark'
        background = '#1f2933' if dark else COLORS['light']
        surface = '#273746' if dark else 'white'
        foreground = '#f4f6f7' if dark else COLORS['dark']
        self.root.configure(bg=background)

        def recolor(widget):
            try:
                current = widget.cget('bg')
                if isinstance(widget, (tk.Frame, tk.Label, tk.Radiobutton, tk.Checkbutton)):
                    widget.configure(bg=surface if current in ('white', '#273746') else background)
                    if not isinstance(widget, tk.Frame):
                        current_fg = widget.cget('fg')
                        if current_fg in ('black', '#2c3e50', '#34495e', '#f4f6f7'):
                            widget.configure(fg=foreground)
                if isinstance(widget, (tk.Entry, tk.Listbox, tk.Text)):
                    widget.configure(bg=surface, fg=foreground, insertbackground=foreground)
            except tk.TclError:
                pass
            for child in widget.winfo_children():
                recolor(child)

        recolor(self.root)
        self.header_frame.configure(bg=COLORS['dark'])
        self.header_label.configure(bg=COLORS['dark'], fg='white')
