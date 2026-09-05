# English Learning App

Локальное настольное приложение для изучения английского языка на Windows и Linux. Регистрация не нужна: словарь, упражнения, настройки и прогресс хранятся на компьютере пользователя. Ollama с моделью Qwen подключается опционально.

## Что уже работает

- персональное занятие на 5–20 минут;
- словарь, поиск, добавление слов и интервальное повторение;
- грамматические задания и перевод с русского на английский;
- режим, скрывающий название грамматического времени до ответа;
- справочник правил и библиотека материалов;
- статистика по словам, ответам и грамматическим темам;
- светлая и тёмная темы;
- резервная копия SQLite из настроек;
- проверка Ollama и загрузка `qwen3:4b` прямо из настроек;
- встроенная начальная база слов, правил и упражнений;
- безопасные миграции БД с автоматической резервной копией.

Основные учебные функции работают без интернета и Ollama.

## Обычный запуск из исходников

Нужен Python 3.10 или новее.

### Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python main.py
```

Или используйте `make setup` и `make run`. Для некоторых дистрибутивов могут понадобиться системные библиотеки Qt; их полный список есть в [infra/docker/Dockerfile](infra/docker/Dockerfile).

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python main.py
```

При первом запуске приложение копирует исходные материалы в пользовательскую БД. Файлы проекта при этом не изменяются.

## Готовое приложение

Пользователю Python не нужен. Распакуйте архив своей операционной системы и запустите:

- Linux: `EnglishLearningApp/EnglishLearningApp`;
- Windows: `EnglishLearningApp\EnglishLearningApp.exe`;
- при наличии Windows-инсталлятора — `EnglishLearningApp-Setup-0.4.0.exe`.

Сборки одной ОС нельзя создавать на другой: Linux-артефакт собирается на Linux, Windows-артефакт — на Windows. Workflow `Release` делает обе сборки автоматически при ручном запуске или публикации тега `v*`.

## Ollama и Qwen

Ollama бесплатна для локального запуска. Модель выполняется на компьютере пользователя, поэтому API-оплаты нет. Стартовый вариант проекта — `qwen3:4b`.

1. Установите Ollama с [официальной страницы](https://ollama.com/download) или кнопкой «Скачать Ollama» в настройках.
2. Запустите Ollama.
3. В приложении откройте «Настройки» → «Проверить».
4. Если модели нет, нажмите «Скачать модель» и дождитесь 100%.

То же из терминала:

```bash
ollama pull qwen3:4b
```

По умолчанию используется `http://127.0.0.1:11434`. Адрес и модель можно изменить в настройках. Проверка и загрузка выполняются в отдельном потоке и не замораживают интерфейс.

## Docker для разработчика

Docker используется для воспроизводимых тестов и headless-проверки интерфейса, а не как основной способ показа desktop GUI.

```bash
docker compose build test gui-smoke
docker compose run --rm test
docker compose run --rm gui-smoke
```

Запуск Ollama в Docker на CPU:

```bash
docker compose --profile ai up -d ollama
docker compose --profile ai exec ollama ollama pull qwen3:4b
```

Для NVIDIA GPU:

```bash
docker compose -f compose.yaml -f compose.nvidia.yaml --profile ai up -d ollama
```

GPU-вариант требует установленного NVIDIA Container Toolkit.

## Тесты и сборка

```bash
make check
make package
```

Ручная Linux-сборка с архивом:

```bash
PATH="$PWD/.venv/bin:$PATH" ./packaging/build-linux.sh
```

Windows PowerShell:

```powershell
.\packaging\build-windows.ps1
```

Если в Windows доступен Inno Setup (`iscc`), скрипт создаст инсталлятор. Без него будет создан ZIP. Спецификация PyInstaller включает исходные учебные материалы и SQL-миграции.

## Где хранятся данные

Рабочая БД, логи и резервные копии лежат в стандартном пользовательском каталоге приложения, который выбирает `platformdirs`. Это позволяет устанавливать обновления, не перезаписывая прогресс.

Для разработки каталог можно задать явно:

```bash
ENGLISH_LEARNING_DATA_DIR=/tmp/english-learning .venv/bin/python main.py
```

| Переменная | Назначение |
|---|---|
| `ENGLISH_LEARNING_DATA_DIR` | каталог пользовательских данных |
| `ENGLISH_LEARNING_RESOURCE_DIR` | каталог исходных материалов |
| `ENGLISH_LEARNING_OLLAMA_URL` | URL Ollama |
| `ENGLISH_LEARNING_OLLAMA_MODEL` | модель, по умолчанию `qwen3:4b` |
| `ENGLISH_LEARNING_LOG_LEVEL` | уровень логирования |

Перед каждой миграцией существующей БД создаётся timestamp-копия в каталоге `backups`. Дополнительную копию можно сохранить через настройки.

## Архитектура

```text
main.py                         вход в desktop-приложение
src/english_learning/
├── presentation/              PySide6: окно, страницы, тема, Ollama UI
├── application/               сценарии приложения и фасад учебной логики
└── infrastructure/            пути, конфигурация, логи, БД, миграции, Ollama
data/                           SQLite-репозиторий и загрузчики
learning/                       подбор заданий и учебные алгоритмы
llm/                            провайдеры и генерация контента
data_files/                     read-only начальные материалы
tests/                          unit и integration-тесты
infra/docker/                   воспроизводимое Linux-окружение
packaging/                      PyInstaller и Windows installer
infra/github-actions-disabled/  временно отключённые шаблоны CI и release
```

UI работает через `LearningService` и не выполняет SQL напрямую. Ollama вынесена за границу приложения: её отсутствие не мешает словарю, тренировкам и статистике.

Старый Tkinter-вход временно сохранён в `legacy_main.py` для диагностики миграции; основной запуск — только `main.py`.

## Проверки CI

Шаблоны CI и Release временно лежат вне `.github/workflows`, поэтому GitHub Actions не запускаются. После настройки токена с правом `workflow` их можно вернуть в `.github/workflows`. Они рассчитаны на Python 3.10/3.12, Linux/Windows и headless smoke-test PySide6. Локальный минимальный набор:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q main.py legacy_main.py src data learning llm tests
```

Личная БД, прогресс, `.venv`, Docker/PyInstaller-артефакты и кеши исключены из Git.
