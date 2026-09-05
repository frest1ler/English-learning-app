"""Legacy Tkinter entry point kept temporarily for migration diagnostics."""

import tkinter as tk

from app import EnglishLearningApp


def main() -> None:
    root = tk.Tk()
    EnglishLearningApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
