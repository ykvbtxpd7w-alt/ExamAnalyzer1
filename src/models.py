class Question:
    def __init__(self, title, base_complexity, q_type):
        self.title = title
        self.base_complexity = base_complexity
        self.q_type = q_type
    def get_real_complexity(self):
        multipliers={"theory":1.0, "problem":1.2, "proof":1.5}
        return self.base_complexity * multipliers.get(self.q_type, 1.0)
class Ticket:
    def __init__(self, id, questions):
        self.id = id
        self.questions = [Question(**q) for q in questions]
    def calculate_score(self):
        if not self.questions:
            return 0
        return sum(q.get_real_complexity() for q in self.questions)/len(self.questions)