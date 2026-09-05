"""PySide6 application entry point."""

import os
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from english_learning.application.context import ApplicationContext
from english_learning.presentation.main_window import MainWindow
from english_learning.presentation.welcome import WelcomeDialog


def build_window() -> tuple[QApplication, MainWindow]:
    application = QApplication.instance() or QApplication(sys.argv)
    application.setApplicationName("English Learning App")
    application.setOrganizationName("EnglishLearningApp")
    context = ApplicationContext.create()
    window = MainWindow(context)
    if (not context.database.get_setting("welcome_completed", False)
            and os.environ.get("ENGLISH_LEARNING_SKIP_WELCOME") != "1"):
        welcome = WelcomeDialog(window)
        if welcome.exec():
            context.database.set_setting("welcome_completed", True)
    return application, window


def main() -> int:
    application, window = build_window()
    window.show()
    if os.environ.get("ENGLISH_LEARNING_SMOKE_TEST") == "1":
        QTimer.singleShot(100, application.quit)
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
