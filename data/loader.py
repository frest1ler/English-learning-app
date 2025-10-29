"""
Загрузка данных из файлов
"""

from config import DATA_FILES

class DataLoader:
    """Класс для загрузки данных из файлов"""
    
    @staticmethod
    def load_words():
        """Загрузка слов из файла"""
        try:
            with open(DATA_FILES['words'], 'r', encoding='utf-8') as f:
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
                return words if words else DataLoader.get_default_words()
        except FileNotFoundError:
            from data.sample_creator import SampleCreator
            SampleCreator.create_all_files()
            return DataLoader.load_words()
        except Exception as e:
            print(f"Ошибка загрузки слов: {e}")
            return DataLoader.get_default_words()
    
    @staticmethod
    def get_default_words():
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
    
    @staticmethod
    def load_exercises():
        """Загрузка упражнений из файла"""
        try:
            with open(DATA_FILES['exercises'], 'r', encoding='utf-8') as f:
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
            from data.sample_creator import SampleCreator
            SampleCreator.create_all_files()
            return DataLoader.load_exercises()
    
    @staticmethod
    def load_rules():
        """Загрузка правил из файла"""
        try:
            with open(DATA_FILES['rules'], 'r', encoding='utf-8') as f:
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
    
    @staticmethod
    def save_word(word_data):
        """Сохранение нового слова в файл"""
        try:
            with open(DATA_FILES['words'], 'a', encoding='utf-8') as f:
                line = f"\n{word_data['word']} | {word_data['translation']} | {word_data['transcription']}"
                if word_data.get('example'):
                    line += f" | {word_data['example']}"
                if word_data.get('example_translation'):
                    line += f" | {word_data['example_translation']}"
                f.write(line)
            return True
        except Exception as e:
            print(f"Ошибка сохранения слова: {e}")
            return False
