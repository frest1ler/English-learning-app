"""Repository entry point for the PySide6 desktop application."""

from pathlib import Path
import sys


SOURCE_DIRECTORY = Path(__file__).resolve().parent / "src"
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from english_learning.main import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
