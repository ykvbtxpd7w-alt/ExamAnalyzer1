from engine import generate_tickets
from file_manager import load_json


def flatten_questions(data):
    return [q for t in data for q in t["questions"]]


def main():
    print("ExamAnalyzer v1.0")

    data = load_json("data/question_bank.json")
    questions = flatten_questions(data)

    # 👇 тільки 3 параметри
    n = int(input("Кількість білетів: "))
    q_count = int(input("Скільки питань у білеті: "))
    target = float(input("Очікувана складність білета: "))

    tickets = generate_tickets(questions, n, q_count, target)

    if not tickets:
        print("❌ Неможливо згенерувати білети з такими параметрами")
        return

    for i, ticket in enumerate(tickets, 1):
        total = sum(q["base_complexity"] for q in ticket)

        print(f"\n🎟 Білет №{i} (сумарна складність: {round(total, 2)}):\n")

        for j, q in enumerate(ticket, 1):
            print(f"{j}. {q['title']} ({q['base_complexity']})")


if __name__ == "__main__":
    main()