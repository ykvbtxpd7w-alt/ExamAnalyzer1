import os
import json
from fpdf import FPDF

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





def save_report(tickets, filename="generated_tickets.pdf"):
    """Створює PDF-звіт з білетами"""
    # 1. Налаштування шляхів
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(src_dir)
    temp_path = os.path.join(project_root, "temp")

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    # Завжди робимо файл .pdf
    if not filename.endswith(".pdf"):
        filename = filename.rsplit('.', 1)[0] + ".pdf"

    file_path = os.path.join(temp_path, filename)

    # 2. Створення PDF з полями (margins)
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(left=20, top=20, right=20)  # Чітко задаємо поля
    pdf.add_page()

    # 3. Підключення шрифту
    font_path = os.path.join(src_dir, "arial.ttf")
    if not os.path.exists(font_path):
        print(f"❌ Файл шрифту не знайдено: {font_path}")
        return

    pdf.add_font('ArialUkr', '', font_path)

    # 4. Друк заголовка
    pdf.set_font('ArialUkr', size=18)
    pdf.cell(w=0, h=10, txt="Екзаменаційні білети", ln=True, align='C')
    pdf.ln(10)

    # 5. Друк білетів
    for i, ticket in enumerate(tickets, 1):
        # Перевіряємо, чи не кінець сторінки (якщо залишилося мало місця — нова сторінка)
        if pdf.get_y() > 250:
            pdf.add_page()

        # Номер білета
        pdf.set_font('ArialUkr', size=14)
        pdf.cell(w=0, h=10, txt=f"БІЛЕТ №{i}", ln=True)

        # Складність
        total_complexity = sum(q.get("base_complexity", 0) for q in ticket)
        pdf.set_font('ArialUkr', size=10)
        pdf.cell(w=0, h=8, txt=f"Складність: {round(total_complexity, 2)}", ln=True)
        pdf.ln(2)

        # Питання (використовуємо multi_cell з явною шириною)
        pdf.set_font('ArialUkr', size=12)
        for j, q in enumerate(ticket, 1):
            title = q.get('title', 'Питання без назви')
            # Вказуємо ширину 170мм (A4 210мм - поля 40мм)
            pdf.multi_cell(w=170, h=8, txt=f"{j}. {title}")
            pdf.ln(2)

        pdf.ln(5)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())  # Лінія-розділювач
        pdf.ln(10)

    # 6. Збереження
    try:
        pdf.output(file_path)
        print(f"✅ Успіх! PDF створено: {file_path}")
        os.startfile(file_path)
    except Exception as e:
        print(f"❌ Помилка при записі PDF: {e}")
