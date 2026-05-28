import json
import os
import random

from history import EXCLUDED_SUBJECT_IDS, is_subject_bank_file


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
            files = [
                f.replace(".json", "")
                for f in os.listdir(self.data_path)
                if is_subject_bank_file(f)
            ]
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

    def get_estimated_time(self, question):
        """Optional minutes to solve. Default 3 only when the field is present but empty."""
        if "estimated_time" not in question:
            return None
        value = question.get("estimated_time")
        if value is None:
            return 3.0
        return float(value)

    def get_time_factor(self, question):
        """
        Backward compatibility: legacy JSON without `estimated_time` keeps factor 1.0,
        so real_complexity matches the old base_complexity * type_weight formula.

        When `estimated_time` is set, apply a weak adjustment (divide by 20) so longer
        tasks nudge balancing without dominating category/type weights.
        """
        estimated_time = self.get_estimated_time(question)
        if estimated_time is None:
            return 1.0
        return 1 + (estimated_time / 20)

    def calculate_real_complexity(self, question):
        base_complexity = self.get_base_complexity(question)
        question_type = self.get_question_type(question)
        type_weight = self.TYPE_WEIGHTS.get(question_type, 1.0)
        time_factor = self.get_time_factor(question)
        return base_complexity * type_weight * time_factor

    def calculate_question_score(self, question):
        return self.calculate_real_complexity(question)

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
        time_factor = self.get_time_factor(normalized)
        real_complexity = base_complexity * type_weight * time_factor

        normalized["category"] = category
        normalized["q_type"] = question_type
        normalized["base_complexity"] = round(base_complexity, 3)
        normalized["type_weight"] = type_weight
        normalized["time_factor"] = round(time_factor, 3)
        if "estimated_time" in question:
            normalized["estimated_time"] = round(self.get_estimated_time(question), 3)
        normalized["real_complexity"] = round(real_complexity, 3)
        normalized["source_points"] = normalized.get("points", 0)
        return normalized

    def calculate_ticket_score(self, questions):
        if not questions:
            return 0
        scores = [self.calculate_question_score(q) for q in questions]
        return sum(scores) / len(scores)

    def validate_generation_request(self, pool, difficulty_recipe, n_tickets, target_total_points):
        if n_tickets <= 0:
            raise ValueError("Кількість білетів має бути більшою за 0.")

        questions_per_ticket = sum(count for count in difficulty_recipe.values() if count > 0)
        if questions_per_ticket <= 0:
            raise ValueError("У білеті має бути хоча б одне питання.")

        if target_total_points < questions_per_ticket:
            raise ValueError(
                "Загальна кількість балів має бути не меншою за кількість питань у білеті. "
                f"Питань: {questions_per_ticket}, балів: {target_total_points}."
            )

        missing = []
        for diff_name, count in difficulty_recipe.items():
            if count <= 0:
                continue

            available = sum(1 for q in pool if self.get_question_category(q) == diff_name)
            if available == 0:
                missing.append(f"{diff_name}: у банку немає питань цього рівня")

        if missing:
            raise ValueError(
                "Неможливо зібрати білет з обраною структурою.\n"
                + "\n".join(missing)
                + "\nДодайте питання в банк або змініть розкладку."
            )

    def _category_pool(self, pool, diff_name):
        return [q for q in pool if self.get_question_category(q) == diff_name]

    def select_questions_for_category(self, pool, diff_name, count, usage_counts):
        if count <= 0:
            return []

        category_pool = self._category_pool(pool, diff_name)
        if not category_pool:
            raise ValueError(f"У банку немає питань рівня {diff_name}.")

        unused = [
            q for q in category_pool
            if usage_counts.get(q.get("title"), 0) == 0
        ]
        random.shuffle(unused)

        selected = []
        for question in unused:
            if len(selected) >= count:
                break
            selected.append(question)

        if len(selected) < count:
            reuse_pool = sorted(
                category_pool,
                key=lambda q: (usage_counts.get(q.get("title"), 0), q.get("title", "")),
            )
            titles_in_ticket = {q.get("title") for q in selected}

            for question in reuse_pool:
                if len(selected) >= count:
                    break
                title = question.get("title")
                if title in titles_in_ticket:
                    continue
                selected.append(question)
                titles_in_ticket.add(title)

            while len(selected) < count:
                question = reuse_pool[len(selected) % len(reuse_pool)]
                selected.append(question)

        normalized = []
        for question in selected:
            title = question.get("title", "")
            item = self.normalize_question(question)
            item["is_repeat"] = usage_counts.get(title, 0) > 0
            usage_counts[title] = usage_counts.get(title, 0) + 1
            normalized.append(item)

        return normalized

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

    def generate_exam(
        self,
        subject_id,
        selected_topics,
        difficulty_recipe,
        n_tickets,
        target_total_points=100,
        seed=None,
    ):
        if subject_id in EXCLUDED_SUBJECT_IDS:
            raise ValueError(f"Невідомий предмет: {subject_id}")

        file_path = os.path.join(self.data_path, f"{subject_id}.json")
        with open(file_path, "r", encoding="utf-8") as f:
            full_db = json.load(f)

        if seed is not None:
            random.seed(int(seed))

        pool = []
        for topic in selected_topics:
            if topic in full_db:
                for question in full_db[topic]:
                    question_with_topic = dict(question)
                    question_with_topic["topic"] = topic
                    pool.append(question_with_topic)

        if not pool:
            raise ValueError("Для вибраних тем не знайдено жодного питання.")

        self.validate_generation_request(pool, difficulty_recipe, n_tickets, target_total_points)

        # Перемішуємо пул для рандомізації тем
        random.shuffle(pool)

        tickets = []
        usage_counts = {}

        for i in range(n_tickets):
            current_ticket_questions = []

            for diff_name, count in difficulty_recipe.items():
                if count <= 0:
                    continue

                current_ticket_questions.extend(
                    self.select_questions_for_category(
                        pool,
                        diff_name,
                        count,
                        usage_counts,
                    )
                )

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
