import json
import os

def load_questions(filename="questions.json"):
    """Читає список питань з JSON-файлу в папці data/"""
    # Будуємо шлях до файлу: проєкт/data/questions.json
    path = os.path.join("data", filename)
    
    if not os.path.exists(path):
        print(f"Помилка: Файл {path} не знайдено!")
        return []

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Сталася помилка при читанні: {e}")
        return []

def save_report(ticket, filename="ticket_report.txt"):
    """Записує дані білета у текстовий файл у папку temp/"""
    # Створюємо папку temp, якщо її ще немає
    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    path = os.path.join("temp", filename)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(ticket))
        print(f"Звіт збережено у: {path}")
    except Exception as e:
        print(f"Не вдалося зберегти файл: {e}")
