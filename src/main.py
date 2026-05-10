from engine import ExamEngine
from file_manager import save_report_pdf
import os
from tkinter import filedialog, messagebox

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
        self.selected_topics = []
        topics=self.engine.get_topics_list(subject_id)
        return topics
    def on_generate_click(self):
         if not self.selected_subject or not self.selected_topics:
            messagebox.showwarning("Error", "Оберіть теми та предмет")
            return None



         self.generated_data=self.engine.generate_exam(
            self.selected_subject,
            self.selected_topics,
            self.recipe,
            self.ticket_count
        )
         return self.generated_data
    def on_save_pdf(self):
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
                save_report_pdf(self.generated_data, file_path)
                messagebox.showinfo('Успіх', f"Файл успішно збережено :\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Помилка зббереження", f"Не вдалося зберегти файл {e}")

