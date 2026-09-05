# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

root = Path(SPECPATH).parent
migrations = root / "src" / "english_learning" / "infrastructure" / "database" / "migrations"

a = Analysis(
    [str(root / "main.py")],
    pathex=[str(root), str(root / "src")],
    binaries=[],
    datas=[
        (str(root / "data_files" / "words.txt"), "resources/seed"),
        (str(root / "data_files" / "exercises.txt"), "resources/seed"),
        (str(root / "data_files" / "rules.txt"), "resources/seed"),
        (str(root / "data_files" / "learning.db"), "resources/seed"),
        (str(migrations), "english_learning/infrastructure/database/migrations"),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True,
    name="EnglishLearningApp", debug=False, bootloader_ignore_signals=False,
    strip=False, upx=True, console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=True, name="EnglishLearningApp")
