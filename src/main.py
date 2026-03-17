import os
import json
from models import Ticket
def load_data(filepath):
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_path, filepath)
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)
def main():
    print("ExamAnalyzer v 1.0")
    try:
        raw_data = load_data("./data/tickets.json")
        tickets=[Ticket(**data) for data in raw_data]
        for t in tickets:
            print(f"Білет № {t.id} | Середня складність: {t.calculate_score():.2f}")
    except FileNotFoundError:
        print("Помилка: Файл data/tickets.json не знайдено!")
    except Exception as e:
        print(f"Cталася помилка {e}")

if __name__ == "__main__":
   main()