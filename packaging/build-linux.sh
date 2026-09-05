#!/usr/bin/env sh
set -eu
python -m PyInstaller --clean --noconfirm packaging/english-learning.spec
tar -C dist -czf dist/EnglishLearningApp-linux-x86_64.tar.gz EnglishLearningApp
