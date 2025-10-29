"""
English Learning Application
Точка входа в приложение
"""

import tkinter as tk
from app import EnglishLearningApp

def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = EnglishLearningApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()