import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import Question, Ticket
def main():
    print (f"ExamAnalyzer")
    q1=Question("Що таке ....", 0.7, "theory")
    q2=Question("написати клас", 0.8, "problem")
    t1=Ticket(id=1 , questions=[q1, q2])
    print(f"Складність білета №{t1.id}: {t1.calculate_score():.2f}")
if __name__ == "__main__":
   main()