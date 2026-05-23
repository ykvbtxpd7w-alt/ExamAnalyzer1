import json
import os
import random


class ExamEngine:
    TYPE_WEIGHTS = {"theory": 1.0, "problem": 1.3, "proof": 1.6}
    CATEGORY_BASE_COMPLEXITY = {"Easy": 0.35, "Medium": 0.65, "Hard": 0.9}
    CATEGORY_TYPES = {"Easy": "theory", "Medium": "problem", "Hard": "proof"}
    DIFFICULTY_ORDER = {"Easy": 1, "Medium": 2, "Hard": 3}

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(self.base_dir, "..", "data")

    def get_all_subjects(self):
        try:
            files = [f.replace(".json", "") for f in os.listdir(self.data_path) if f.endswith(".json")]
            return files
        except Exception as e:
            print(f"Помилка доступу до бази {e}")
            return []

    def get_topics_list(self, subject_id):
        try:
            file_path = os.path.join(self.data_path, f"{subject_id}.json")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return list(data.keys())
        except Exception as e:
            print(f"Помилка читання тем: {e}")
            return []

    def get_question_type(self, question):
        if question.get("q_type"):
            return question["q_type"]
        if question.get("type"):
            return question["type"]
        return self.CATEGORY_TYPES.get(question.get("category"), "theory")

    def get_base_complexity(self, question):
        if "base_complexity" in question:
            return float(question["base_complexity"])
        return self.CATEGORY_BASE_COMPLEXITY.get(question.get("category"), 0.5)

    def calculate_question_score(self, question):
        base_complexity = self.get_base_complexity(question)
        question_type = self.get_question_type(question)
        type_weight = self.TYPE_WEIGHTS.get(question_type, 1.0)
        return base_complexity * type_weight

    def get_question_category(self, question):
        if question.get("category"):
            return question["category"]

        score = self.calculate_question_score(question)
        if score <= 0.6:
            return "Easy"
        if score <= 1.0:
            return "Medium"
        return "Hard"

    def normalize_question(self, question):
        normalized = dict(question)
        category = self.get_question_category(normalized)
        question_type = self.get_question_type(normalized)
        base_complexity = self.get_base_complexity(normalized)
        type_weight = self.TYPE_WEIGHTS.get(question_type, 1.0)
        real_complexity = base_complexity * type_weight

        normalized["category"] = category
        normalized["q_type"] = question_type
        normalized["base_complexity"] = round(base_complexity, 3)
        normalized["type_weight"] = type_weight
        normalized["real_complexity"] = round(real_complexity, 3)
        normalized["source_points"] = normalized.get("points", 0)
        return normalized

    def calculate_ticket_score(self, questions):
        if not questions:
            return 0
        scores = [self.calculate_question_score(q) for q in questions]
        return sum(scores) / len(scores)

    def distribute_ticket_points(self, questions, target_total_points):
        if not questions:
            return questions

        target_total_points = max(1, int(target_total_points))
        minimum_per_question = 1 if target_total_points >= len(questions) else 0
        distributable_points = target_total_points - minimum_per_question * len(questions)
        total_complexity = sum(q.get("real_complexity", 0) for q in questions)

        if total_complexity <= 0:
            base_points = target_total_points // len(questions)
            remainder = target_total_points % len(questions)
            for index, question in enumerate(questions):
                question["points"] = base_points + (1 if index < remainder else 0)
            return questions

        raw_points = [
            q.get("real_complexity", 0) / total_complexity * distributable_points
            for q in questions
        ]
        rounded_down = [int(value) for value in raw_points]
        remainder = distributable_points - sum(rounded_down)
        by_fraction = sorted(
            range(len(raw_points)),
            key=lambda index: raw_points[index] - rounded_down[index],
            reverse=True
        )

        for index in by_fraction[:remainder]:
            rounded_down[index] += 1

        for question, points in zip(questions, rounded_down):
            question["points"] = points + minimum_per_question

        return questions

    def generate_exam(self, subject_id, selected_topics, difficulty_recipe, n_tickets, target_total_points=100):
        file_path = os.path.join(self.data_path, f"{subject_id}.json")
        with open(file_path, "r", encoding="utf-8") as f:
            full_db = json.load(f)

        pool = []
        for topic in selected_topics:
            if topic in full_db:
                pool.extend(full_db[topic])

        # Перемішуємо пул для рандомізації тем
        random.shuffle(pool)

        tickets = []
        usage_tracker = {}

        for i in range(n_tickets):
            current_ticket_questions = []

            # Збираємо питання всіх рівнів складності в один кошик білета
            for diff_name, count in difficulty_recipe.items():
                if count <= 0:
                    continue

                candidates = [q for q in pool if self.get_question_category(q) == diff_name]

                # Сортуємо кандидатів за вживаністю (найменш вживані — перші)
                candidates.sort(key=lambda q: usage_tracker.get(q["title"], 0))

                selected = candidates[:count]

                for q in selected:
                    usage_tracker[q["title"]] = usage_tracker.get(q["title"], 0) + 1
                    current_ticket_questions.append(self.normalize_question(q))

            # СОРТУВАННЯ: Тепер один раз сортуємо весь білет від легкого до складного
            current_ticket_questions.sort(
                key=lambda q: (
                    self.DIFFICULTY_ORDER.get(q.get('category', 'Easy'), 1),
                    q.get('real_complexity', 0),
                    q.get('title')
                )
            )

            ticket_score = self.calculate_ticket_score(current_ticket_questions)
            current_ticket_questions = self.distribute_ticket_points(
                current_ticket_questions,
                target_total_points
            )

            # ДОДАВАННЯ: Додаємо готовий білет у список ОДИН раз
            tickets.append({
                "number": i + 1,
                "subject": subject_id,
                "questions": current_ticket_questions,
                "total_points": sum(q.get('points', 0) for q in current_ticket_questions),
                "difficulty_score": round(ticket_score, 3)
            })

        return tickets
