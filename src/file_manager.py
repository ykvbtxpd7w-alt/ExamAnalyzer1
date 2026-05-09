from fpdf import FPDF
import os



def save_report_pdf(tickets, subject_name=f"Exam "):
    # Створюємо PDF з явною орієнтацією та форматом
    pdf = FPDF(orientation='P', unit='mm', format='A4')

    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_regular = os.path.join(current_dir, "arial.ttf")
    font_bold = os.path.join(current_dir, "arialbd.ttf")

    # Додаємо шрифти
    pdf.add_font("CustomArial", "", font_regular)
    pdf.add_font("CustomArial", "B", font_bold)

    pdf.set_auto_page_break(auto=True, margin=15)

    # Вираховуємо доступну ширину (A4 = 210мм, мінус поля по 10мм з обох боків)
    effective_width = pdf.w - 20

    for ticket in tickets:
        pdf.add_page()

        # Заголовок
        pdf.set_font("CustomArial", "B", 16)
        pdf.cell(effective_width, 10, f"Екзаменаційний білет №{ticket['number']}", ln=True, align='C')

        pdf.set_font("CustomArial", "", 12)
        subject_title = subject_name.replace('_', ' ').capitalize()
        pdf.cell(effective_width, 10, f"Предмет: {subject_title}", ln=True, align='C')
        pdf.ln(10)

        # Поля для заповнення
        pdf.set_font("CustomArial", "", 11)
        pdf.cell(effective_width, 10, "Студент: __________________________  Група: _________", ln=True)
        pdf.ln(5)

        # Питання
        pdf.set_font("CustomArial", "B", 12)
        pdf.cell(effective_width, 10, "Питання:", ln=True)
        pdf.ln(2)

        pdf.set_font("CustomArial", "", 11)
        for idx, q in enumerate(ticket['questions'], 1):
            # Замість 0 використовуємо effective_width для точності
            text = f"{idx}. {q['title']} ({q['points']} б.)"
            # Переконуємося, що текст — це рядок
            pdf.multi_cell(effective_width, 8, str(text), border=0)
            pdf.ln(2)  # Невеликий відступ між питаннями

        # Підсумок
        pdf.ln(5)
        pdf.set_font("CustomArial", "B", 10)
        pdf.cell(effective_width, 10, f"Всього балів: {ticket['total_points']}", ln=True, align='R')

    output_name = f"{subject_name}_report.pdf"
    pdf.output(output_name)
    print(f"✅ PDF '{output_name}' успішно створено!")