# Ручний smoke-тест бекенду. Не покладайтесь на нього в CI:
# PDF зберігається через діалог, а не у корінь проєкту.
from main import ExamApp


def test_full_cycle():
    print("🚀 Починаємо тест бекенду...")

    # 1. Ініціалізуємо додаток
    app = ExamApp()

    # 2. Імітуємо Крок 1: Вибір предмета
    subject = "math_analysis"
    topics = app.on_subject_select(subject)
    print(f"✅ Крок 1: Предмет '{subject}' вибрано. Знайдено тем: {len(topics)}")
    print(f"📋 Список тем: {topics}")

    # 3. Імітуємо Крок 2: Вибір конкретних тем (наприклад, перші дві)
    if len(topics) >= 2:
        app.selected_topics = ["Похідні", "Множини", "Ліміти", "Інтеграли"] # Виберіть кілька назв зі списку
    else:
        app.selected_topics = topics
    print(f"✅ Крок 2: Обрано теми: {app.selected_topics}")

    # 4. Імітуємо Крок 3 та 4: Налаштування рецепту та кількості
    app.recipe = {"Easy": 3, "Medium": 3, "Hard": 3}  # 4 питання на білет
    app.ticket_count = 10  # Згенеруємо 5 білетів для тесту
    print(f"✅ Крок 3/4: Рецепт {app.recipe}, Кількість білетів: {app.ticket_count}")

    # 5. Імітуємо Крок 5: Генерація
    print("⚙️ Геруємо білети...")
    tickets = app.on_generate_click()

    if tickets and len(tickets) == 10:
        print(f"✅ Крок 5: Успішно згенеровано {len(tickets)} білетів!")
        # Перевіримо перший білет
        first_t = tickets[0]
        print(f"   - Перший білет має {len(first_t['questions'])} питань.")
        print(f"   - Сума балів: {first_t['total_points']}")
    else:
        print("❌ Помилка на етапі генерації!")
        return

    # 6. Фінальний крок: Збереження в PDF
    print("📄 Формуємо PDF...")
    app.on_save_pdf()

    if os.path.exists(f"{subject}_report.pdf"):
        print(f"🎉 ТЕСТ ЗАВЕРШЕНО УСПІШНО! Файл '{subject}_report.pdf' створено.")
    else:
        print("❌ PDF файл не було знайдено.")


if __name__ == "__main__":
    import os

    test_full_cycle()