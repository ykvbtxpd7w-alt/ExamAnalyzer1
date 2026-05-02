import json
import os
import random


def crate_fake_db(filename, num_blocks):
    # Використовуємо множину для назв списків
    subjects_list = ["Python", "Math", "Algorithms", "Databases", "Networks"]
    q_types_list = ["theory", "problem", "proof"]

    new_data = []

    for i in range(1, num_blocks + 1):
        chosen_subject = random.choice(subjects_list)

        # Створюємо структуру БЛОКУ (квитка), яку чекає твій двигун
        block = {
            "id": i,
            "subject": chosen_subject,
            "questions": []  # Має бути questions (множина)
        }

        for j in range(random.randint(2, 3)):
            complexity = round(random.uniform(0.3, 0.95), 2)
            chosen_type = random.choice(q_types_list)

            question = {
                "title": f"Питання з теми {chosen_subject} #{i * 10 + j}: вивчення {chosen_type}",
                "base_complexity": complexity,
                "q_type": chosen_type
            }
            block["questions"].append(question)

        # Додаємо ВЕСЬ БЛОК у фінальний список
        new_data.append(block)

    # Логіка шляхів
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Переконайся, що папка data існує, або прибери її зі шляху
    filepath = os.path.join(base_dir, "..", "data", filename)

    # Створюємо папку, якщо вона відсутня
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Готово! Створено {num_blocks} блоків у файлі: {filepath}")


# Виносимо за межі функції
if __name__ == "__main__":
    crate_fake_db("test_question_bank.json", num_blocks=150)