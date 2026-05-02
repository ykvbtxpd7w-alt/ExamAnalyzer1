from engine import generate_tickets
from file_manager import load_json, save_report  # Додано імпорт save_report


def flatten_questions(data):
    """Перетворює список білетів у плоский список усіх питань."""
    return [q for t in data for q in t.get("questions", [])]


def main():
    print("=== ExamAnalyzer v1.0 ===")

    # 1. Завантаження та обробка даних
    data = load_json("data/question_bank.json")  # Перевір шлях ще раз!

    if not data:
        print("❌ Помилка: База даних порожня або не завантажена.")
        return

    # Використовуємо функцію, яку ти написав, замість ручного циклу
    questions = flatten_questions(data)

    print(f"✅ Успішно завантажено питань: {len(questions)}")

    # 2. Діагностика (виправляємо ключі)
    if len(questions) > 0:
        first_q = questions[0]
        # Міняємо 'text' на 'title', бо в JSON саме 'title'
        print(f"📝 Приклад питання: {first_q.get('title', 'Заголовок відсутній')}")
        print(f"🔑 Ключі питання: {list(first_q.keys())}")

    print("-" * 30)

    # 3. Ввід параметрів
    try:
        n = int(input("Кількість білетів: "))
        q_count = int(input("Скільки питань у білеті: "))
        target = float(input("Очікувана складність білета (напр. 2.5): "))
    except ValueError:
        print("❌ Помилка: Вводьте тільки числа!")
        return

    # 4. Генерація
    tickets = generate_tickets(questions, n, q_count, target)

    if not tickets:
        print("❌ Неможливо згенерувати білети з такими параметрами. Спробуйте змінити складність або кількість.")
        return

    # 5. Збереження результатів у файл (замінено вивід у термінал)
    print(f"\n🚀 Згенеровано білетів: {len(tickets)}")

    # Викликаємо функцію збереження для всього списку білетів
    save_report(tickets, "generated_tickets.json")

    print("📂 Перевірте папку 'temp' у вашому проекті.")


if __name__ == "__main__":
    main()
