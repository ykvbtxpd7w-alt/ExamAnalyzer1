import json
import os
import random
class ExamEngine:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path=os.path.join(self.base_dir, "..", "data")
    def get_all_subjects(self):
        try:
            files=[f.replace(".json","") for f in os.listdir(self.data_path) if f.endswith(".json")]
            return files
        except Exception as e:
          print(f"Помилка доступу до бази {e}")
          return []
    def get_topics_list(self, subject_id):
        try:
            # Треба додати назву файлу до шляху!
            file_path = os.path.join(self.data_path, f"{subject_id}.json")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return list(data.keys())
        except Exception as e:
            print(f"Помилка читання тем: {e}")
            return []
    def generate_exam(self, subject_id, selected_topics, difficulty_recipe, n_tickets):
        file_path = os.path.join(self.data_path, f"{subject_id}.json")
        with open(file_path, "r", encoding="utf-8") as f:
            full_db = json.load(f)
        pool=[]
        for topic in selected_topics:
            if topic in full_db:
                pool.extend(full_db[topic])
        random.shuffle(pool)
        tickets=[]
        usage_tracker={}
        for i in range (n_tickets):
            current_ticket_question=[]
            for diff_name, count in difficulty_recipe.items():
                if count<=0:
                    continue
                candidates = []
                for q in pool:
                    if q["category"] == diff_name:
                        candidates.append(q)
                candidates.sort(key=lambda q: usage_tracker.get(q["title"], 0))
                if len(candidates)>=count:
                    selected=candidates[:count]
                else:
                    selected=candidates
                for q in selected:
                    usage_tracker[q["title"]]=usage_tracker.get(q["title"], 0) + 1
                    current_ticket_question.append(q)
            random.shuffle(current_ticket_question)
            tickets.append({
                "number": i + 1,
                "subject": subject_id,
                "questions": current_ticket_question,
                "total_points": sum(q['points'] for q in current_ticket_question)
            })

        return tickets
