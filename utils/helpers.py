"""
Вспомогательные функции
"""

def normalize_answer(answer):
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

def parse_answer_variants(answer_string):
    """
    Парсинг строки с вариантами ответов
    
    Поддерживает форматы:
    - "слово1, слово2" → ['слово1', 'слово2']
    - "слово1 / слово2" → ['слово1', 'слово2']
    - "слово" → ['слово']
    
    Args:
        answer_string: строка с ответом или вариантами
    
    Returns:
        список нормализованных вариантов ответа
    """
    # Разделители для вариантов
    separators = [',', '/', ';']
    
    # Пробуем найти разделитель
    variants = [answer_string]
    for separator in separators:
        if separator in answer_string:
            variants = answer_string.split(separator)
            break
    
    # Нормализуем каждый вариант
    normalized_variants = []
    for variant in variants:
        normalized = normalize_answer(variant)
        if normalized:  # Добавляем только непустые варианты
            normalized_variants.append(normalized)
    
    return normalized_variants

def check_answer_match(user_answer, correct_answer):
    """
    Проверка соответствия ответа с учетом множественных вариантов
    
    Правильными считаются:
    1. Один из вариантов правильного ответа
    2. Несколько вариантов в любом порядке
    3. Все варианты в любом порядке
    
    Args:
        user_answer: ответ пользователя
        correct_answer: правильный ответ (может содержать варианты через запятую/слеш)
    
    Returns:
        True если ответ правильный, False иначе
    """
    # Получаем варианты правильного ответа
    correct_variants = parse_answer_variants(correct_answer)
    
    # Получаем варианты ответа пользователя
    user_variants = parse_answer_variants(user_answer)
    
    # Если пользователь ввел один вариант
    if len(user_variants) == 1:
        # Проверяем, совпадает ли с одним из правильных вариантов
        return user_variants[0] in correct_variants
    
    # Если пользователь ввел несколько вариантов
    # Проверяем, что все введенные варианты есть в правильных
    # и хотя бы один правильный вариант присутствует
    user_set = set(user_variants)
    correct_set = set(correct_variants)
    
    # Все введенные варианты должны быть правильными
    return user_set.issubset(correct_set) and len(user_set) > 0

def format_correct_answer(answer_string):
    """
    Форматирование правильного ответа для отображения
    
    Args:
        answer_string: строка с ответом
    
    Returns:
        отформатированная строка
    """
    variants = parse_answer_variants(answer_string)
    
    if len(variants) == 1:
        return variants[0]
    elif len(variants) == 2:
        return f"{variants[0]} или {variants[1]}"
    else:
        return ", ".join(variants[:-1]) + f" или {variants[-1]}"

def search_in_list(search_term, items, fields):
    """
    Поиск в списке словарей
    
    Args:
        search_term: строка поиска
        items: список словарей
        fields: список полей для поиска
    
    Returns:
        индекс найденного элемента или -1
    """
    search_term = search_term.lower()
    for i, item in enumerate(items):
        for field in fields:
            if search_term in str(item.get(field, '')).lower():
                return i
    return -1