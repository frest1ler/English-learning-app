import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import json
from datetime import datetime

class EnglishLearningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("English Learning App")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Загрузка данных
        self.words_data = self.load_words()
        self.exercises_data = self.load_exercises()
        self.rules_data = self.load_rules()
        
        # Переменные для отслеживания прогресса
        self.current_word_index = 0
        self.current_exercise = None
        self.current_rule = None
        self.score = 0
        self.total_attempts = 0
        
        # Переменные для теста
        self.test_mode = False
        self.test_words = []
        self.test_current_index = 0
        self.test_score = 0
        self.test_answers = []
        self.test_type = "eng_to_rus"
        
        # Создание интерфейса
        self.create_widgets()
        
    def load_words(self):
        """Загрузка слов из файла"""
        try:
            with open('words.txt', 'r', encoding='utf-8') as f:
                words = []
                for line in f:
                    if line.strip():
                        parts = line.strip().split('|')
                        if len(parts) == 3:
                            words.append({
                                'word': parts[0].strip(),
                                'translation': parts[1].strip(),
                                'transcription': parts[2].strip()
                            })
                return words
        except FileNotFoundError:
            self.create_sample_files()
            return self.load_words()
    
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
        # Создание файла со словами
        with open('words.txt', 'w', encoding='utf-8') as f:
            f.write("""apple | яблоко | [ˈæpl]
book | книга | [bʊk]
cat | кот | [kæt]
dog | собака | [dɒɡ]
house | дом | [haʊs]
water | вода | [ˈwɔːtə]
friend | друг | [frend]
school | школа | [skuːl]
teacher | учитель | [ˈtiːtʃə]
student | студент | [ˈstjuːdənt]
computer | компьютер | [kəmˈpjuːtə]
phone | телефон | [fəʊn]
city | город | [ˈsɪti]
country | страна | [ˈkʌntri]
family | семья | [ˈfæmɪli]
morning | утро | [ˈmɔːnɪŋ]
evening | вечер | [ˈiːvnɪŋ]
night | ночь | [naɪt]
day | день | [deɪ]
work | работа | [wɜːk]""")
        
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
            text="П��казать перевод",
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
    
    def create_exercises_tab(self):
        """Создание вкладки с упражнениями по грамматике"""
        # Верхняя панель с выбором темы
        top_frame = tk.Frame(self.exercises_frame, bg='#ecf0f1')
        top_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            top_frame,
            text="Выберите тему:",
            font=('Arial', 12, 'bold'),
            bg='#ecf0f1'
        ).pack(side='left', padx=10)
        
        # Выпадающий список с темами
        self.topic_var = tk.StringVar()
        self.topic_combo = ttk.Combobox(
            top_frame,
            textvariable=self.topic_var,
            font=('Arial', 11),
            width=30,
            state='readonly'
        )
        self.topic_combo.pack(side='left', padx=10)
        
        # Заполняем список темами из упражнений
        if self.exercises_data:
            topics = list(self.exercises_data.keys())
            self.topic_combo['values'] = topics
            if topics:
                self.topic_combo.current(0)
        
        tk.Button(
            top_frame,
            text="Начать упражнения",
            command=self.start_exercises,
            font=('Arial', 11),
            bg='#27ae60',
            fg='white',
            padx=15,
            pady=5
        ).pack(side='left', padx=10)
        
        # Фрейм для упражнения
        exercise_frame = tk.Frame(self.exercises_frame, bg='white', relief='raised', bd=2)
        exercise_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Название правила
        self.rule_title_label = tk.Label(
            exercise_frame,
            text="Выберите тему и нажмите 'Начать упражнения'",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        self.rule_title_label.pack(pady=15)
        
        # Задание
        self.exercise_instruction_label = tk.Label(
            exercise_frame,
            text="Поставьте глагол в правильную форму:",
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
            wraplength=600
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
        answer_frame = tk.Frame(self.exercises_frame, bg='#ecf0f1')
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
            self.exercises_frame,
            text="",
            font=('Arial', 14),
            bg='#ecf0f1'
        )
        self.result_label.pack(pady=10)
        
        # Кнопка следующего упражнения
        self.next_exercise_btn = tk.Button(
            self.exercises_frame,
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
        progress_frame = tk.Frame(self.exercises_frame, bg='#ecf0f1')
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
    
    def start_exercises(self):
        """Начать упражнения по выбранной теме"""
        selected_topic = self.topic_var.get()
        if not selected_topic or selected_topic not in self.exercises_data:
            messagebox.showwarning("Внимание", "Выберите тему для упражнений")
            return
        
        self.current_rule = selected_topic
        self.current_exercises = self.exercises_data[selected_topic].copy()
        random.shuffle(self.current_exercises)
        self.current_exercise_index = 0
        
        # Обновляем заголовок
        self.rule_title_label.config(text=f"📚 {selected_topic}")
        
        # Показываем первое упражнение
        self.show_exercise()
    
    def show_exercise(self):
        """Показать текущее упражнение"""
        if not self.current_exercises or self.current_exercise_index >= len(self.current_exercises):
            self.show_exercise_results()
            return
        
        self.current_exercise = self.current_exercises[self.current_exercise_index]
        
        # Обновляем предложение
        self.sentence_label.config(text=self.current_exercise['sentence'])
        
        # Очищаем поле ввода и результат
        self.answer_entry.delete(0, tk.END)
        self.result_label.config(text="")
        self.hint_label.config(text="")
        self.next_exercise_btn.config(state='disabled')
        
        # Обновляем прогресс
        self.exercise_progress_label.config(
            text=f"Упражнение {self.current_exercise_index + 1} из {len(self.current_exercises)}"
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
        
        user_answer = self.answer_entry.get().strip().lower()
        correct_answer = self.current_exercise['answer'].lower()
        
        self.total_attempts += 1
        
        if user_answer == correct_answer:
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
        self.update_stats()
    
    def next_exercise(self):
        """Следующее упражнение"""
        self.current_exercise_index += 1
        self.show_exercise()
    
    def show_exercise_results(self):
        """Показать результаты упражнений"""
        if not self.current_exercises:
            return
        
        total = len(self.current_exercises)
        percentage = (self.score / self.total_attempts * 100) if self.total_attempts > 0 else 0
        
        message = f"""
        Упражнения по теме "{self.current_rule}" завершены!
        
        Результаты:
        ✅ Правильных ответов: {self.score}
        📝 Всего попыток: {self.total_attempts}
        📊 Точность: {percentage:.1f}%
        
        Хотите продолжить с другой темой?
        """
        
        if messagebox.askyesno("Упражнения завершены", message):
            # Сброс для новых упражнений
            self.current_exercise_index = 0
            self.current_exercise = None
            self.sentence_label.config(text="")
            self.exercise_progress_label.config(text="")
            self.result_label.config(text="")
            self.hint_label.config(text="")
            self.rule_title_label.config(text="Выберите тему и нажмите 'Начать упражнения'")
    
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
        
        self.test_question_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 24, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        self.test_question_label.pack(pady=30)
        
        self.test_hint_label = tk.Label(
            question_frame,
            text="",
            font=('Arial', 14),
            bg='white',
            fg='#7f8c8d'
        )
        self.test_hint_label.pack(pady=10)
        
        # Варианты ответов
        self.answer_frame = tk.Frame(question_frame, bg='white')
        self.answer_frame.pack(pady=20)
        
        self.answer_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.answer_frame,
                text="",
                font=('Arial', 14),
                bg='#3498db',
                fg='white',
                width=30,
                pady=10,
                command=lambda x=i: self.check_test_answer(x)
            )
            btn.pack(pady=5)
            self.answer_buttons.append(btn)
        
        # Кнопка пропуска
        tk.Button(
            self.test_container,
            text="Пропустить →",
            command=self.skip_question,
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            padx=15,
            pady=5
        ).pack(pady=10)
    
    def show_test_question(self):
        """Показать вопрос теста"""
        if self.test_current_index >= len(self.test_words):
            self.show_test_results()
            return
        
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
        
        # Формируем вопрос и варианты ответов
        if question_type == "eng_to_rus":
            self.test_question_label.config(text=current_word['word'])
            self.test_hint_label.config(text=current_word['transcription'])
            correct_answer = current_word['translation']
            
            wrong_answers = [w['translation'] for w in self.words_data 
                           if w['translation'] != correct_answer]
        else:
            self.test_question_label.config(text=current_word['translation'])
            self.test_hint_label.config(text="Выберите английский перевод")
            correct_answer = current_word['word']
            
            wrong_answers = [w['word'] for w in self.words_data 
                           if w['word'] != correct_answer]
        
        # Выбираем 3 случайных неправильных ответа
        wrong_answers = random.sample(wrong_answers, min(3, len(wrong_answers)))
        
        # Создаем список всех вариантов и перемешиваем
        all_answers = wrong_answers + [correct_answer]
        random.shuffle(all_answers)
        
        # Сохраняем правильный ответ
        self.correct_answer_index = all_answers.index(correct_answer)
        
        # Обновляем кнопки с вариантами
        for i, btn in enumerate(self.answer_buttons):
            if i < len(all_answers):
                btn.config(text=all_answers[i], state='normal', bg='#3498db')
                btn.pack()
            else:
                btn.pack_forget()
    
    def check_test_answer(self, answer_index):
        """Проверка ответа в тесте"""
        is_correct = answer_index == self.correct_answer_index
        
        # Сохраняем результат
        self.test_answers.append({
            'word': self.test_words[self.test_current_index],
            'is_correct': is_correct
        })
        
        if is_correct:
            self.test_score += 1
            self.answer_buttons[answer_index].config(bg='#27ae60')
        else:
            self.answer_buttons[answer_index].config(bg='#e74c3c')
            self.answer_buttons[self.correct_answer_index].config(bg='#27ae60')
        
        # Отключаем все кнопки
        for btn in self.answer_buttons:
            btn.config(state='disabled')
        
        # Переход к следующему вопросу через 1.5 секунды
        self.root.after(1500, self.next_test_question)
    
    def skip_question(self):
        """Пропустить вопрос"""
        self.test_answers.append({
            'word': self.test_words[self.test_current_index],
            'is_correct': False
        })
        self.next_test_question()
    
    def next_test_question(self):
        """Следующий вопрос теста"""
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
        percentage = (self.test_score / len(self.test_words)) * 100
        
        result_frame = tk.Frame(self.test_container, bg='white', relief='raised', bd=2)
        result_frame.pack(pady=10, padx=20, fill='x')
        
        # Определяем цвет и эмодзи в зависимости от результата
        if percentage >= 80:
            color = '#27ae60'
            emoji = '🎉'
            message = 'Отлично!'
        elif percentage >= 60:
            color = '#f39c12'
            emoji = '👍'
            message = 'Хорошо!'
        else:
            color = '#e74c3c'
            emoji = '📚'
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
        
        # Кнопки действий
        button_frame = tk.Frame(self.test_container, bg='#ecf0f1')
        button_frame.pack(pady=20)
        
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
    
    def restart_test(self):
        """Перезапустить тот же тест"""
        self.test_current_index = 0
        self.test_score = 0
        self.test_answers = []
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
        
        self.rule_title_label = tk.Label(
            content_frame,
            text="Выберите правило из списка",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        self.rule_title_label.pack(pady=10)
        
        self.rule_text = scrolledtext.ScrolledText(
            content_frame,
            font=('Arial', 11),
            wrap=tk.WORD,
            width=60,
            height=25,
            bg='white'
        )
        self.rule_text.pack(padx=10, pady=10, fill='both', expand=True)
    
    def show_rule(self, event):
        """Отображение выбранного правила"""
        selection = self.rules_listbox.curselection()
        if selection:
            index = selection[0]
            rule = self.rules_data[index]
            self.rule_title_label.config(text=rule['title'])
            self.rule_text.delete('1.0', tk.END)
            self.rule_text.insert('1.0', rule['content'])
    
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
        words_frame = tk.Frame(stats_container, bg='white')
        words_frame.pack(pady=10)
        
        tk.Label(
            words_frame,
            text=f"📖 Всего слов в словаре: {len(self.words_data)}",
            font=('Arial', 14),
            bg='white'
        ).pack(pady=5)
        
        # Статистика по упражнениям
        exercises_frame = tk.Frame(stats_container, bg='white')
        exercises_frame.pack(pady=10)
        
        self.stats_score_label = tk.Label(
            exercises_frame,
            text=f"✅ Правильных ответов: {self.score}",
            font=('Arial', 14),
            bg='white',
            fg='#27ae60'
        )
        self.stats_score_label.pack(pady=5)
        
        self.stats_total_label = tk.Label(
            exercises_frame,
            text=f"📝 Всего попыток: {self.total_attempts}",
            font=('Arial', 14),
            bg='white'
        )
        self.stats_total_label.pack(pady=5)
        
        self.accuracy_label = tk.Label(
            exercises_frame,
            text="📈 Точность: 0%",
            font=('Arial', 14),
            bg='white',
            fg='#3498db'
        )
        self.accuracy_label.pack(pady=5)
        
        # Кнопка сброса статистики
        tk.Button(
            stats_container,
            text="🔄 Сбросить статистику",
            command=self.reset_stats,
            font=('Arial', 12),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=10
        ).pack(pady=20)
    
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
            messagebox.showinfo("Успешно", "Статистика сброшена!")

def main():
    root = tk.Tk()
    app = EnglishLearningApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()