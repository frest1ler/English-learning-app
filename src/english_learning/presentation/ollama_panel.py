"""Non-blocking Ollama setup panel used by desktop settings."""

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton, QWidget

from english_learning.infrastructure.ollama_client import OllamaClient


class OllamaWorker(QThread):
    status_ready = Signal(object)
    progress_ready = Signal(int, str)
    failed = Signal(str)

    def __init__(self, url: str, model: str, pull: bool = False, parent=None):
        super().__init__(parent)
        self.url, self.model, self.should_pull = url, model, pull

    def run(self) -> None:
        try:
            client = OllamaClient(self.url)
            if self.should_pull:
                client.pull(self.model, self.progress_ready.emit)
            self.status_ready.emit(client.status(self.model))
        except (ValueError, RuntimeError) as error:
            self.failed.emit(str(error))


class OllamaPanel(QWidget):
    status_changed = Signal(str)

    def __init__(self, service, parent=None):
        super().__init__(parent); self.service = service; self.worker = None
        layout = QFormLayout(self)
        self.url = QLineEdit(str(service.setting("ollama_url", "http://127.0.0.1:11434")))
        self.model = QLineEdit(str(service.setting("ollama_model", "qwen3:4b")))
        self.status = QLabel("Проверка ещё не выполнялась"); self.status.setWordWrap(True)
        self.progress = QProgressBar(); self.progress.hide()
        actions = QHBoxLayout(); self.check_button = QPushButton("Проверить")
        self.pull_button = QPushButton("Скачать модель"); install = QPushButton("Скачать Ollama")
        self.check_button.clicked.connect(self.check); self.pull_button.clicked.connect(self.pull)
        install.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://ollama.com/download")))
        for button in (self.check_button, self.pull_button, install): actions.addWidget(button)
        layout.addRow("Адрес", self.url); layout.addRow("Модель", self.model)
        layout.addRow(actions); layout.addRow(self.status); layout.addRow(self.progress)

    def persist(self) -> None:
        self.service.save_setting("ollama_url", self.url.text().strip())
        self.service.save_setting("ollama_model", self.model.text().strip() or "qwen3:4b")

    def check(self) -> None:
        self._start(False)

    def pull(self) -> None:
        self.progress.setValue(0); self.progress.show(); self._start(True)

    def _start(self, pull: bool) -> None:
        if self.worker and self.worker.isRunning():
            return
        self.persist(); self._busy(True)
        self.worker = OllamaWorker(self.url.text().strip(), self.model.text().strip(), pull, self)
        self.worker.status_ready.connect(self._show_status)
        self.worker.progress_ready.connect(self._show_progress)
        self.worker.failed.connect(self._show_error)
        self.worker.finished.connect(lambda: self._busy(False))
        self.worker.start()

    def _busy(self, busy: bool) -> None:
        self.check_button.setEnabled(not busy); self.pull_button.setEnabled(not busy)

    def _show_status(self, status) -> None:
        suffix = f" · Ollama {status.version}" if status.version else ""
        self.status.setText(status.message + suffix)
        self.progress.setValue(100 if status.state == "ready" else self.progress.value())
        self.status_changed.emit(status.message)

    def _show_progress(self, value: int, status: str) -> None:
        self.progress.setValue(value); self.status.setText(status or "Загрузка…")

    def _show_error(self, message: str) -> None:
        self.status.setText(f"Ошибка: {message}"); self.status_changed.emit("Ollama недоступна")
