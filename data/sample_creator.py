"""
Создание примеров файлов данных
"""

import os
from config import DATA_FILES, DATA_FILES_DIR

class SampleCreator:
    """Класс для создания примеров файлов"""
    
    @staticmethod
    def ensure_data_directory():
        """Убедиться, что папка data_files существует"""
        os.makedirs(DATA_FILES_DIR, exist_ok=True)
        print(f"✓ Папка для данных: {DATA_FILES_DIR}")
    
    @staticmethod
    def create_all_files():
        """Создание всех файлов с примерами"""
        SampleCreator.ensure_data_directory()
        SampleCreator.create_words_file()
        SampleCreator.create_exercises_file()
        SampleCreator.create_rules_file()
        print(f"✓ Все файлы созданы в папке: {DATA_FILES_DIR}")
    
    @staticmethod
    def create_words_file():
        """Создание файла со словами"""
        filepath = DATA_FILES['words']
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("""apple | яблоко | [ˈæpl] | I eat an apple every day. | Я ем яблоко каждый день.
book | книга | [bʊk] | This book is very interesting. | Эта книга очень интересная.
cat | кот | [kæt] | My cat likes to sleep on the sofa. | Мой кот любит спать на диване.
dog | собака | [dɒɡ] | The dog is playing in the garden. | Собака играет в саду.
house | дом | [haʊs] | We live in a big house. | Мы живем в большом доме.
water | вода | [ˈwɔːtə] | I drink water every morning. | Я пью воду каждое утро.
friend | друг | [frend] | She is my best friend. | Она моя лучшая подруга.
school | школа | [skuːl] | Children go to school every day. | Дети ходят в школу каждый день.
teacher | учитель | [ˈtiːtʃə] | Our teacher is very kind and patient. | Наш учитель очень добрый и терпеливый.
student | студент | [ˈstjuːdənt] | He is a good student. | Он хороший студент.
computer | компьютер | [kəmˈpjuːtə] | I work on my computer all day. | Я работаю на компьютере весь день.
phone | телефон | [fəʊn] | Can you answer the phone, please? | Можешь ответить на телефон, пожалуйста?
city | город | [ˈsɪti] | London is a beautiful city. | Лондон - красивый город.
country | страна | [ˈkʌntri] | France is a wonderful country. | Франция - замечательная страна.
family | семья | [ˈfæmɪli] | I love my family very much. | Я очень люблю свою семью.
morning | утро | [ˈmɔːnɪŋ] | Good morning! How are you today? | Доброе утро! Как дела сегодня?
evening | вечер | [ˈiːvnɪŋ] | We go for a walk in the evening. | Мы гуляем вечером.
night | ночь | [naɪt] | The stars shine bright at night. | Звезды ярко светят ночью.
day | день | [deɪ] | Have a nice day! | Хорошего дня!
work | работа | [wɜːk] | I go to work by bus. | Я езжу на работу на автобусе.
hello | привет | [həˈləʊ] | Hello! Nice to meet you. | Привет! Приятно познакомиться.
world | мир | [wɜːld] | We live in a beautiful world. | Мы живем в прекрасном мире.
learn | учиться | [lɜːn] | I want to learn English. | Я хочу учить английский.
love | любовь | [lʌv] | Love makes us happy. | Любовь делает нас счастливыми.
time | время | [taɪm] | What time is it now? | Который сейчас час?
people | люди | [ˈpiːpl] | Many people live in this city. | Много людей живет в этом городе.
year | год | [jɪə] | This year was amazing. | Этот год был удивительным.
way | путь | [weɪ] | Can you show me the way? | Можешь показать мне дорогу?
new | новый | [njuː] | I bought a new car yesterday. | Я купил новую машину вчера.
good | хороший | [ɡʊd] | That's a good idea! | Это хорошая идея!
man | мужчина | [mæn] | That man is my father. | Тот мужчина - мой отец.""")
        print(f"✓ Создан файл: {filepath}")
    
    @staticmethod
    def create_exercises_file():
        """Создание файла с упражнениями"""
        filepath = DATA_FILES['exercises']
        with open(filepath, 'w', encoding='utf-8') as f:
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
        print(f"✓ Создан файл: {filepath}")
    
    @staticmethod
    def create_rules_file():
        """Создание файла с правилами"""
        filepath = DATA_FILES['rules']
        with open(filepath, 'w', encoding='utf-8') as f:
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
        print(f"✓ Создан файл: {filepath}")