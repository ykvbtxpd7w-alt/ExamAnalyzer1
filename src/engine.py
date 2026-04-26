import random


def generate_one_ticket(questions, count, target, tolerance, usage):
    shuffled = questions[:]
    random.shuffle(shuffled)

    shuffled.sort(key=lambda q: usage.get(q["title"], 0))

    result = []

    def backtrack(start, current_ticket, current_sum):
        if len(current_ticket) == count:
            if abs(current_sum - target) <= tolerance:
                result.extend(current_ticket)
                return True
            return False

        if current_sum > target + tolerance:
            return False

        for i in range(start, len(shuffled)):
            q = shuffled[i]

            remaining = count - len(current_ticket) - 1

            min_possible = current_sum + q["base_complexity"]
            max_possible = (
                current_sum
                + q["base_complexity"]
                + remaining * shuffled[-1]["base_complexity"]
            )

            if min_possible > target + tolerance:
                continue
            if max_possible < target - tolerance:
                continue

            current_ticket.append(q)

            if backtrack(i + 1, current_ticket, current_sum + q["base_complexity"]):
                return True

            current_ticket.pop()

        return False

    success = backtrack(0, [], 0)
    return result if success else None


def generate_tickets(questions, ticket_count, questions_per_ticket, target):
    tolerance = 0.1  # 🔥 фіксовано тут

    tickets = []
    usage = {}

    attempts = 0
    max_attempts = ticket_count * 10

    while len(tickets) < ticket_count and attempts < max_attempts:
        ticket = generate_one_ticket(
            questions,
            questions_per_ticket,
            target,
            tolerance,
            usage
        )

        attempts += 1

        if not ticket:
            continue

        for q in ticket:
            usage[q["title"]] = usage.get(q["title"], 0) + 1

        tickets.append(ticket)

    return tickets