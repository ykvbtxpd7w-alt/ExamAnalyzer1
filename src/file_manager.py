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
    """Створює професійний PDF-звіт з розподілом по балах"""
    # 1. Налаштування шляхів
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(src_dir)
    temp_path = os.path.join(project_root, "temp")

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    # Гарантуємо розширення .pdf
    if not filename.endswith(".pdf"):
        filename = filename.rsplit('.', 1)[0] + ".pdf"

    file_path = os.path.join(temp_path, filename)

    # 2. Створення PDF
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(left=20, top=20, right=20)
    pdf.add_page()

    # 3. Підключення шрифту (переконайся, що arial.ttf лежить в папці src)
    font_path = os.path.join(src_dir, "arial.ttf")
    if not os.path.exists(font_path):
        print(f"❌ ПОМИЛКА: Шрифт не знайдено за шляхом: {font_path}")
        return

    pdf.add_font('ArialUkr', '', font_path)

    # 4. Заголовок документа
    pdf.set_font('ArialUkr', size=20)
    pdf.cell(w=0, h=15, txt="Екзаменаційні білети", ln=True, align='C')
    pdf.ln(5)

    # 5. Друк білетів
    # 5. Друк білетів
    for i, ticket_data in enumerate(tickets, 1):
        if pdf.get_y() > 220:
            pdf.add_page()

        # --- ТУТ ПРАВКА ---
        # Перевіряємо: якщо ticket_data це список, а не словник
        if isinstance(ticket_data, list):
            questions = ticket_data
            total_p = sum(q.get("points", 0) for q in questions)
        else:
            questions = ticket_data.get("questions", [])
            total_p = ticket_data.get("total_points", 0)
        # ------------------

        # Шапка білета
        pdf.set_font('ArialUkr', size=14)
        pdf.cell(w=85, h=10, txt=f"БІЛЕТ №{i}", ln=False)

        pdf.set_font('ArialUkr', size=10)
        pdf.cell(w=85, h=10, txt=f"Максимальний бал: {total_p}", ln=True, align='R')
        pdf.ln(2)

        # Список питань
        pdf.set_font('ArialUkr', size=12)
        for j, q in enumerate(questions, 1):
            title = q.get('title', 'Питання без назви')
            pts = q.get('points', 0)
            full_text = f"{j}. {title} ({pts} балів)"
            pdf.multi_cell(w=170, h=8, txt=full_text)
            pdf.ln(1)

    # 6. Збереження та відкриття
    try:
        pdf.output(file_path)
        print(f"✅ Успіх! PDF створено: {file_path}")

        # Для macOS використовуємо 'open', для Windows було б os.startfile
        import platform
        if platform.system() == "Darwin":  # macOS
            os.system(f'open "{file_path}"')
        elif platform.system() == "Windows":
            os.startfile(file_path)

    except Exception as e:
        print(f"❌ Помилка при записі PDF: {e}")