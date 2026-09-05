"""First-run explanation; AI remains optional."""

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout


class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добро пожаловать")
        self.setMinimumWidth(480)
        layout = QVBoxLayout(self)
        title = QLabel("English Learning App")
        title.setObjectName("title")
        layout.addWidget(title)
        text = QLabel(
            "Ваш прогресс хранится только на этом компьютере.\n\n"
            "Основные занятия работают без интернета. Ollama и Qwen можно подключить позже "
            "для объяснений, проверки перевода и генерации материалов."
        )
        text.setWordWrap(True)
        layout.addWidget(text)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Начать обучение")
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
