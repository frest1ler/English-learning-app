"""
Управление прогрессом пользователя
"""

import json
import os
from datetime import datetime
from config import DATA_FILES

class ProgressManager:
    """Класс для управления прогрессом"""
    
    @staticmethod
    def load():
        """Загрузка сохраненного прогресса"""
        try:
            if os.path.exists(DATA_FILES['progress']):
                with open(DATA_FILES['progress'], 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки прогресса: {e}")
        return {'score': 0, 'total_attempts': 0}
    
    @staticmethod
    def save(score, total_attempts):
        """Сохранение прогресса"""
        try:
            progress = {
                'score': score,
                'total_attempts': total_attempts,
                'last_session': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(DATA_FILES['progress'], 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            print("Прогресс сохранен")
            return True
        except Exception as e:
            print(f"Ошибка сохранения прогресса: {e}")
            return False
