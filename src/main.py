from engine import ExamEngine
from file_manager import save_report_pdf
from history import (
    append_history_entry,
    build_history_entry,
    calculate_bank_fingerprint,
    load_history,
    make_seed,
)
import json
import os
from tkinter import filedialog, messagebox

class ExamApp:
    def __init__(self):
        self.engine = ExamEngine()
        self.selected_subject=None
        self.selected_topics=[]
        self.recipe={"Easy": 0, "Medium": 0, "Hard": 0}
        self.ticket_count=0
        self.total_points=100
        self.generated_data=None
        self.last_generation_seed=None
        self.last_history_entry=None
    def on_subject_select(self, subject_id):
        self.selected_subject = subject_id
        self.selected_topics = []
        topics=self.engine.get_topics_list(subject_id)
        return topics
    def get_session_history(self):
        return list(reversed(load_history(self.engine.data_path)))

    def add_custom_question(self, *, subject_id, topic, title, category):
        if not subject_id:
            raise ValueError("Оберіть предмет.")
        if not topic or not topic.strip():
            raise ValueError("Вкажіть тему.")
        if not title or not title.strip():
            raise ValueError("Вкажіть текст питання.")
        if category not in {"Easy", "Medium", "Hard"}:
            raise ValueError("Невірна складність (Easy/Medium/Hard).")

        topic = topic.strip()
        title = title.strip()

        bank_path = os.path.join(self.engine.data_path, f"{subject_id}.json")
        try:
            with open(bank_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception as e:
            raise ValueError(f"Не вдалось прочитати банк: {e}")

        if not isinstance(data, dict):
            raise ValueError("Невірний формат банку питань (очікується словник тем).")

        questions = data.get(topic, [])
        if not isinstance(questions, list):
            questions = []

        if any(q.get("title") == title for q in questions if isinstance(q, dict)):
            raise ValueError("Таке питання вже є в цій темі.")

        default_points = {"Easy": 2, "Medium": 5, "Hard": 10}
        questions.append(
            {
                "title": title,
                "category": category,
                "points": default_points.get(category, 0),
                "usage_count": 0,
            }
        )
        data[topic] = questions

        try:
            with open(bank_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except Exception as e:
            raise ValueError(f"Не вдалось зберегти банк: {e}")

        return True

    def _validate_generation_inputs(self):
        if not self.selected_subject:
            raise ValueError("Оберіть предмет.")
        if not self.selected_topics:
            raise ValueError("Оберіть хоча б одну тему.")
        if self.ticket_count <= 0:
            raise ValueError("Кількість білетів має бути більшою за 0.")
        if sum(self.recipe.values()) <= 0:
            raise ValueError("У білеті має бути хоча б одне питання.")

    def on_generate_click(self):
        self._validate_generation_inputs()
        self.last_generation_seed = make_seed()
        self.generated_data = self.engine.generate_exam(
            self.selected_subject,
            self.selected_topics,
            self.recipe,
            self.ticket_count,
            self.total_points,
            seed=self.last_generation_seed,
        )
        entry = build_history_entry(
            subject=self.selected_subject,
            topics=self.selected_topics,
            recipe=self.recipe,
            tickets_count=self.ticket_count,
            total_points=self.total_points,
            bank_fingerprint=calculate_bank_fingerprint(
                self.engine.data_path,
                self.selected_subject,
            ),
            seed=self.last_generation_seed,
        )
        self.last_history_entry = append_history_entry(self.engine.data_path, entry)
        return self.generated_data

    def on_regenerate_from_entry(self, entry):
        self.selected_subject = entry["subject"]
        self.selected_topics = list(entry.get("topics", []))
        self.recipe = dict(entry.get("recipe", {}))
        self.ticket_count = entry.get("tickets_count", 0)
        self.total_points = entry.get("total_points", 100)
        self._validate_generation_inputs()

        current_fingerprint = calculate_bank_fingerprint(
            self.engine.data_path,
            self.selected_subject,
        )
        saved_fingerprint = entry.get("bank_fingerprint")
        bank_changed = bool(saved_fingerprint and saved_fingerprint != current_fingerprint)

        self.last_generation_seed = entry.get("seed")
        if not self.last_generation_seed:
            raise ValueError("У записі історії немає seed для відтворення.")

        self.generated_data = self.engine.generate_exam(
            self.selected_subject,
            self.selected_topics,
            self.recipe,
            self.ticket_count,
            self.total_points,
            seed=self.last_generation_seed,
        )
        self.last_history_entry = entry
        return self.generated_data, bank_changed
    def on_save_pdf(self, ticket_header_text=None):
        if  not self.generated_data:
            messagebox.showerror("Помилка", "Немає данних для збереження")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"{self.selected_subject}_report.pdf",
            filetypes=[("PDF files", "*.pdf"), ("All Files", "*.*")],
            title="Оберіть куди зберігати екземенаційні білети"
        )
        if file_path:
            try:
                save_report_pdf(self.generated_data, file_path, ticket_header_text=ticket_header_text)
                messagebox.showinfo('Успіх', f"Файл успішно збережено :\n{os.path.basename(file_path)}")
                return os.path.abspath(file_path)
            except Exception as e:
                messagebox.showerror("Помилка зббереження", f"Не вдалося зберегти файл {e}")
        return None
