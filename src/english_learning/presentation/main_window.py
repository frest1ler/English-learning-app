"""Top-level window and stable page navigation."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget,
    QVBoxLayout, QWidget,
)

from english_learning import __version__
from english_learning.application.context import ApplicationContext
from english_learning.presentation.theme import stylesheet
from english_learning.application.learning_service import LearningService
from english_learning.presentation.pages import PAGE_FACTORIES


PAGE_NAMES = (
    ("Сегодня", "Сегодняшний персональный план"),
    ("Словарь", "Слова, поиск и интервальное повторение"),
    ("Практика", "Грамматика, перевод и умные тренировки"),
    ("Правила", "Грамматический справочник"),
    ("Материалы", "Библиотека и генерация Qwen"),
    ("Прогресс", "Подробная статистика обучения"),
    ("Настройки", "Интерфейс, данные и локальный AI"),
)


class PlaceholderPage(QWidget):
    def __init__(self, title: str, description: str):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        heading = QLabel(title); heading.setObjectName("title")
        description_label = QLabel(description); description_label.setObjectName("muted")
        card = QFrame(); card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(QLabel("Экран подключён к новой оболочке PySide6."))
        card_layout.addStretch()
        layout.addWidget(heading); layout.addWidget(description_label); layout.addSpacing(16)
        layout.addWidget(card, 1)


class MainWindow(QMainWindow):
    def __init__(self, context: ApplicationContext):
        super().__init__()
        self.context = context
        self.setWindowTitle(f"English Learning App {__version__}")
        self.resize(1180, 760)
        self.setMinimumSize(900, 620)
        central = QWidget(); root = QHBoxLayout(central); root.setContentsMargins(12, 12, 12, 12)
        sidebar = QFrame(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(210)
        navigation = QVBoxLayout(sidebar)
        brand = QLabel("English\nLearning")
        brand.setObjectName("title"); brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        navigation.addWidget(brand); navigation.addSpacing(16)
        self.stack = QStackedWidget(); self.buttons = []
        for index, (name, description) in enumerate(PAGE_NAMES):
            button = QPushButton(name); button.setObjectName("nav"); button.setCheckable(True)
            button.clicked.connect(lambda checked=False, page=index: self.select_page(page))
            navigation.addWidget(button); self.buttons.append(button)
            page = PAGE_FACTORIES[index](LearningService(context.database))
            page.changed.connect(self.refresh_pages)
            if hasattr(page, "theme_changed"):
                page.theme_changed.connect(self.apply_theme)
            self.stack.addWidget(page)
        navigation.addStretch()
        self.ai_status = QLabel("AI: проверка не выполнена")
        self.ai_status.setObjectName("muted"); self.ai_status.setWordWrap(True)
        navigation.addWidget(self.ai_status)
        root.addWidget(sidebar); root.addWidget(self.stack, 1)
        self.setCentralWidget(central)
        self.select_page(0)
        self.apply_saved_theme()

    def select_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for button_index, button in enumerate(self.buttons):
            button.setChecked(button_index == index)

    def apply_saved_theme(self) -> None:
        self.setStyleSheet(stylesheet(self.context.database.get_setting("theme", "light")))

    def apply_theme(self, theme: str) -> None:
        self.setStyleSheet(stylesheet(theme))

    def refresh_pages(self) -> None:
        for index in range(self.stack.count()):
            self.stack.widget(index).refresh()
