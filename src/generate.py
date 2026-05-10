import json
import random
import os


def fillup_db():
    # 1. Правильно визначаємо шлях до папки data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Якщо скрипт у /src, а база у /data, шлях буде такий:
    data_path = os.path.join(base_dir, '..', 'data')

    file_to_fillup = {
        "math_analysis.json": ["Інтеграли", "Похідні", "Множини", "Ліміти", "Ряди", "Диф. рівняння"],
        "physics.json": ["Механіка", "Термодинаміка", "Оптика", "Електрика", "Квантова фізика"]
    }

    categories = [
        {"name": "Easy", "pts": 2},
        {"name": "Medium", "pts": 5},
        {"name": "Hard", "pts": 10}
    ]

    for filename, topics in file_to_fillup.items():
        file_full_path = os.path.join(data_path, filename)

        if not os.path.exists(file_full_path):
            print(f"❌ Файл {filename} не знайдено за шляхом {file_full_path}")
            continue

        massive_data = {}
        for topic in topics:
            massive_data[topic] = []  # Створюємо список для кожної теми
            for i in range(1, 101):
                cat = random.choice(categories)
                # Додаємо питання саме в список поточної ТЕМИ
                massive_data[topic].append({
                    "title": f"{topic}: Питання №{i} ({cat['name']})",
                    "category": cat["name"],
                    "points": cat["pts"],
                    "usage_count": 0
                })

        # 2. Записуємо у файл ОДИН РАЗ після завершення збору всіх даних для предмета
        with open(file_full_path, 'w', encoding='utf-8') as f:
            json.dump(massive_data, f, ensure_ascii=False, indent=4)

        print(f"✅ Файл {filename} успішно заповнений!")


if __name__ == "__main__":
    fillup_db()
