"""
Конфигурация приложения
"""

import os

# Настройки окна
WINDOW_WIDTH = 950
WINDOW_HEIGHT = 750
WINDOW_TITLE = "English Learning App"

# Пути к папкам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILES_DIR = os.path.join(BASE_DIR, 'data_files')

# Создаем папку для данных, если её нет
os.makedirs(DATA_FILES_DIR, exist_ok=True)

# Файлы данных
DATA_FILES = {
    'words': os.path.join(DATA_FILES_DIR, 'words.txt'),
    'exercises': os.path.join(DATA_FILES_DIR, 'exercises.txt'),
    'rules': os.path.join(DATA_FILES_DIR, 'rules.txt'),
    'progress': os.path.join(DATA_FILES_DIR, 'progress.json')
}

# Цвета
COLORS = {
    'primary': '#3498db',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#2980b9',
    'dark': '#2c3e50',
    'light': '#ecf0f1',
    'white': '#ffffff',
    'gray': '#7f8c8d',
    'purple': '#9b59b6',
    'orange': '#e67e22',
    'teal': '#16a085'
}

# Настройки упражнений
EXERCISE_MIN_COUNT = 5
EXERCISE_MAX_COUNT = 30
EXERCISE_DEFAULT_COUNT = 10

# Настройки теста
TEST_MIN_WORDS = 5
TEST_MAX_WORDS = 50
TEST_DEFAULT_WORDS = 10

# Шрифты
FONTS = {
    'header': ('Arial', 20, 'bold'),
    'title': ('Arial', 16, 'bold'),
    'subtitle': ('Arial', 14, 'bold'),
    'normal': ('Arial', 12),
    'small': ('Arial', 11),
    'tiny': ('Arial', 10),
    'word': ('Arial', 32, 'bold'),
    'translation': ('Arial', 24),
    'transcription': ('Arial', 18),
    'input': ('Arial', 16),
    'example': ('Arial', 14, 'italic')
}