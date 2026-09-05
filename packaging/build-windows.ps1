$ErrorActionPreference = "Stop"
python -m PyInstaller --clean --noconfirm packaging/english-learning.spec
if (Get-Command iscc -ErrorAction SilentlyContinue) {
    iscc packaging/windows/EnglishLearningApp.iss
} else {
    Compress-Archive -Force dist/EnglishLearningApp dist/EnglishLearningApp-windows-x64.zip
}
