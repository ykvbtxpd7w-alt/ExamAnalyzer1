import json
import os


def load_json(path):
    # 1. Отримуємо абсолютний шлях (щоб не було проблем із папками)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Якщо main.py в src, а база в data, треба піднятися на рівень вище (..)
    full_path = os.path.join(base_dir, "..", path)

    # Видаляємо дублювання папок, якщо вони є
    full_path = full_path.replace("data/data/", "data/")

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            # ✅ МАЄ БУТИ json.load(f), а не load_json(path)!
            return json.load(f)
    except FileNotFoundError:
        print(f"Помилка: Файл {full_path} не знайдено!")
        return []
    except json.JSONDecodeError:
        print(f"Помилка: Файл {full_path} має пошкоджений JSON!")
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