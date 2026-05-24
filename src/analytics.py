def _ticket_scores(tickets):
    return [ticket.get("difficulty_score", 0) for ticket in tickets if ticket.get("questions")]


def summarize_ticket_set(tickets):
    scores = _ticket_scores(tickets)
    if not scores:
        return {
            "average_difficulty": 0,
            "min_difficulty": 0,
            "max_difficulty": 0,
            "variance": 0,
            "easiest_ticket": None,
            "hardest_ticket": None,
        }

    average = sum(scores) / len(scores)
    variance = sum((score - average) ** 2 for score in scores) / len(scores)
    hardest = max(tickets, key=lambda ticket: ticket.get("difficulty_score", 0))
    easiest = min(tickets, key=lambda ticket: ticket.get("difficulty_score", 0))

    return {
        "average_difficulty": round(average, 3),
        "min_difficulty": round(min(scores), 3),
        "max_difficulty": round(max(scores), 3),
        "variance": round(variance, 3),
        "easiest_ticket": easiest.get("number"),
        "hardest_ticket": hardest.get("number"),
    }
