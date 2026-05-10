from engine import ExamEngine
from file_manager import save_report_pdf

class ExamApp:
    def __init__(self):
        self.engine = ExamEngine()
        self.selected_subject=None
        self.selected_topics=[]
        self.recipe={"Easy": 0, "Medium": 0, "Hard": 0}
        self.ticket_count=0
        self.generated_data=None
    def on_subject_select(self, subject_id):
        self.selected_subject = subject_id
        topics=self.engine.get_topics_list(subject_id)
        return topics
    def on_generate_click(self):
        self.generated_data=self.engine.generate_exam(
            self.selected_subject,
            self.selected_topics,
            self.recipe,
            self.ticket_count
        )
        return self.generated_data
    def on_save_pdf(self):
        if self.generated_data:
            save_report_pdf(self.generated_data, self.selected_subject)
