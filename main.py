import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import json
from datetime import datetime
import os

class EnglishLearningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("English Learning App")
        self.root.geometry("950x750")
        self.root.configure(bg='#f0f0f0')
        
        # Загрузка данных
        self.words_data = self.load_words()
        self.exercises_data = self.load_exercises()
        self.rules_data = self.load_rules()
        
        # Загрузка прогресса
        self.progress_data = self.load_progress()
        
        # Переменные для отслеживания прогресса
        self.current_word_index = 0
        self.current_exercise = None
        self.current_rule = None
        self.score = self.progress_data.get('score', 0)
        self.total_attempts = self.progress_data.get('total_attempts', 0)
        
        # Переменные для упражнений
        self.selected_topics = []
        self.mixed_exercises = []
        self.current_exercise_index = 0
        self.exercise_results = []
        
        # Переменные для теста
        self.test_mode = False
        self.test_words = []
        self.test_current_index = 0
        self.test_score = 0
        self.test_answers = []
        self.test_type = "eng_to_rus"
        
        # Флаги для предотвращения множественных проверок
        self.answer_checked = False
        self.test_answer_checked = False
        
        # Создание интерфейса
        self.create_widgets()
        
        # Сохранение прогресса при закрытии
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Привязка горячих клавиш
        self.bind_hotkeys()
    
    def bind_hotkeys(self):
        """Привязка горячих клавиш"""
        self.root.bind('<Control-s>', lambda e: self.save_progress())
    
    def load_progress(self):
        """Загрузка сохраненного прогресса"""
        try:
            if os.path.exists('progress.json'):
                with open('progress.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки прогресса: {e}")
        return {'score': 0, 'total_attempts': 0}
    
    def save_progress(self):
        """Сохранение прогресса"""
        try:
            progress = {
                'score': self.score,
                'total_attempts': self.total_attempts,
                'last_session': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            with open('progress.json', 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            print("Прогресс сохранен")
        except Exception as e:
            print(f"Ошибка сохранения прогресса: {e}")
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        self.save_progress()
        self.root.destroy()
    
    def get_default_words(self):
        """Получить базовый набор слов"""
        return [
            {
                'word': 'hello',
                'translation': 'привет',
                'transcription': '[həˈləʊ]',
                'example': 'Hello! How are you today?',
                'example_translation': 'Привет! Как дела сегодня?'
            },
            {
                'word': 'world',
                'translation': 'мир',
                'transcription': '[wɜːld]',
                'example': 'We live in a beautiful world.',
                'example_translation': 'Мы живем в прекрасном мире.'
            },
            {
                'word': 'learn',
                'translation': 'учиться',
                'transcription': '[lɜːn]',
                'example': 'I want to learn English.',
                'example_translation': 'Я хочу учить английский.'
            }
        ]
    
    def load_words(self):
        """Загрузка слов из файла с примерами использования"""
        try:
            with open('words.txt', 'r', encoding='utf-8') as f:
                words = []
                line_number = 0
                for line in f:
                    line_number += 1
                    if line.strip():
                        parts = line.strip().split('|')
                        if len(parts) >= 3:
                            word_dict = {
                                'word': parts[0].strip(),
                                'translation': parts[1].strip(),
                                'transcription': parts[2].strip(),
                                'example': parts[3].strip() if len(parts) > 3 else '',
                                'example_translation': parts[4].strip() if len(parts) > 4 else ''
                            }
                            words.append(word_dict)
                        else:
                            print(f"Предупреждение: неверный формат в строке {line_number}")
                return words if words else self.get_default_words()
        except FileNotFoundError:
            self.create_sample_files()
            return self.load_words()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки слов: {e}")
            return self.get_default_words()
    
    def load_exercises(self):
        """Загрузка упражнений из файла"""
        try:
            with open('exercises.txt', 'r', encoding='utf-8') as f:
                exercises = {}
                current_rule = None
                
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith('###'):
                        current_rule = line.replace('###', '').strip()
                        if current_rule not in exercises:
                            exercises[current_rule] = []
                    elif current_rule and '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            exercises[current_rule].append({
                                'rule': current_rule,
                                'sentence': parts[0].strip(),
                                'answer': parts[1].strip(),
                                'hint': parts[2].strip() if len(parts) > 2 else ''
                            })
                
                return exercises
        except FileNotFoundError:
            self.create_sample_files()
            return self.load_exercises()
    
    def load_rules(self):
        """Загрузка правил из файла"""
        try:
            with open('rules.txt', 'r', encoding='utf-8') as f:
                rules = []
                current_rule = {'title': '', 'content': ''}
                
                for line in f:
                    if line.startswith('###'):
                        if current_rule['title']:
                            rules.append(current_rule)
                        current_rule = {'title': line.replace('###', '').strip(), 'content': ''}
                    else:
                        current_rule['content'] += line
                
                if current_rule['title']:
                    rules.append(current_rule)
                
                return rules
        except FileNotFoundError:
            return []
    
    def create_sample_files(self):
        """Создание примеров файлов"""
        # Создание файла со словами (теперь с примерами)
        with open('words.txt', 'w', encoding='utf-8') as f:
            f.write("""apple | яблоко | [ˈæpl] | I eat an apple every day. | Я ем яблоко каждый день.
book | книга | [bʊk] | This book is very interesting. | Эта книга очень интересная.
cat | кот | [kæt] | My cat likes to sleep. | Мой кот любит спать.
dog | собака | [dɒɡ] | The dog is playing in the garden. | Собака играет в саду.
house | дом | [haʊs] | We live in a big house. | Мы живем в большом доме.
water | вода | [ˈwɔːtə] | I drink water every morning. | Я пью воду каждое утро.
friend | друг | [frend] | She is my best friend. | Она моя лучшая подруга.
school | школа | [skuːl] | Children go to school every day. | Дети ходят в школу каждый день.
teacher | учитель | [ˈtiːtʃə] | Our teacher is very kind. | Наш учитель очень добрый.
student | студент | [ˈstjuːdənt] | He is a good student. | Он хороший студент.
computer | компьютер | [kəmˈpjuːtə] | I work on my computer. | Я работаю на компьютере.
phone | телефон | [fəʊn] | Can you answer the phone? | Можешь ответить на телефон?
city | город | [ˈsɪti] | London is a beautiful city. | Лондон - красивый город.
country | страна | [ˈkʌntri] | France is a wonderful country. | Франция - замечательная страна.
family | семья | [ˈfæmɪli] | I love my family. | Я люблю свою семью.
morning | утро | [ˈmɔːnɪŋ] | Good morning! How are you? | Доброе утро! Как дела?
evening | вечер | [ˈiːvnɪŋ] | We go for a walk in the evening. | Мы гуляем вечером.
night | ночь | [naɪt] | The stars shine at night. | Звезды светят ночью.
day | день | [deɪ] | Have a nice day! | Хорошего дня!
work | работа | [wɜːk] | I go to work by bus. | Я езжу на работу на автобусе.""")
        
        # Создание файла с упражнениями
        with open('exercises.txt', 'w', encoding='utf-8') as f:
            f.write("""### Present Simple
I ___ (work) in an office | work | Используйте базовую форму для I/you/we/they
She ___ (go) to school every day | goes | Добавьте -s для he/she/it
They ___ (play) football on Sundays | play | Базовая форма для they
He ___ (watch) TV in the evening | watches | Добавьте -es после ch
My sister ___ (study) English | studies | Измените y на ies
We ___ (live) in London | live | Базовая форма для we
The sun ___ (rise) in the east | rises | Факт - добавьте -s
Tom ___ (like) pizza | likes | He/she/it + глагол+s
I ___ (drink) coffee every morning | drink | Регулярное действие
The train ___ (leave) at 9 AM | leaves | Расписание - добавьте -s

### Past Simple
I ___ (visit) Paris last year | visited | Правильный глагол + ed
She ___ (buy) a new dress yesterday | bought | Неправильный глагол
They ___ (go) to the cinema last night | went | go → went
He ___ (write) a letter to his friend | wrote | write → wrote
We ___ (have) dinner at 7 PM | had | have → had
The children ___ (play) in the garden | played | Правильный глагол + ed
I ___ (see) him yesterday | saw | see → saw
She ___ (make) a cake for the party | made | make → made
They ___ (come) home late | came | come → came
He ___ (read) the book last week | read | read → read (произношение меняется)

### Future Simple
I ___ (call) you tomorrow | will call | will + базовая форма
She ___ (help) you with homework | will help | will + базовая форма
They ___ (arrive) next week | will arrive | will + базовая форма
It ___ (rain) tomorrow | will rain | Предсказание
We ___ (meet) at 5 PM | will meet | Планы на будущее
He ___ (be) happy to see you | will be | will + be
I ___ (finish) this work soon | will finish | Обещание
The concert ___ (start) at 8 PM | will start | Будущее событие
You ___ (love) this movie | will love | Предсказание
They ___ (travel) to Spain | will travel | Будущий план

### Present Continuous
I ___ (work) right now | am working | am + глагол+ing
She ___ (read) a book at the moment | is reading | is + глагол+ing
They ___ (play) football now | are playing | are + глагол+ing
We ___ (have) lunch | are having | are + глагол+ing
He ___ (sleep) | is sleeping | is + глагол+ing
The children ___ (watch) TV | are watching | are + глагол+ing
I ___ (learn) English this year | am learning | Временный процесс
She ___ (cook) dinner now | is cooking | Действие происходит сейчас
Look! It ___ (rain) | is raining | Действие в момент речи
They ___ (come) tomorrow | are coming | Запланированное будущее

### Past Continuous
I ___ (sleep) when you called | was sleeping | was + глагол+ing
They ___ (watch) TV at 8 PM yesterday | were watching | were + глагол+ing
She ___ (cook) when I arrived | was cooking | was + глагол+ing
We ___ (play) football all morning | were playing | Длительное действие в прошлом
He ___ (read) a book from 5 to 7 | was reading | was + глагол+ing
The birds ___ (sing) beautifully | were singing | were + глагол+ing
I ___ (wait) for you for an hour | was waiting | Процесс в прошлом
It ___ (rain) all day yesterday | was raining | Длительное действие
They ___ (travel) around Europe last summer | were traveling | Процесс в прошлом
She ___ (study) when the lights went out | was studying | Прерванное действие

### Present Perfect
I ___ (finish) my homework | have finished | have + причастие прошедшего времени
She ___ (visit) Paris three times | has visited | has + причастие (для he/she/it)
They ___ (see) this movie before | have seen | have + seen (неправильный глагол)
He ___ (live) here since 2010 | has lived | Действие началось в прошлом и продолжается
We ___ (know) each other for 5 years | have known | have + known
I ___ never (be) to Japan | have never been | Опыт
She ___ just (arrive) | has just arrived | Только что произошло
They ___ already (eat) lunch | have already eaten | Уже завершено
He ___ (lose) his keys | has lost | Результат важен сейчас
I ___ (work) here for two years | have worked | Период до настоящего момента""")
        
        # Создание файла с правилами
        with open('rules.txt', 'w', encoding='utf-8') as f:
            f.write("""### Present Simple
Настоящее простое время используется для:
- Регулярных действий: I go to school every day
- Фактов: The sun rises in the east
- Расписаний: The train leaves at 9 AM
- Привычек: She drinks coffee every morning

Формула:
• I/You/We/They + глагол (базовая форма)
• He/She/It + глагол + s/es

Примеры:
- I work in an office
- She works in a bank
- They play tennis
- He watches TV

Слова-маркеры: always, usually, often, sometimes, never, every day/week/month/year

### Past Simple
Прошедшее простое время используется для:
- Завершенных действий в прошлом: I visited Paris last year
- Последовательных действий: He came home, had dinner and went to bed
- Привычек в прошлом: When I was young, I played football

Формула:
• Правильные глаголы: глагол + ed (worked, played, visited)
• Неправильные глаголы: 2-я форма (went, saw, bought)

Вопрос: Did + подлежащее + глагол (базовая форма)?
Отрицание: Подлежащее + didn't + глагол (базовая форма)

Слова-маркеры: yesterday, last week/month/year, ago, in 2010

### Future Simple
Будущее простое время используется для:
- Предсказаний: It will rain tomorrow
- Спонтанных решений: I'll help you
- Обещаний: I will call you later
- Фактов о будущем: I will be 30 next year

Формула: Подлежащее + will + глагол (базовая форма)
Сокращение: I'll, you'll, he'll, she'll, we'll, they'll
Вопрос: Will + подлежащее + глагол?
Отрицание: Подлежащее + won't (will not) + глагол

Слова-маркеры: tomorrow, next week/month/year, in the future, soon

### Present Continuous
Настоящее продолженное время используется для:
- Действий, происходящих сейчас: I am reading a book
- Временных ситуаций: I am living in London this month
- Запланированных действий: We are meeting tomorrow
- Изменяющихся ситуаций: The weather is getting better

Формула:
• I + am + глагол+ing
• He/She/It + is + глагол+ing
• You/We/They + are + глагол+ing

Правила добавления -ing:
- Обычно просто добавляем -ing: work → working
- Глаголы на -e: убираем e и добавляем -ing: make → making
- Короткие глаголы с согласной: удваиваем согласную: run → running

Слова-маркеры: now, at the moment, currently, these days, Look!, Listen!

### Past Continuous
Прошедшее продолженное время используется для:
- Действий в процессе в определенный момент прошлого: I was sleeping at 10 PM
- Фоновых действий: While I was cooking, he was watching TV
- Прерванных действий: I was reading when the phone rang
- Параллельных действий: They were singing and dancing

Формула:
• I/He/She/It + was + глагол+ing
• You/We/They + were + глагол+ing

Вопрос: Was/Were + подлежащее + глагол+ing?
Отрицание: Подлежащее + wasn't/weren't + глагол+ing

Слова-маркеры: while, when, as, all day/night, at 5 o'clock yesterday

### Present Perfect
Настоящее совершенное время используется для:
- Опыта: I have been to London
- Изменений: You have grown so much!
- Действий с результатом в настоящем: I have lost my keys
- Незаконченных периодов: I have worked here for 5 years

Формула:
• I/You/We/They + have + причастие прошедшего времени
• He/She/It + has + причастие прошедшего времени

Правильные глаголы: глагол + ed (worked, played)
Неправильные глаголы: 3-я форма (been, seen, done)

Слова-маркеры: already, just, yet, ever, never, for, since, recently""")
    
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Стиль
        style = ttk.Style()
        style.theme_use('clam')
        
        # Заголовок
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="📚 English Learning Application",
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=15)
        
        # Notebook для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка изучения слов
        self.words_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.words_frame, text='📖 Словарь')
        self.create_words_tab()
        
        # Вкладка упражнений
        self.exercises_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.exercises_frame, text='✏️ Упражнения')
        self.create_exercises_tab()
        
        # Вкладка правил
        self.rules_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.rules_frame, text='📋 Правила')
        self.create_rules_tab()
        
        # Вкладка статистики
        self.stats_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.stats_frame, text='📊 Статистика')
        self.create_stats_tab()
    
    def create_words_tab(self):
        """Создание вкладки со словами"""
        # Главный контейнер с двумя режимами
        self.words_container = tk.Frame(self.words_frame, bg='#ecf0f1')
        self.words_container.pack(fill='both', expand=True)
        
        # Фрейм выбора режима
        mode_frame = tk.Frame(self.words_container, bg='#ecf0f1')
        mode_frame.pack(pady=10)
        
        tk.Button(
            mode_frame,
            text="📖 Режим изучения",
            command=self.switch_to_study_mode,
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            mode_frame,
            text="🎯 Режим теста",
            command=self.show_test_setup,
            font=('Arial', 12, 'bold'),
            bg='#e67e22',
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            mode_frame,
            text="➕ Добавить слово",
            command=self.show_add_word_dialog,
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        # Панель поиска
        search_frame = tk.Frame(self.words_container, bg='#ecf0f1')
        search_frame.pack(pady=10)
        
        tk.Label(
            search_frame,
            text="🔍 Поиск:",
            font=('Arial', 11),
            bg='#ecf0f1'
        ).pack(side='left', padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=('Arial', 11), width=20)
        self.search_entry.pack(side='left', padx=5)
        
        tk.Button(
            search_frame,
            text="Найти",
            command=self.search_word,
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
        
        # Контейнер для режима изучения
        self.study_container = tk.Frame(self.words_container, bg='#ecf0f1')
        self.study_container.pack(fill='both', expand=True)
        
        # Карточка слова
        card_frame = tk.Frame(self.study_container, bg='white', relief='raised', bd=2)
        card_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Слово
        self.word_label = tk.Label(
            card_frame,
            text="",
            font=('Arial', 32, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        self.word_label.pack(pady=20)
        
        # Транскрипция
        self.transcription_label = tk.Label(
            card_frame,
            text="",
            font=('Arial', 18),
            bg='white',
            fg='#7f8c8d'
        )
        self.transcription_label.pack(pady=10)
        
        # Перевод
        self.translation_label = tk.Label(
            card_frame,
            text="",
            font=('Arial', 24),
            bg='white',
            fg='#27ae60'
        )
        self.translation_label.pack(pady=20)
        
        # НОВОЕ: Пример использования
        self.example_label = tk.Label(
            card_frame,
            text="",
            font=('Arial', 14, 'italic'),
            bg='white',
            fg='#3498db',
            wraplength=600
        )
        self.example_label.pack(pady=10)
        
        # НОВОЕ: Перевод примера
        self.example_translation_label = tk.Label(
            card_frame,
            text="",
            font=('Arial', 13),
            bg='white',
            fg='#95a5a6',
            wraplength=600
        )
        self.example_translation_label.pack(pady=5)
        
        # Кнопки управления
        control_frame = tk.Frame(self.study_container, bg='#ecf0f1')
        control_frame.pack(pady=20)
        
        tk.Button(
            control_frame,
            text="◀ Предыдущее",
            command=self.prev_word,
            font=('Arial', 12),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        tk.Button(
            control_frame,
            text="Показать перевод",
            command=self.show_translation,
            font=('Arial', 12),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        tk.Button(
            control_frame,
            text="Следующее ▶",
            command=self.next_word,
            font=('Arial', 12),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        tk.Button(
            control_frame,
            text="🔀 Случайное",
            command=self.random_word,
            font=('Arial', 12),
            bg='#9b59b6',
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        # НОВОЕ: Кнопки для примеров
        example_frame = tk.Frame(self.study_container, bg='#ecf0f1')
        example_frame.pack(pady=10)
        
        tk.Button(
            example_frame,
            text="📝 Показать пример",
            command=self.show_example,
            font=('Arial', 11),
            bg='#16a085',
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            example_frame,
            text="🔄 Перевод примера",
            command=self.show_example_translation,
            font=('Arial', 11),
            bg='#2980b9',
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        # Прогресс
        self.word_progress_label = tk.Label(
            self.study_container,
            text="",
            font=('Arial', 11),
            bg='#ecf0f1',
            fg='#7f8c8d'
        )
        self.word_progress_label.pack()
        
        # Контейнер для режима теста (изначально скрыт)
        self.test_container = tk.Frame(self.words_container, bg='#ecf0f1')
        
        # Показываем первое слово
        self.show_word()
    
    def show_example(self):
        """Показать пример использования слова"""
        if self.test_mode and self.test_words:
            # В режиме теста
            word_data = self.test_words[self.test_current_index]
        elif self.words_data:
            # В режиме изучения
            word_data = self.words_data[self.current_word_index]
        else:
            return
        
        if word_data.get('example'):
            if self.test_mode:
                self.test_example_label.config(text=f"💡 {word_data['example']}")
            else:
                self.example_label.config(text=f"💡 {word_data['example']}")
        else:
            if self.test_mode:
                self.test_example_label.config(text="💡 Пример недоступен")
            else:
                self.example_label.config(text="💡 Пример недоступен")
    
    def show_example_translation(self):
        """Показать перевод примера"""
        if self.test_mode and self.test_words:
            # В режиме теста
            word_data = self.test_words[self.test_current_index]
        elif self.words_data:
            # В режиме изучения
            word_data = self.words_data[self.current_word_index]
        else:
            return
        
        if word_data.get('example_translation'):
            if self.test_mode:
                self.test_example_translation_label.config(text=f"📖 {word_data['example_translation']}")
            else:
                self.example_translation_label.config(text=f"📖 {word_data['example_translation']}")
        else:
            if self.test_mode:
                self.test_example_translation_label.config(text="📖 Перевод недоступен")
            else:
                self.example_translation_label.config(text="📖 Перевод недоступен")
    
    def show_add_word_dialog(self):
        """Диалог добавления нового слова"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить новое слово")
        dialog.geometry("500x450")
        dialog.configure(bg='#ecf0f1')
        
        tk.Label(
            dialog,
            text="Добавить новое слово",
            font=('Arial', 14, 'bold'),
            bg='#ecf0f1'
        ).pack(pady=15)
        
        # Поле для английского слова
        tk.Label(dialog, text="Английское слово:", bg='#ecf0f1').pack(pady=5)
        word_entry = tk.Entry(dialog, font=('Arial', 12), width=40)
        word_entry.pack(pady=5)
        
        # Поле для перевода
        tk.Label(dialog, text="Перевод:", bg='#ecf0f1').pack(pady=5)
        translation_entry = tk.Entry(dialog, font=('Arial', 12), width=40)
        translation_entry.pack(pady=5)
        
        # Поле для транскрипции
        tk.Label(dialog, text="Транскрипция:", bg='#ecf0f1').pack(pady=5)
        transcription_entry = tk.Entry(dialog, font=('Arial', 12), width=40)
        transcription_entry.pack(pady=5)
        
        # НОВОЕ: Поле для примера
        tk.Label(dialog, text="Пример использования (опционально):", bg='#ecf0f1').pack(pady=5)
        example_entry = tk.Entry(dialog, font=('Arial', 12), width=40)
        example_entry.pack(pady=5)
        
        # НОВОЕ: Поле для перевода примера
        tk.Label(dialog, text="Перевод примера (опционально):", bg='#ecf0f1').pack(pady=5)
        example_translation_entry = tk.Entry(dialog, font=('Arial', 12), width=40)
        example_translation_entry.pack(pady=5)
        
        def add_word():
            word = word_entry.get().strip()
            translation = translation_entry.get().strip()
            transcription = transcription_entry.get().strip()
            example = example_entry.get().strip()
            example_translation = example_translation_entry.get().strip()
            
            if not word or not translation:
                messagebox.showwarning("Внимание", "Заполните обязательные поля!")
                return
            
            if not transcription:
                transcription = "[...]"
            
            # Добавляем слово в данные
            self.words_data.append({
                'word': word,
                'translation': translation,
                'transcription': transcription,
                'example': example,
                'example_translation': example_translation
            })
            
            # Сохраняем в файл
            try:
                with open('words.txt', 'a', encoding='utf-8') as f:
                    f.write(f"\n{word} | {translation} | {transcription} | {example} | {example_translation}")
                messagebox.showinfo("Успешно", "Слово добавлено!")
                dialog.destroy()
                self.show_word()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить слово: {e}")
        
        tk.Button(
            dialog,
            text="✅ Добавить",
            command=add_word,
            font=('Arial', 12),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=8
        ).pack(pady=15)
        
        tk.Button(
            dialog,
            text="Отмена",
            command=dialog.destroy,
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=5
        ).pack()
    
    def search_word(self):
        """Поиск слова в словаре"""
        search_term = self.search_entry.get().strip().lower()
        if not search_term:
            return
        
        for i, word_data in enumerate(self.words_data):
            if (search_term in word_data['word'].lower() or 
                search_term in word_data['translation'].lower()):
                self.current_word_index = i
                self.show_word()
                messagebox.showinfo("Найдено", f"Слово найдено: {word_data['word']}")
                return
        
        messagebox.showinfo("Не найдено", "Слово не найдено в словаре")
        
    def create_exercises_tab(self):
        """Создание вкладки с упражнениями по грамматике"""
        # Главный контейнер
        main_container = tk.Frame(self.exercises_frame, bg='#ecf0f1')
        main_container.pack(fill='both', expand=True)
        
        # Левая панель с выбором тем
        left_panel = tk.Frame(main_container, bg='white', relief='raised', bd=1)
        left_panel.pack(side='left', fill='y', padx=10, pady=10)
        
        tk.Label(
            left_panel,
            text="📝 Выберите темы:",
            font=('Arial', 13, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=10, padx=10)
        
        # Фрейм для чекбоксов
        checkbox_frame = tk.Frame(left_panel, bg='white')
        checkbox_frame.pack(padx=10, pady=5)
        
        # Словарь для хранения переменных чекбоксов
        self.topic_vars = {}
        
        # Создаем чекбоксы для каждой темы
        for topic in self.exercises_data.keys():
            var = tk.BooleanVar()
            self.topic_vars[topic] = var
            
            cb = tk.Checkbutton(
                checkbox_frame,
                text=f"{topic} ({len(self.exercises_data[topic])})",
                variable=var,
                font=('Arial', 11),
                bg='white',
                anchor='w',
                command=self.update_selected_topics
            )
            cb.pack(fill='x', pady=3)
        
        # Кнопки выбора всех/сброса
        button_frame = tk.Frame(left_panel, bg='white')
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="✅ Выбрать все",
            command=self.select_all_topics,
            font=('Arial', 10),
            bg='#27ae60',
            fg='white',
            padx=10,
            pady=5
        ).pack(side='left', padx=3)
        
        tk.Button(
            button_frame,
            text="❌ Снять все",
            command=self.deselect_all_topics,
            font=('Arial', 10),
            bg='#e74c3c',
            fg='white',
            padx=10,
            pady=5
        ).pack(side='left', padx=3)
        
        # Информация о выбранных темах
        self.selected_info_label = tk.Label(
            left_panel,
            text="Выбрано тем: 0\nВсего упражнений: 0",
            font=('Arial', 10),
            bg='white',
            fg='#7f8c8d'
        )
        self.selected_info_label.pack(pady=5)
        
        # Настройки упражнений
        settings_frame = tk.Frame(left_panel, bg='white')
        settings_frame.pack(pady=10)
        
        tk.Label(
            settings_frame,
            text="Количество упражнений:",
            font=('Arial', 10),
            bg='white'
        ).pack()
        
        self.exercise_count_var = tk.IntVar(value=10)
        self.exercise_count_scale = tk.Scale(
            settings_frame,
            from_=5,
            to=30,
            orient='horizontal',
            variable=self.exercise_count_var,
            bg='white',
            length=150
        )
        self.exercise_count_scale.pack(pady=5)
        
        # Кнопка начала упражнений
        tk.Button(
            left_panel,
            text="🚀 Начать упражнения",
            command=self.start_mixed_exercises,
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10
        ).pack(pady=15)
        
        # Правая панель с упражнениями
        right_panel = tk.Frame(main_container, bg='#ecf0f1')
        right_panel.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Фрейм для упражнения
        exercise_frame = tk.Frame(right_panel, bg='white', relief='raised', bd=2)
        exercise_frame.pack(fill='both', expand=True)
        
        # Название правила текущего упражнения
        self.current_topic_label = tk.Label(
            exercise_frame,
            text="",
            font=('Arial', 11),
            bg='white',
            fg='#8e44ad'
        )
        self.current_topic_label.pack(pady=5)
        
        # Название правила
        self.rule_title_label = tk.Label(
            exercise_frame,
            text="Выберите темы и нажмите 'Начать упражнения'",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        self.rule_title_label.pack(pady=15)
        
        # Задание
        self.exercise_instruction_label = tk.Label(
            exercise_frame,
            text="",
            font=('Arial', 12),
            bg='white',
            fg='#7f8c8d'
        )
        self.exercise_instruction_label.pack(pady=5)
        
        # Предложение
        self.sentence_label = tk.Label(
            exercise_frame,
            text="",
            font=('Arial', 18),
            bg='white',
            fg='#34495e',
            wraplength=500
        )
        self.sentence_label.pack(pady=20, padx=20)
        
        # Подсказка
        self.hint_label = tk.Label(
            exercise_frame,
            text="",
            font=('Arial', 11, 'italic'),
            bg='white',
            fg='#95a5a6'
        )
        self.hint_label.pack(pady=5)
        
        # Поле для ввода ответа
        answer_frame = tk.Frame(right_panel, bg='#ecf0f1')
        answer_frame.pack(pady=10)
        
        tk.Label(
            answer_frame,
            text="Ваш ответ:",
            font=('Arial', 12),
            bg='#ecf0f1'
        ).pack(side='left', padx=10)
        
        self.answer_entry = tk.Entry(
            answer_frame,
            font=('Arial', 14),
            width=20
        )
        self.answer_entry.pack(side='left', padx=10)
        self.answer_entry.bind('<Return>', lambda e: self.check_grammar_answer())
        
        tk.Button(
            answer_frame,
            text="Проверить",
            command=self.check_grammar_answer,
            font=('Arial', 12),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=5
        ).pack(side='left', padx=10)
        
        tk.Button(
            answer_frame,
            text="💡 Подсказка",
            command=self.show_hint,
            font=('Arial', 11),
            bg='#f39c12',
            fg='white',
            padx=15,
            pady=5
        ).pack(side='left', padx=5)
        
        # Результат
        self.result_label = tk.Label(
            right_panel,
            text="",
            font=('Arial', 14),
            bg='#ecf0f1'
        )
        self.result_label.pack(pady=10)
        
        # Кнопка следующего упражнения
        self.next_exercise_btn = tk.Button(
            right_panel,
            text="Следующее упражнение ▶",
            command=self.next_exercise,
            font=('Arial', 12),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            state='disabled'
        )
        self.next_exercise_btn.pack(pady=10)
        
        # Прогресс и счет
        progress_frame = tk.Frame(right_panel, bg='#ecf0f1')
        progress_frame.pack(pady=10)
        
        self.exercise_progress_label = tk.Label(
            progress_frame,
            text="",
            font=('Arial', 11),
            bg='#ecf0f1',
            fg='#7f8c8d'
        )
        self.exercise_progress_label.pack(side='left', padx=10)
        
        self.score_label = tk.Label(
            progress_frame,
            text="Счет: 0/0",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.score_label.pack(side='left', padx=10)
    
    def update_selected_topics(self):
        """Обновить информацию о выбранных темах"""
        selected = [topic for topic, var in self.topic_vars.items() if var.get()]
        total_exercises = sum(len(self.exercises_data[topic]) for topic in selected)
        
        self.selected_info_label.config(
            text=f"Выбрано тем: {len(selected)}\nВсего упражнений: {total_exercises}"
        )
        
        # Обновляем максимум для слайдера
        if total_exercises > 0:
            max_exercises = min(total_exercises, 30)
            self.exercise_count_scale.config(to=max_exercises)
            if self.exercise_count_var.get() > max_exercises:
                self.exercise_count_var.set(max_exercises)
    
    def select_all_topics(self):
        """Выбрать все темы"""
        for var in self.topic_vars.values():
            var.set(True)
        self.update_selected_topics()
    
    def deselect_all_topics(self):
        """Снять выбор со всех тем"""
        for var in self.topic_vars.values():
            var.set(False)
        self.update_selected_topics()
    
    def start_mixed_exercises(self):
        """Начать упражнения по выбранным темам"""
        # Получаем выбранные темы
        self.selected_topics = [topic for topic, var in self.topic_vars.items() if var.get()]
        
        if not self.selected_topics:
            messagebox.showwarning("Внимание", "Выберите хотя бы одну тему!")
            return
        
        # Собираем все упражнения из выбранных тем
        all_exercises = []
        for topic in self.selected_topics:
            all_exercises.extend(self.exercises_data[topic])
        
        # Перемешиваем и выбираем нужное количество
        random.shuffle(all_exercises)
        exercise_count = min(self.exercise_count_var.get(), len(all_exercises))
        self.mixed_exercises = all_exercises[:exercise_count]
        
        # Сбрасываем счетчики и флаги
        self.current_exercise_index = 0
        self.exercise_results = []
        self.answer_checked = False
        
        # Обновляем интерфейс
        topics_text = ", ".join(self.selected_topics[:3])
        if len(self.selected_topics) > 3:
            topics_text += f" и еще {len(self.selected_topics) - 3}"
        
        self.rule_title_label.config(text=f"📚 Смешанные упражнения")
        self.exercise_instruction_label.config(text="Поставьте глагол в правильную форму:")
        
        # Показываем первое упражнение
        self.show_mixed_exercise()
    
    def show_mixed_exercise(self):
        """Показать текущее упражнение из смешанного списка"""
        if self.current_exercise_index >= len(self.mixed_exercises):
            self.show_mixed_results()
            return
        
        # Сбрасываем флаг при показе нового упражнения
        self.answer_checked = False
        
        self.current_exercise = self.mixed_exercises[self.current_exercise_index]
        
        # Показываем из какой темы упражнение
        self.current_topic_label.config(text=f"📌 Тема: {self.current_exercise['rule']}")
        
        # Обновляем предложение
        self.sentence_label.config(text=self.current_exercise['sentence'])
        
        # Очищаем поле ввода и результат
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.config(state='normal')
        self.result_label.config(text="")
        self.hint_label.config(text="")
        self.next_exercise_btn.config(state='disabled')
        
        # Обновляем прогресс
        self.exercise_progress_label.config(
            text=f"Упражнение {self.current_exercise_index + 1} из {len(self.mixed_exercises)}"
        )
        
        # Фокус на поле ввода
        self.answer_entry.focus()
    
    def show_hint(self):
        """Показать подсказку"""
        if self.current_exercise and self.current_exercise['hint']:
            self.hint_label.config(text=f"💡 {self.current_exercise['hint']}")
    
    def check_grammar_answer(self):
        """Проверка ответа в грамматическом упражнении"""
        if not self.current_exercise:
            return
        
        # Предотвращаем множественную проверку одного ответа
        if self.answer_checked:
            return
        
        user_answer = self.answer_entry.get().strip()
        if not user_answer:
            messagebox.showwarning("Внимание", "Введите ответ!")
            return
        
        # Устанавливаем флаг, что ответ уже проверен
        self.answer_checked = True
        
        user_answer = user_answer.lower()
        correct_answer = self.current_exercise['answer'].lower()
        
        self.total_attempts += 1
        
        is_correct = user_answer == correct_answer
        
        # Сохраняем результат
        self.exercise_results.append({
            'exercise': self.current_exercise,
            'user_answer': user_answer,
            'is_correct': is_correct
        })
        
        if is_correct:
            self.score += 1
            self.result_label.config(
                text=f"✅ Правильно! {self.current_exercise['answer']}",
                fg='#27ae60'
            )
        else:
            self.result_label.config(
                text=f"❌ Неправильно. Правильный ответ: {self.current_exercise['answer']}",
                fg='#e74c3c'
            )
        
        self.score_label.config(text=f"Счет: {self.score}/{self.total_attempts}")
        self.next_exercise_btn.config(state='normal')
        
        # Отключаем поле ввода после проверки
        self.answer_entry.config(state='disabled')
        
        self.update_stats()
        self.save_progress()
    
    def next_exercise(self):
        """Следующее упражнение"""
        # Сбрасываем флаг проверки ответа
        self.answer_checked = False
        
        # Включаем поле ввода обратно
        self.answer_entry.config(state='normal')
        
        self.current_exercise_index += 1
        self.show_mixed_exercise()
    
    def show_mixed_results(self):
        """Показать результаты смешанных упражнений"""
        if not self.mixed_exercises:
            return
        
        # Создаем окно с результатами
        results_window = tk.Toplevel(self.root)
        results_window.title("Результаты упражнений")
        results_window.geometry("700x600")
        results_window.configure(bg='#ecf0f1')
        
        # Заголовок
        tk.Label(
            results_window,
            text="📊 Результаты упражнений",
            font=('Arial', 18, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=15)
        
        # Статистика
        correct_count = sum(1 for r in self.exercise_results if r['is_correct'])
        total_count = len(self.exercise_results)
        percentage = (correct_count / total_count * 100) if total_count > 0 else 0
        
        stats_frame = tk.Frame(results_window, bg='white', relief='raised', bd=1)
        stats_frame.pack(pady=10, padx=20, fill='x')
        
        # Определяем оценку
        if percentage >= 90:
            grade = "Отлично! 🎉"
            grade_color = '#27ae60'
        elif percentage >= 75:
            grade = "Хорошо! 👍"
            grade_color = '#3498db'
        elif percentage >= 60:
            grade = "Неплохо 📚"
            grade_color = '#f39c12'
        else:
            grade = "Нужна практика 💪"
            grade_color = '#e74c3c'
        
        tk.Label(
            stats_frame,
            text=grade,
            font=('Arial', 16, 'bold'),
            bg='white',
            fg=grade_color
        ).pack(pady=10)
        
        tk.Label(
            stats_frame,
            text=f"Правильных ответов: {correct_count} из {total_count}",
            font=('Arial', 14),
            bg='white'
        ).pack(pady=5)
        
        tk.Label(
            stats_frame,
            text=f"Результат: {percentage:.1f}%",
            font=('Arial', 14, 'bold'),
            bg='white'
        ).pack(pady=5)
        
        # Статистика по темам
        topic_stats = {}
        for result in self.exercise_results:
            topic = result['exercise']['rule']
            if topic not in topic_stats:
                topic_stats[topic] = {'correct': 0, 'total': 0}
            topic_stats[topic]['total'] += 1
            if result['is_correct']:
                topic_stats[topic]['correct'] += 1
        
        tk.Label(
            results_window,
            text="Результаты по темам:",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1'
        ).pack(pady=10)
        
        topics_frame = tk.Frame(results_window, bg='white', relief='raised', bd=1)
        topics_frame.pack(pady=5, padx=20, fill='x')
        
        for topic, stats in topic_stats.items():
            topic_percentage = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            color = '#27ae60' if topic_percentage >= 75 else '#e74c3c' if topic_percentage < 50 else '#f39c12'
            
            tk.Label(
                topics_frame,
                text=f"{topic}: {stats['correct']}/{stats['total']} ({topic_percentage:.0f}%)",
                font=('Arial', 11),
                bg='white',
                fg=color
            ).pack(pady=3)
        
        # Детальные результаты
        tk.Label(
            results_window,
            text="Подробные результаты:",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1'
        ).pack(pady=10)
        
        # Создаем область с прокруткой
        details_frame = tk.Frame(results_window, bg='white', relief='raised', bd=1)
        details_frame.pack(pady=5, padx=20, fill='both', expand=True)
        
        text_widget = scrolledtext.ScrolledText(
            details_frame,
            font=('Arial', 10),
            wrap=tk.WORD,
            height=10,
            bg='white'
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Заполняем детальными результатами
        for i, result in enumerate(self.exercise_results, 1):
            exercise = result['exercise']
            symbol = "✓" if result['is_correct'] else "✗"
            
            text_widget.insert(tk.END, f"{i}. [{exercise['rule']}]\n")
            text_widget.insert(tk.END, f"   {exercise['sentence']}\n")
            text_widget.insert(tk.END, f"   Правильный ответ: {exercise['answer']}\n")
            if not result['is_correct']:
                text_widget.insert(tk.END, f"   Ваш ответ: {result['user_answer']}\n")
            text_widget.insert(tk.END, f"   {symbol}\n\n")
        
        text_widget.config(state='disabled')
        
        # Кнопки действий
        button_frame = tk.Frame(results_window, bg='#ecf0f1')
        button_frame.pack(pady=15)
        
        tk.Button(
            button_frame,
            text="Новые упражнения",
            command=lambda: [results_window.destroy(), self.reset_exercises()],
            font=('Arial', 12),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="Закрыть",
            command=results_window.destroy,
            font=('Arial', 12),
            bg='#95a5a6',
            fg='white',
            padx=20,
            pady=8
        ).pack(side='left', padx=10)
    
    def reset_exercises(self):
        """Сброс упражнений для новой сессии"""
        self.current_exercise_index = 0
        self.current_exercise = None
        self.mixed_exercises = []
        self.exercise_results = []
        self.answer_checked = False
        
        self.sentence_label.config(text="")
        self.exercise_progress_label.config(text="")
        self.result_label.config(text="")
        self.hint_label.config(text="")
        self.current_topic_label.config(text="")
        self.rule_title_label.config(text="Выберите темы и нажмите 'Начать упражнения'")
        self.exercise_instruction_label.config(text="")
        self.answer_entry.config(state='normal')
        self.answer_entry.delete(0, tk.END)
    
    def show_test_setup(self):
        """Показать настройки теста"""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Настройки теста")
        setup_window.geometry("400x350")
        setup_window.configure(bg='#ecf0f1')
        
        tk.Label(
            setup_window,
            text="⚙️ Настройки теста",
            font=('Arial', 16, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=15)
        
        # Выбор типа теста
        tk.Label(
            setup_window,
            text="Тип теста:",
            font=('Arial', 12),
            bg='#ecf0f1'
        ).pack(pady=5)
        
        test_type_var = tk.StringVar(value="eng_to_rus")
        
        tk.Radiobutton(
            setup_window,
            text="Английский → Русский",
            variable=test_type_var,
            value="eng_to_rus",
            font=('Arial', 11),
            bg='#ecf0f1'
        ).pack(pady=5)
        
        tk.Radiobutton(
            setup_window,
            text="Русский → Английский",
            variable=test_type_var,
            value="rus_to_eng",
            font=('Arial', 11),
            bg='#ecf0f1'
        ).pack(pady=5)
        
        tk.Radiobutton(
            setup_window,
            text="Смешанный",
            variable=test_type_var,
            value="mixed",
            font=('Arial', 11),
            bg='#ecf0f1'
        ).pack(pady=5)
        
        # Выбор количества слов
        tk.Label(
            setup_window,
            text="Количество слов:",
            font=('Arial', 12),
            bg='#ecf0f1'
        ).pack(pady=10)
        
        words_count_var = tk.IntVar(value=10)
        words_scale = tk.Scale(
            setup_window,
            from_=5,
            to=min(len(self.words_data), 50),
            orient='horizontal',
            variable=words_count_var,
            bg='#ecf0f1',
            length=200
        )
        words_scale.pack(pady=5)
        
        # Кнопка начала теста
        tk.Button(
            setup_window,
            text="🚀 Начать тест",
            command=lambda: self.start_test(test_type_var.get(), words_count_var.get(), setup_window),
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10
        ).pack(pady=20)
        
        tk.Button(
            setup_window,
            text="Отмена",
            command=setup_window.destroy,
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=5
        ).pack()
    
    def start_test(self, test_type, words_count, setup_window):
        """Начать тест"""
        setup_window.destroy()
        
        self.test_mode = True
        self.test_type = test_type
        self.test_score = 0
        self.test_current_index = 0
        self.test_answers = []
        self.test_answer_checked = False
        
        # Выбираем случайные слова для теста
        self.test_words = random.sample(self.words_data, min(words_count, len(self.words_data)))
        
        # Скрываем режим изучения и показываем режим теста
        self.study_container.pack_forget()
        self.create_test_interface()
        self.show_test_question()
    
    def create_test_interface(self):
        """Создание интерфейса теста"""
        # Очищаем контейнер теста
        for widget in self.test_container.winfo_children():
            widget.destroy()
        
        self.test_container.pack(fill='both', expand=True)
        
        # Прогресс теста
        self.test_progress_label = tk.Label(
            self.test_container,
            text="",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.test_progress_label.pack(pady=10)
        
        # Карточка вопроса
        question_frame = tk.Frame(self.test_container, bg='white', relief='raised', bd=2)
        question_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Инструкция
        self.test_instruction_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 12),
            bg='white',
            fg='#7f8c8d'
        )
        self.test_instruction_label.pack(pady=10)
        
        # Вопрос
        self.test_question_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50',
            wraplength=600
        )
        self.test_question_label.pack(pady=30)
        
        # Подсказка (транскрипция)
        self.test_hint_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 14),
            bg='white',
            fg='#7f8c8d'
        )
        self.test_hint_label.pack(pady=10)
        
        # НОВОЕ: Пример использования в режиме теста
        self.test_example_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 13, 'italic'),
            bg='white',
            fg='#3498db',
            wraplength=600
        )
        self.test_example_label.pack(pady=5)
        
        # НОВОЕ: Перевод примера в режиме теста
        self.test_example_translation_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 12),
            bg='white',
            fg='#95a5a6',
            wraplength=600
        )
        self.test_example_translation_label.pack(pady=5)
        
        # Фрейм для ввода ответа
        answer_input_frame = tk.Frame(question_frame, bg='white')
        answer_input_frame.pack(pady=20)
        
        tk.Label(
            answer_input_frame,
            text="Ваш ответ:",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=5)
        
        # Поле ввода ответа
        self.test_answer_entry = tk.Entry(
            answer_input_frame,
            font=('Arial', 16),
            width=30,
            justify='center'
        )
        self.test_answer_entry.pack(pady=10)
        self.test_answer_entry.bind('<Return>', lambda e: self.check_test_answer_input())
        
        # Результат проверки
        self.test_result_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 14, 'bold'),
            bg='white'
        )
        self.test_result_label.pack(pady=10)
        
        # Показать правильный ответ (изначально скрыт)
        self.test_correct_answer_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 13),
            bg='white',
            fg='#27ae60'
        )
        self.test_correct_answer_label.pack(pady=5)
        
        # Кнопки управления
        buttons_frame = tk.Frame(self.test_container, bg='#ecf0f1')
        buttons_frame.pack(pady=15)
        
        # Кнопка проверки
        self.test_check_button = tk.Button(
            buttons_frame,
            text="✓ Проверить",
            command=self.check_test_answer_input,
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10
        )
        self.test_check_button.pack(side='left', padx=5)
        
        # Кнопка следующего вопроса (изначально скрыта)
        self.test_next_button = tk.Button(
            buttons_frame,
            text="Следующий вопрос →",
            command=self.next_test_question,
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10,
            state='disabled'
        )
        self.test_next_button.pack(side='left', padx=5)
        
        # Кнопка пропуска
        self.test_skip_button = tk.Button(
            buttons_frame,
            text="Пропустить →",
            command=self.skip_question,
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=8
        )
        self.test_skip_button.pack(side='left', padx=5)
        
        # НОВОЕ: Кнопки для примеров в режиме теста
        example_buttons_frame = tk.Frame(self.test_container, bg='#ecf0f1')
        example_buttons_frame.pack(pady=10)
        
        tk.Button(
            example_buttons_frame,
            text="📝 Показать пример",
            command=self.show_example,
            font=('Arial', 11),
            bg='#16a085',
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            example_buttons_frame,
            text="🔄 Перевод примера",
            command=self.show_example_translation,
            font=('Arial', 11),
            bg='#2980b9',
            fg='white',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)
        
        # Счетчик правильных ответов
        self.test_score_label = tk.Label(
            self.test_container,
            text="Правильных ответов: 0",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1',
            fg='#27ae60'
        )
        self.test_score_label.pack(pady=5)
    
    def show_test_question(self):
        """Показать вопрос теста"""
        if self.test_current_index >= len(self.test_words):
            self.show_test_results()
            return
        
        # Сбрасываем флаг проверки ответа для нового вопроса
        self.test_answer_checked = False
        
        current_word = self.test_words[self.test_current_index]
        
        # Обновляем прогресс
        self.test_progress_label.config(
            text=f"Вопрос {self.test_current_index + 1} из {len(self.test_words)}"
        )
        
        # Определяем тип вопроса
        if self.test_type == "mixed":
            question_type = random.choice(["eng_to_rus", "rus_to_eng"])
        else:
            question_type = self.test_type
        
        # Сохраняем текущий тип вопроса и правильный ответ
        self.current_question_type = question_type
        
        # Формируем вопрос
        if question_type == "eng_to_rus":
            self.test_instruction_label.config(text="Переведите на русский:")
            self.test_question_label.config(text=current_word['word'])
            self.test_hint_label.config(text=current_word['transcription'])
            self.current_correct_answer = current_word['translation']
        else:
            self.test_instruction_label.config(text="Переведите на английский:")
            self.test_question_label.config(text=current_word['translation'])
            self.test_hint_label.config(text="")
            self.current_correct_answer = current_word['word']
        
        # ИСПРАВЛЕНИЕ: Очищаем поле ввода и результаты
        self.test_answer_entry.delete(0, tk.END)
        self.test_answer_entry.config(state='normal', bg='white')
        self.test_result_label.config(text="")
        self.test_correct_answer_label.config(text="")
        
        # НОВОЕ: Очищаем примеры при новом вопросе
        self.test_example_label.config(text="")
        self.test_example_translation_label.config(text="")
        
        # Настраиваем кнопки
        self.test_check_button.config(state='normal')
        self.test_next_button.config(state='disabled')
        self.test_skip_button.config(state='normal')
        
        # Фокус на поле ввода
        self.test_answer_entry.focus()
        
        # Обновляем счетчик
        self.test_score_label.config(text=f"Правильных ответов: {self.test_score}/{self.test_current_index}")
    
    def normalize_answer(self, answer):
        """Нормализация ответа для более гибкой проверки"""
        # Приводим к нижнему регистру
        normalized = answer.lower().strip()
        
        # Удаляем лишние пробелы
        normalized = ' '.join(normalized.split())
        
        # Для английских слов - убираем артикли в начале
        articles = ['a ', 'an ', 'the ']
        for article in articles:
            if normalized.startswith(article):
                normalized = normalized[len(article):]
                break
        
        # Убираем точку в конце, если есть
        normalized = normalized.rstrip('.')
        
        return normalized
    
    def check_test_answer_input(self):
        """Проверка введенного ответа в тесте"""
        # Предотвращаем множественную проверку
        if self.test_answer_checked:
            return
        
        user_answer = self.test_answer_entry.get().strip()
        
        if not user_answer:
            messagebox.showwarning("Внимание", "Введите ответ!")
            return
        
        # Устанавливаем флаг
        self.test_answer_checked = True
        
        # Нормализуем ответы для сравнения
        normalized_user_answer = self.normalize_answer(user_answer)
        normalized_correct_answer = self.normalize_answer(self.current_correct_answer)
        
        # Проверяем правильность
        is_correct = normalized_user_answer == normalized_correct_answer
        
        # Сохраняем результат
        self.test_answers.append({
            'word': self.test_words[self.test_current_index],
            'user_answer': user_answer,
            'correct_answer': self.current_correct_answer,
            'is_correct': is_correct,
            'question_type': self.current_question_type
        })
        
        if is_correct:
            self.test_score += 1
            self.test_result_label.config(
                text="✅ Правильно!",
                fg='#27ae60'
            )
            self.test_answer_entry.config(bg='#d4edda')  # Светло-зеленый фон
        else:
            self.test_result_label.config(
                text="❌ Неправильно",
                fg='#e74c3c'
            )
            self.test_correct_answer_label.config(
                text=f"Правильный ответ: {self.current_correct_answer}"
            )
            self.test_answer_entry.config(bg='#f8d7da')  # Светло-красный фон
        
        # Обновляем счетчик
        self.test_score_label.config(
            text=f"Правильных ответов: {self.test_score}/{self.test_current_index + 1}"
        )
        
        # Отключаем поле ввода и кнопку проверки
        self.test_answer_entry.config(state='disabled')
        self.test_check_button.config(state='disabled')
        self.test_skip_button.config(state='disabled')
        
        # Активируем кнопку следующего вопроса
        self.test_next_button.config(state='normal')
        self.test_next_button.focus()
    
    def skip_question(self):
        """Пропустить вопрос"""
        # Предотвращаем пропуск уже отвеченного вопроса
        if self.test_answer_checked:
            return
        
        self.test_answer_checked = True
        
        # Сохраняем как неправильный ответ
        self.test_answers.append({
            'word': self.test_words[self.test_current_index],
            'user_answer': '',
            'correct_answer': self.current_correct_answer,
            'is_correct': False,
            'question_type': self.current_question_type
        })
        
        # Показываем правильный ответ
        self.test_result_label.config(
            text="⏭️ Вопрос пропущен",
            fg='#f39c12'
        )
        self.test_correct_answer_label.config(
            text=f"Правильный ответ: {self.current_correct_answer}"
        )
        
        # Переходим к следующему вопросу через 2 секунды
        self.root.after(2000, self.next_test_question)
    
    def next_test_question(self):
        """Следующий вопрос теста"""
        # Сбрасываем флаг и цвет поля ввода
        self.test_answer_checked = False
        self.test_answer_entry.config(bg='white')
        
        # ИСПРАВЛЕНИЕ: Очищаем поле ввода перед переходом к следующему вопросу
        self.test_answer_entry.delete(0, tk.END)
        
        self.test_current_index += 1
        self.show_test_question()

    def show_test_results(self):
        """Показать результаты теста"""
        # Очищаем контейнер
        for widget in self.test_container.winfo_children():
            widget.destroy()
        
        # Заголовок результатов
        tk.Label(
            self.test_container,
            text="📊 Результаты теста",
            font=('Arial', 20, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=20)
        
        # Статистика
        percentage = (self.test_score / len(self.test_words)) * 100 if len(self.test_words) > 0 else 0
        
        result_frame = tk.Frame(self.test_container, bg='white', relief='raised', bd=2)
        result_frame.pack(pady=10, padx=20, fill='x')
        
        # Определяем цвет и эмодзи в зависимости от результата
        if percentage >= 90:
            color = '#27ae60'
            emoji = '🎉'
            message = 'Превосходно!'
        elif percentage >= 80:
            color = '#2ecc71'
            emoji = '🌟'
            message = 'Отлично!'
        elif percentage >= 70:
            color = '#3498db'
            emoji = '👍'
            message = 'Хорошо!'
        elif percentage >= 60:
            color = '#f39c12'
            emoji = '📚'
            message = 'Неплохо!'
        else:
            color = '#e74c3c'
            emoji = '💪'
            message = 'Нужно больше практики!'
        
        tk.Label(
            result_frame,
            text=f"{emoji} {message}",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg=color
        ).pack(pady=10)
        
        tk.Label(
            result_frame,
            text=f"Правильных ответов: {self.test_score} из {len(self.test_words)}",
            font=('Arial', 16),
            bg='white'
        ).pack(pady=5)
        
        tk.Label(
            result_frame,
            text=f"Результат: {percentage:.1f}%",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg=color
        ).pack(pady=5)
        
        # Детальные результаты
        tk.Label(
            self.test_container,
            text="📝 Подробные результаты:",
            font=('Arial', 14, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50'
        ).pack(pady=10)
        
        # Создаем область с прокруткой для детальных результатов
        details_frame = tk.Frame(self.test_container, bg='white', relief='raised', bd=1)
        details_frame.pack(pady=5, padx=20, fill='both', expand=True)
        
        text_widget = scrolledtext.ScrolledText(
            details_frame,
            font=('Arial', 11),
            wrap=tk.WORD,
            height=12,
            bg='white'
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Заполняем детальными результатами
        for i, result in enumerate(self.test_answers, 1):
            word_data = result['word']
            symbol = "✅" if result['is_correct'] else "❌"
            
            if result['question_type'] == 'eng_to_rus':
                question = f"{word_data['word']} {word_data['transcription']}"
            else:
                question = word_data['translation']
            
            text_widget.insert(tk.END, f"{i}. {question}\n", "question")
            
            if result['is_correct']:
                text_widget.insert(tk.END, f"   {symbol} Ваш ответ: {result['user_answer']}\n", "correct")
            else:
                if result['user_answer']:
                    text_widget.insert(tk.END, f"   {symbol} Ваш ответ: {result['user_answer']}\n", "wrong")
                else:
                    text_widget.insert(tk.END, f"   {symbol} Вопрос пропущен\n", "skipped")
                text_widget.insert(tk.END, f"   ✓ Правильный ответ: {result['correct_answer']}\n", "correct_answer")
            
            # НОВОЕ: Показываем примеры в результатах
            if word_data.get('example'):
                text_widget.insert(tk.END, f"   💡 Пример: {word_data['example']}\n", "example")
                if word_data.get('example_translation'):
                    text_widget.insert(tk.END, f"   📖 Перевод: {word_data['example_translation']}\n", "example_trans")
            
            text_widget.insert(tk.END, "\n")
        
        # Настройка тегов для цветного текста
        text_widget.tag_config("question", foreground="#2c3e50", font=('Arial', 11, 'bold'))
        text_widget.tag_config("correct", foreground="#27ae60")
        text_widget.tag_config("wrong", foreground="#e74c3c")
        text_widget.tag_config("skipped", foreground="#f39c12")
        text_widget.tag_config("correct_answer", foreground="#27ae60", font=('Arial', 11, 'italic'))
        text_widget.tag_config("example", foreground="#3498db", font=('Arial', 10, 'italic'))
        text_widget.tag_config("example_trans", foreground="#95a5a6", font=('Arial', 10))
        
        text_widget.config(state='disabled')
        
        # Кнопки действий
        button_frame = tk.Frame(self.test_container, bg='#ecf0f1')
        button_frame.pack(pady=15)
        
        tk.Button(
            button_frame,
            text="🔄 Пройти тест заново",
            command=self.restart_test,
            font=('Arial', 12),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="🎯 Новый тест",
            command=self.show_test_setup,
            font=('Arial', 12),
            bg='#e67e22',
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="📖 Вернуться к изучению",
            command=self.switch_to_study_mode,
            font=('Arial', 12),
            bg='#9b59b6',
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=10)
        
        # Обновляем общую статистику
        self.total_attempts += len(self.test_words)
        self.score += self.test_score
        self.update_stats()
        self.save_progress()
    
    def restart_test(self):
        """Перезапустить тот же тест"""
        self.test_current_index = 0
        self.test_score = 0
        self.test_answers = []
        self.test_answer_checked = False
        random.shuffle(self.test_words)
        self.create_test_interface()
        self.show_test_question()
    
    def switch_to_study_mode(self):
        """Переключиться в режим изучения"""
        self.test_mode = False
        self.test_container.pack_forget()
        self.study_container.pack(fill='both', expand=True)
        self.show_word()
    
    def show_word(self):
        """Отображение текущего слова"""
        if self.words_data and not self.test_mode:
            word_data = self.words_data[self.current_word_index]
            self.word_label.config(text=word_data['word'])
            self.transcription_label.config(text=word_data['transcription'])
            self.translation_label.config(text="")
            
            # НОВОЕ: Очищаем примеры при показе нового слова
            self.example_label.config(text="")
            self.example_translation_label.config(text="")
            
            self.word_progress_label.config(
                text=f"Слово {self.current_word_index + 1} из {len(self.words_data)}"
            )
    
    def show_translation(self):
        """Показать перевод текущего слова"""
        if self.words_data and not self.test_mode:
            word_data = self.words_data[self.current_word_index]
            self.translation_label.config(text=word_data['translation'])
    
    def next_word(self):
        """Следующее слово"""
        if self.words_data and not self.test_mode:
            self.current_word_index = (self.current_word_index + 1) % len(self.words_data)
            self.show_word()
    
    def prev_word(self):
        """Предыдущее слово"""
        if self.words_data and not self.test_mode:
            self.current_word_index = (self.current_word_index - 1) % len(self.words_data)
            self.show_word()
    
    def random_word(self):
        """Случайное слово"""
        if self.words_data and not self.test_mode:
            self.current_word_index = random.randint(0, len(self.words_data) - 1)
            self.show_word()
    
    def create_rules_tab(self):
        """Создание вкладки с правилами"""
        # Список правил
        list_frame = tk.Frame(self.rules_frame, bg='#ecf0f1')
        list_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        tk.Label(
            list_frame,
            text="Выберите правило:",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1'
        ).pack(pady=5)
        
        # Listbox для выбора правила
        self.rules_listbox = tk.Listbox(
            list_frame,
            font=('Arial', 11),
            width=30,
            height=20
        )
        self.rules_listbox.pack(pady=5)
        self.rules_listbox.bind('<<ListboxSelect>>', self.show_rule)
        
        # Заполнение списка правил
        for rule in self.rules_data:
            self.rules_listbox.insert(tk.END, rule['title'])
        
        # Область отображения правила
        content_frame = tk.Frame(self.rules_frame, bg='white', relief='raised', bd=2)
        content_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # ИСПРАВЛЕНО: переименовано для избежания конфликта
        self.rules_title_label = tk.Label(
            content_frame,
            text="Выберите правило из списка",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        self.rules_title_label.pack(pady=10)
        
        # ИСПРАВЛЕНО: переименовано для избежания конфликта
        self.rules_text_widget = scrolledtext.ScrolledText(
            content_frame,
            font=('Arial', 11),
            wrap=tk.WORD,
            width=60,
            height=25,
            bg='white'
        )
        self.rules_text_widget.pack(padx=10, pady=10, fill='both', expand=True)
    
    def show_rule(self, event):
        """Отображение выбранного правила"""
        selection = self.rules_listbox.curselection()
        if selection:
            index = selection[0]
            rule = self.rules_data[index]
            self.rules_title_label.config(text=rule['title'])
            self.rules_text_widget.delete('1.0', tk.END)
            self.rules_text_widget.insert('1.0', rule['content'])
    
    def create_stats_tab(self):
        """Создание вкладки со статистикой"""
        stats_container = tk.Frame(self.stats_frame, bg='white', relief='raised', bd=2)
        stats_container.pack(pady=20, padx=20, fill='both', expand=True)
        
        tk.Label(
            stats_container,
            text="📊 Ваша статистика",
            font=('Arial', 20, 'bold'),
            bg='white',
            fg='#2c3e50'
        ).pack(pady=20)
        
        # Статистика по словам
        words_frame = tk.Frame(stats_container, bg='#ecf0f1', relief='raised', bd=1)
        words_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(
            words_frame,
            text="📖 Словарь",
            font=('Arial', 14, 'bold'),
            bg='#ecf0f1'
        ).pack(pady=5)
        
        tk.Label(
            words_frame,
            text=f"Всего слов: {len(self.words_data)}",
            font=('Arial', 12),
            bg='#ecf0f1'
        ).pack(pady=3)
        
        # Подсчет слов с примерами
        words_with_examples = sum(1 for word in self.words_data if word.get('example'))
        tk.Label(
            words_frame,
            text=f"Слов с примерами: {words_with_examples}",
            font=('Arial', 11),
            bg='#ecf0f1',
            fg='#7f8c8d'
        ).pack(pady=2)
        
        # Статистика по упражнениям
        exercises_frame = tk.Frame(stats_container, bg='#ecf0f1', relief='raised', bd=1)
        exercises_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(
            exercises_frame,
            text="✏️ Упражнения",
            font=('Arial', 14, 'bold'),
            bg='#ecf0f1'
        ).pack(pady=5)
        
        self.stats_score_label = tk.Label(
            exercises_frame,
            text=f"✅ Правильных ответов: {self.score}",
            font=('Arial', 12),
            bg='#ecf0f1',
            fg='#27ae60'
        )
        self.stats_score_label.pack(pady=3)
        
        self.stats_total_label = tk.Label(
            exercises_frame,
            text=f"📝 Всего попыток: {self.total_attempts}",
            font=('Arial', 12),
            bg='#ecf0f1'
        )
        self.stats_total_label.pack(pady=3)
        
        self.accuracy_label = tk.Label(
            exercises_frame,
            text="📈 Точность: 0%",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1',
            fg='#3498db'
        )
        self.accuracy_label.pack(pady=3)
        
        # Последняя сессия
        if 'last_session' in self.progress_data:
            tk.Label(
                stats_container,
                text=f"🕒 Последняя сессия: {self.progress_data['last_session']}",
                font=('Arial', 11),
                bg='white',
                fg='#7f8c8d'
            ).pack(pady=10)
        
        # Кнопки
        button_frame = tk.Frame(stats_container, bg='white')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="🔄 Сбросить статистику",
            command=self.reset_stats,
            font=('Arial', 12),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="💾 Сохранить прогресс",
            command=lambda: [self.save_progress(), messagebox.showinfo("Успешно", "Прогресс сохранен!")],
            font=('Arial', 12),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10
        ).pack(side='left', padx=5)
        
        # Обновляем статистику
        self.update_stats()
    
    def update_stats(self):
        """Обновление статистики"""
        self.stats_score_label.config(text=f"✅ Правильных ответов: {self.score}")
        self.stats_total_label.config(text=f"📝 Всего попыток: {self.total_attempts}")
        
        if self.total_attempts > 0:
            accuracy = (self.score / self.total_attempts) * 100
            self.accuracy_label.config(text=f"📈 Точность: {accuracy:.1f}%")
    
    def reset_stats(self):
        """Сброс статистики"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите сбросить статистику?"):
            self.score = 0
            self.total_attempts = 0
            self.update_stats()
            self.score_label.config(text="Счет: 0/0")
            self.save_progress()
            messagebox.showinfo("Успешно", "Статистика сброшена!")

def main():
    root = tk.Tk()
    app = EnglishLearningApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()