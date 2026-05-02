from engine import generate_tickets
from file_manager import load_json


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

    # 5. Гарний вивід результатів
    print(f"\n🚀 Згенеровано білетів: {len(tickets)}")
    for i, ticket in enumerate(tickets, 1):
        total_complexity = sum(q["base_complexity"] for q in ticket)

        print(f"\n" + "=" * 40)
        print(f"🎟 БІЛЕТ №{i}")
        print(f"📊 Сумарна складність: {round(total_complexity, 2)}")
        print("-" * 40)

        for j, q in enumerate(ticket, 1):
            # Використовуємо title та base_complexity
            print(f"{j}. {q.get('title', 'Без назви')} [Складність: {q.get('base_complexity', 0)}]")
        print("=" * 40)


if __name__ == "__main__":
    main()