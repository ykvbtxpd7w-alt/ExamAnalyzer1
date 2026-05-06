from engine import generate_tickets  # Переконайся, що в engine.py вже нова логіка
from file_manager import load_json, save_report


def flatten_questions(data):
    return [q for t in data for q in t.get("questions", [])]


def main():
    print("=== ExamAnalyzer v2.0: Smart Constructor ===")

    data = load_json("data/test_question_bank.json")
    if not data:
        print("❌ Помилка: База даних порожня.")
        return

    questions = flatten_questions(data)
    print(f"✅ Успішно завантажено питань: {len(questions)}")

    print("-" * 30)

    # 3. Ввід параметрів через "Рецепт"
    try:
        n = int(input("Кількість білетів: "))
        print("\nСкладіть структуру білета:")
        e_count = int(input("  - Легких (2 бали): "))
        m_count = int(input("  - Середніх (5 балів): "))
        h_count = int(input("  - Важких (10 балів): "))

        recipe = {"Easy": e_count, "Medium": m_count, "Hard": h_count}

    except ValueError:
        print("❌ Помилка: Вводьте тільки цілі числа!")
        return

    # 4. Генерація через оновлений engine
    # Тепер ми передаємо recipe замість q_count та target
    tickets = generate_tickets(questions, n, recipe)

    if not tickets:
        print("❌ Не вдалося згенерувати. Перевірте, чи достатньо питань у базі.")
        return

    # 5. Звіт
    print(f"\n🚀 Успіх! Згенеровано {len(tickets)} білетів.")
    total_score = (e_count * 2) + (m_count * 5) + (h_count * 10)
    print(f"📊 Балів за кожен білет: {total_score}")

    save_report(tickets, "generated_tickets.json")
    print("📂 Результат збережено у 'temp/generated_tickets.json'")


if __name__ == "__main__":
    main()