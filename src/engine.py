import random


def generate_one_ticket_by_recipe(questions, recipe, usage):
    """
    questions: список усіх питань з категоріями
    recipe: словник {'Easy': 10, 'Medium': 5, 'Hard': 2}
    usage: словник для відстеження частоти використання
    """
    ticket = []

    # Йдемо по кожному типу питань у рецепті
    for category, count in recipe.items():
        # Фільтруємо кошик під конкретну категорію
        pool = [q for q in questions if q.get("category") == category]

        # Сортуємо за використанням (як у тебе було), щоб брати ті, що рідше зустрічались
        pool.sort(key=lambda q: usage.get(q["title"], 0))

        if len(pool) < count:
            print(f"⚠️ Не вистачає питань категорії {category}!")
            return None

        # Беремо перші 'count' питань з тих, що найменше використовувались
        # (додаємо трохи рандому серед питань з однаковим використанням)
        top_slice = pool[:count + 5]  # беремо трохи з запасом
        selected = random.sample(top_slice, count)

        ticket.extend(selected)

    random.shuffle(ticket)  # Перемішуємо, щоб категорії не йшли блоками
    return ticket


def generate_tickets(questions, ticket_count, recipe):
    tickets = []
    usage = {}

    for i in range(ticket_count):
        ticket = generate_one_ticket_by_recipe(questions, recipe, usage)

        if not ticket:
            break

        # Оновлюємо статистику використання
        for q in ticket:
            usage[q["title"]] = usage.get(q["title"], 0) + 1

        tickets.append(ticket)

    return tickets