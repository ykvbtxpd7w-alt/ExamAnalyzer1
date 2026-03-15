from dataclasses import dataclass
from typing import List

# Ваги типів питань
TYPE_WEIGHTS = {
    "theory": 1.0,
    "problem": 1.3,
    "proof": 1.6
}

@dataclass
class Question:
    title: str
    base_complexity: float  # від 0 до 1
    q_type: str             # theory, problem, proof

    def get_complexity(self) -> float:
        weight = TYPE_WEIGHTS.get(self.q_type, 1.0)
        return self.base_complexity * weight

@dataclass
class Ticket:
    id: int
    questions: List[Question]

    def calculate_score(self) -> float:
        if not self.questions:
            return 0.0
        total = sum(q.get_complexity() for q in self.questions)
        return total / len(self.questions)