# ExamAnalyzer - візуальна частина
# Робить Андрій

import customtkinter as ctk
import sys
import os
import subprocess
import json

# додаю шлях до src/ щоб знайти main.py, engine.py і file_manager.py
# тому що app.py лежить у src/ui/, а бекенд у src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import ExamApp

# кольори
COLOR_PRIMARY = "#185FA5"
COLOR_PRIMARY_DARK = "#042C53"
COLOR_PRIMARY_LIGHT = "#E6F1FB"
COLOR_PRIMARY_HOVER = "#0C447C"
COLOR_TEXT = "#042C53"
COLOR_TEXT_MUTED = "#5F5E5A"
COLOR_BORDER = "#D3D1C7"
COLOR_BORDER_LIGHT = "#B5D4F4"
COLOR_DISABLED_BG = "#F1EFE8"
COLOR_DISABLED_TEXT = "#888780"
# COLOR_RED = "#FF0000"  # було яскравий червоний, замінив на нормальний
COLOR_RED = "#E24B4A"
COLOR_RED_HOVER = "#A32D2D"
COLOR_WHITE = "#FFFFFF"
# шрифти
FONT_TITLE = ("Arial", 20, "bold")
FONT_SUBTITLE = ("Arial", 12)
FONT_LABEL = ("Arial", 11, "bold")
FONT_BUTTON = ("Arial", 13, "bold")
FONT_SMALL = ("Arial", 10)

# розмір вікна
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 520

BUTTON_WIDTH = 320
BUTTON_HEIGHT = 44


class ExamAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # налаштування вікна
        self.title("ExamAnalyzer")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_WHITE)

        # створюю інстанс бекенду один раз при старті
        # він буде зберігати все що ввів юзер і робити генерацію
        self.backend = ExamApp()

        # тут зберігаю що ввів юзер
        self.mode = None  # "generate" або "view"
        self.selected_subject = None
        self.selected_topics = []

        # розкладка білета по складності (типові пропорції 60/30/10)
        # юзер їх змінює на Е5
        self.easy_count = 3      # легких (2 бали кожне)
        self.medium_count = 2    # середніх (3 бали)
        self.hard_count = 1      # важких (5 балів)

        # кількість білетів (юзер вибирає на Е6)
        self.tickets_count = 30

        # загальна кількість балів за один білет
        self.total_points = 100
        self.last_saved_path = None
        self.preview_ticket_index = 0
        self.replacement_topic_scope = "same"
        self.replacement_difficulty_scope = "similar"
        self.replacement_search_query = ""
        self.history_entries = []
        self.selected_history_index = 0

        # головний контейнер
        self.container = ctk.CTkFrame(self, fg_color=COLOR_WHITE)
        self.container.pack(fill="both", expand=True)

        # запускаюся з 1 екрану
        self.show_screen_1_main_menu()

    def clear_container(self):
        # очищаю екран перед тим як показати новий
        for widget in self.container.winfo_children():
            widget.destroy()

# ====== ЕКРАН 1: Головне меню ======
    def show_screen_1_main_menu(self):
        self.clear_container()
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # версія в правому верхньому кутку
        version_label = ctk.CTkLabel(
            self.container,
            text="v0.1",
            font=("Arial", 10),
            text_color=COLOR_DISABLED_TEXT
        )
        version_label.place(relx=0.97, rely=0.03, anchor="ne")

        # центральний блок з усім вмістом
        center = ctk.CTkFrame(self.container, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # фрейм для логотипа з іконкою позаду
        logo_frame = ctk.CTkFrame(center, fg_color="transparent", width=300, height=60)
        logo_frame.pack(pady=(0, 6))
        logo_frame.pack_propagate(False)

        # іконка-водяний знак позаду (велика, бліда)
        icon_bg = ctk.CTkLabel(
            logo_frame,
            text="📊",
            font=("Arial", 56),
            text_color=COLOR_PRIMARY_LIGHT
        )
        icon_bg.place(relx=0.5, rely=0.5, anchor="center")

        # сама назва зверху іконки
        ctk.CTkLabel(
            logo_frame,
            text="ExamAnalyzer",
            font=("Arial", 24, "bold"),
            text_color="#042C53",
            fg_color="transparent"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # підпис
        ctk.CTkLabel(
            center,
            text="ЩО ВИ ХОЧЕТЕ ЗРОБИТИ?",
            font=FONT_SMALL,
            text_color=COLOR_DISABLED_TEXT
        ).pack(pady=(0, 24))

        # кнопка згенерувати білет
        btn_generate = ctk.CTkButton(
            center,
            text="Згенерувати білет  →",
            font=FONT_BUTTON,
            fg_color="#185FA5",
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="white",
            corner_radius=8,
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            command=self.on_generate_clicked
        )
        btn_generate.pack(pady=6)

        # кнопка переглянути банк
        btn_bank = ctk.CTkButton(
            center,
            text="Переглянути банк питань  →",
            font=FONT_BUTTON,
            fg_color=COLOR_WHITE,
            hover_color=COLOR_PRIMARY_LIGHT,
            text_color=COLOR_PRIMARY,
            border_color=COLOR_PRIMARY,
            border_width=2,
            corner_radius=8,
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            command=self.on_view_bank_clicked
        )
        btn_bank.pack(pady=6)

        ctk.CTkButton(
            center,
            text="Історія генерацій  →",
            font=FONT_BUTTON,
            fg_color=COLOR_WHITE,
            hover_color=COLOR_PRIMARY_LIGHT,
            text_color=COLOR_PRIMARY,
            border_color=COLOR_PRIMARY,
            border_width=2,
            corner_radius=8,
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            command=self.on_history_clicked
        ).pack(pady=6)

        # похилений підпис команди внизу
        signature = ctk.CTkLabel(
            self.container,
            text="Створено командою Базис",
            font=("Arial", 11, "italic"),
            text_color=COLOR_TEXT_MUTED
        )
        signature.place(relx=0.04, rely=0.94, anchor="sw")

        # хрестик "Вихід" в правому нижньому куті - блідіший,
        # щоб не відволікав увагу
        exit_btn = ctk.CTkButton(
            self.container,
            text="✕",
            font=("Arial", 14, "bold"),
            fg_color="#F5C4B3",  # бліший рожево-червоний
            hover_color=COLOR_RED,  # стає яскравим при наведенні
            text_color="#993C1D",  # темно-червоний текст
            corner_radius=6,
            width=26,
            height=26,
            command=self.quit
        )
        exit_btn.place(relx=0.96, rely=0.94, anchor="se")

    def on_generate_clicked(self):
        print("натиснув згенерувати")  # для дебагу
        self.mode = "generate"
        self.show_screen_2_subject()

    def on_view_bank_clicked(self):
        self.mode = "view"
        self.show_screen_2_subject()

    def on_history_clicked(self):
        self.selected_history_index = 0
        self.show_screen_history()

    # ====== ЕКРАН: Історія генерацій ======
    def show_screen_history(self):
        self.clear_container()
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.history_entries = self.backend.get_session_history()
        if self.history_entries and self.selected_history_index >= len(self.history_entries):
            self.selected_history_index = 0

        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 8))

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="Історія генерацій",
            font=FONT_TITLE,
            text_color=COLOR_PRIMARY_DARK,
            anchor="w"
        ).pack(anchor="w")

        count_text = f"{len(self.history_entries)} записів" if self.history_entries else "Поки порожньо"
        ctk.CTkLabel(
            title_frame,
            text=count_text,
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w")

        content = ctk.CTkFrame(self.container, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=(0, 8))

        if not self.history_entries:
            ctk.CTkLabel(
                content,
                text="Ще немає згенерованих комплектів.\nСпочатку створіть білети через «Згенерувати білет».",
                font=FONT_SUBTITLE,
                text_color=COLOR_TEXT_MUTED,
                justify="center"
            ).pack(expand=True, pady=80)
        else:
            self.history_list_frame = ctk.CTkScrollableFrame(
                content,
                fg_color=COLOR_WHITE,
                border_width=1,
                border_color=COLOR_PRIMARY_LIGHT,
                corner_radius=8,
                width=250,
                height=300,
                scrollbar_button_color=COLOR_PRIMARY,
                scrollbar_button_hover_color=COLOR_PRIMARY_HOVER
            )
            self.history_list_frame.pack(side="left", fill="y", padx=(0, 12))

            self.history_detail_frame = ctk.CTkFrame(
                content,
                fg_color=COLOR_WHITE,
                border_width=1,
                border_color=COLOR_PRIMARY_LIGHT,
                corner_radius=8
            )
            self.history_detail_frame.pack(side="left", fill="both", expand=True)

            self.draw_history_list()
            self.draw_history_detail()

        ctk.CTkButton(
            self.container,
            text="← На головну",
            font=FONT_SUBTITLE,
            fg_color=COLOR_WHITE,
            hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_TEXT_MUTED,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=6,
            width=130,
            height=32,
            command=self.show_screen_1_main_menu
        ).place(relx=0.04, rely=0.92, anchor="sw")

    def draw_history_list(self):
        for widget in self.history_list_frame.winfo_children():
            widget.destroy()

        for index, entry in enumerate(self.history_entries):
            is_active = index == self.selected_history_index
            subject_name = self.get_subject_display_name(entry.get("subject"))
            topics_count = len(entry.get("topics", []))
            btn = ctk.CTkButton(
                self.history_list_frame,
                text=(
                    f"{entry.get('created_at', '—')}\n"
                    f"{subject_name} · {entry.get('tickets_count', 0)} біл."
                    f"\n{topics_count} тем"
                ),
                font=FONT_SMALL,
                fg_color=COLOR_PRIMARY_LIGHT if is_active else COLOR_WHITE,
                hover_color=COLOR_PRIMARY_LIGHT,
                text_color=COLOR_PRIMARY_DARK if is_active else COLOR_TEXT_MUTED,
                border_color=COLOR_PRIMARY if is_active else COLOR_BORDER_LIGHT,
                border_width=2 if is_active else 1,
                corner_radius=6,
                width=210,
                height=64,
                command=lambda i=index: self.select_history_entry(i)
            )
            btn.pack(fill="x", padx=6, pady=4)

    def select_history_entry(self, index):
        self.selected_history_index = index
        self.draw_history_list()
        self.draw_history_detail()

    def get_current_history_entry(self):
        if not self.history_entries:
            return None
        return self.history_entries[self.selected_history_index]

    def format_recipe_text(self, recipe):
        easy = recipe.get("Easy", 0)
        medium = recipe.get("Medium", 0)
        hard = recipe.get("Hard", 0)
        return f"{easy} легких + {medium} середніх + {hard} важких"

    def is_bank_changed(self, entry):
        from history import calculate_bank_fingerprint

        saved = entry.get("bank_fingerprint")
        if not saved:
            return False

        current = calculate_bank_fingerprint(
            self.backend.engine.data_path,
            entry.get("subject", "")
        )
        return saved != current

    def draw_history_detail(self):
        for widget in self.history_detail_frame.winfo_children():
            widget.destroy()

        entry = self.get_current_history_entry()
        if not entry:
            return

        inner = ctk.CTkFrame(self.history_detail_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=14)

        ctk.CTkLabel(
            inner,
            text=entry.get("created_at", "—"),
            font=FONT_TITLE,
            text_color=COLOR_PRIMARY_DARK,
            anchor="w"
        ).pack(anchor="w", pady=(0, 10))

        topics_text = ", ".join(entry.get("topics", [])) or "—"
        recipe = entry.get("recipe", {})
        questions_total = sum(recipe.values())

        detail_rows = [
            ("Предмет", self.get_subject_display_name(entry.get("subject"))),
            ("Теми", topics_text),
            ("Розкладка", self.format_recipe_text(recipe)),
            ("Питань у білеті", str(questions_total)),
            ("Балів за білет", str(entry.get("total_points", "—"))),
            ("Білетів", str(entry.get("tickets_count", "—"))),
            ("Seed", entry.get("seed", "—")),
        ]

        for label, value in detail_rows:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(
                row,
                text=label,
                font=FONT_SMALL,
                text_color=COLOR_PRIMARY,
                width=110,
                anchor="w"
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=value,
                font=FONT_SUBTITLE,
                text_color=COLOR_PRIMARY_DARK,
                anchor="w",
                wraplength=380,
                justify="left"
            ).pack(side="left", fill="x", expand=True)

        if self.is_bank_changed(entry):
            ctk.CTkLabel(
                inner,
                text="Банк питань змінився після цієї генерації — комплект може відрізнятися.",
                font=FONT_SMALL,
                text_color=COLOR_RED,
                wraplength=400,
                justify="left"
            ).pack(anchor="w", pady=(10, 0))

        ctk.CTkButton(
            inner,
            text="Відтворити комплект  →",
            font=FONT_BUTTON,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color=COLOR_WHITE,
            corner_radius=8,
            width=240,
            height=40,
            command=self.replay_selected_history_entry
        ).pack(anchor="w", pady=(16, 0))

    def apply_history_entry_to_ui(self, entry):
        self.selected_subject = entry.get("subject")
        self.selected_topics = list(entry.get("topics", []))
        recipe = entry.get("recipe", {})
        self.easy_count = recipe.get("Easy", 0)
        self.medium_count = recipe.get("Medium", 0)
        self.hard_count = recipe.get("Hard", 0)
        self.tickets_count = entry.get("tickets_count", 30)
        self.total_points = entry.get("total_points", 100)

        self.backend.selected_subject = self.selected_subject
        self.backend.selected_topics = self.selected_topics
        self.backend.recipe = dict(recipe)
        self.backend.ticket_count = self.tickets_count
        self.backend.total_points = self.total_points

    def replay_selected_history_entry(self):
        entry = self.get_current_history_entry()
        if not entry:
            return

        try:
            tickets, bank_changed = self.backend.on_regenerate_from_entry(entry)
            if not tickets:
                self.show_generation_error("Не вдалось відтворити комплект")
                return

            self.apply_history_entry_to_ui(entry)
            self.generated_tickets = tickets
            self.last_saved_path = None

            if bank_changed:
                self.show_history_replay_warning()

            self.geometry(f"{WINDOW_WIDTH}x{620}")
            self.show_screen_8_done()

        except Exception as e:
            print(f"Помилка відтворення: {e}")
            self.show_generation_error(str(e))

    def show_history_replay_warning(self):
        warning = ctk.CTkFrame(
            self.container,
            fg_color=COLOR_WHITE,
            border_color=COLOR_PRIMARY,
            border_width=2,
            corner_radius=10,
            width=420,
            height=110
        )
        warning.place(relx=0.5, rely=0.08, anchor="n")

        ctk.CTkLabel(
            warning,
            text="Банк питань змінився — комплект може відрізнятися від оригіналу.",
            font=FONT_SMALL,
            text_color=COLOR_PRIMARY_DARK,
            wraplength=380
        ).pack(pady=(14, 10), padx=12)

        ctk.CTkButton(
            warning,
            text="OK",
            font=FONT_SMALL,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color=COLOR_WHITE,
            corner_radius=6,
            width=80,
            height=26,
            command=warning.destroy
        ).pack(pady=(0, 10))

    # ====== ЕКРАН 2: Вибір предмета ======
    def show_screen_2_subject(self):
        self.clear_container()

        # прогрес тільки коли генерую
        if self.mode == "generate":
            self.draw_progress_bar(step=1, total=5)

        center = ctk.CTkFrame(self.container, fg_color="transparent")
        center.place(relx=0.5, rely=0.45, anchor="center")

        # заголовок
        ctk.CTkLabel(
            center, text="Виберіть предмет",
            font=FONT_TITLE, text_color=COLOR_PRIMARY_DARK
        ).pack(pady=(0, 4))

        # підзаголовок
        ctk.CTkLabel(
            center, text="З нього будуть братись питання",
            font=FONT_SUBTITLE, text_color=COLOR_TEXT_MUTED
        ).pack(pady=(0, 24))

        cards_frame = ctk.CTkFrame(center, fg_color="transparent")
        cards_frame.pack()

        # картка "Мат. аналіз"
        # subject_id="math_analysis" - саме так називається файл math_analysis.json
        math_card = ctk.CTkButton(
            cards_frame,
            text="Мат. аналіз\n6 тем",
            font=FONT_BUTTON,
            fg_color=COLOR_PRIMARY_LIGHT,
            hover_color="#D5E8F8",
            text_color=COLOR_PRIMARY_DARK,
            border_color=COLOR_PRIMARY,
            border_width=2,
            corner_radius=10,
            width=170,
            height=85,
            command=lambda: self.on_subject_selected("math_analysis")
        )
        math_card.pack(side="left", padx=8)

        # картка "Фізика" - тепер працює
        # subject_id="physics" - файл physics.json
        physics_card = ctk.CTkButton(
            cards_frame,
            text="Фізика\n5 тем",
            font=FONT_BUTTON,
            fg_color=COLOR_PRIMARY_LIGHT,
            hover_color="#D5E8F8",
            text_color=COLOR_PRIMARY_DARK,
            border_color=COLOR_PRIMARY,
            border_width=2,
            corner_radius=10,
            width=170,
            height=85,
            command=lambda: self.on_subject_selected("physics")
        )
        physics_card.pack(side="left", padx=8)

        # кнопка назад
        self.draw_back_button(self.show_screen_1_main_menu)

    def on_subject_selected(self, subject):
        self.selected_subject = subject
        # якщо переглядаю банк - йду на банк
        # якщо генерую - йду на вибір тем
        if self.mode == "view":
            self.show_screen_3_bank()
        else:
            self.show_screen_4_topics()

# ====== ЕКРАН 3: Банк питань ======
    def show_screen_3_bank(self):
        self.clear_container()

        # завантажую питання з реального банку через бекенд
        # бекенд читає JSON і повертає словник {тема: [питання]}
        # розгортаю його в плоский список кортежів для відображення
        self.all_questions = self.load_questions_from_backend()

        # шапка зверху
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 8))

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame, text="Банк питань",
            font=FONT_TITLE, text_color=COLOR_PRIMARY_DARK, anchor="w"
        ).pack(anchor="w")

        # формую підзаголовок з реальною кількістю питань і назвою предмета
        subtitle = f"{len(self.all_questions)} питань · {self.get_subject_display_name()}"
        ctk.CTkLabel(
            title_frame, text=subtitle,
            font=FONT_SUBTITLE, text_color=COLOR_TEXT_MUTED, anchor="w"
        ).pack(anchor="w")

        # робоче поле пошуку
        self.search_entry = ctk.CTkEntry(
            header,
            placeholder_text="🔍 пошук теми",
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT,
            fg_color=COLOR_WHITE,
            border_color=COLOR_PRIMARY_LIGHT,
            border_width=1,
            corner_radius=6,
            width=180,
            height=32
        )
        self.search_entry.pack(side="right", padx=4)
        # коли юзер відпускає клавішу - запускається фільтр
        self.search_entry.bind("<KeyRelease>", self.filter_questions)

        # скрол з питаннями
        self.scroll = ctk.CTkScrollableFrame(
            self.container,
            fg_color=COLOR_WHITE,
            border_width=1,
            border_color=COLOR_PRIMARY_LIGHT,
            corner_radius=8,
            width=720,
            height=300,
            scrollbar_button_color=COLOR_PRIMARY,
            scrollbar_button_hover_color=COLOR_PRIMARY_HOVER
        )
        self.scroll.pack(padx=30, pady=4)

        # малюю всі питання спочатку
        self.draw_questions(self.all_questions)

        # кнопка на головну
        ctk.CTkButton(
            self.container, text="← На головну",
            font=FONT_SUBTITLE, fg_color=COLOR_WHITE, hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_TEXT_MUTED, border_color=COLOR_BORDER, border_width=1,
            corner_radius=6, width=130, height=32,
            command=self.show_screen_1_main_menu
        ).pack(pady=4)

    def load_questions_from_backend(self):
        # читаю JSON-файл предмета напряму
        # бо engine.get_topics_list повертає тільки список тем,
        # а нам тут потрібні самі питання
        import json

        # формую шлях до файлу банку (наприклад data/math_analysis.json)
        # __file__ це src/ui/app.py, треба піднятись на 2 рівні до src,
        # потім ще на 1 до проекту, і зайти в data
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "..", "..", "data", f"{self.selected_subject}.json")

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Помилка читання банку: {e}")
            return []

        # розгортаю всі питання з усіх тем у плоский список
        # формат який очікує draw_questions: (назва, тип, складність)
        questions_list = []
        for topic, questions in data.items():
            for q in questions:
                title = q.get("title", "—")
                category = q.get("category", "—")
                short_category = self.short_category(category)
                questions_list.append((title, short_category, category))

        return questions_list

    def short_category(self, category):
        # переводжу англійську категорію в коротку українську для таблиці
        if category == "Easy":
            return "легке"
        elif category == "Medium":
            return "середнє"
        elif category == "Hard":
            return "важке"
        return "—"

    def draw_questions(self, questions):
        # очищаю скрол перед перемалюванням
        for widget in self.scroll.winfo_children():
            widget.destroy()

        # шапка таблиці
        header_row = ctk.CTkFrame(self.scroll, fg_color=COLOR_PRIMARY_LIGHT, corner_radius=4)
        header_row.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(header_row, text="Питання", font=FONT_LABEL,
                     text_color=COLOR_PRIMARY, width=400, anchor="w").pack(side="left", padx=12, pady=6)
        ctk.CTkLabel(header_row, text="Тип", font=FONT_LABEL,
                     text_color=COLOR_PRIMARY, width=100, anchor="w").pack(side="left")
        ctk.CTkLabel(header_row, text="Скл.", font=FONT_LABEL,
                     text_color=COLOR_PRIMARY, width=60, anchor="e").pack(side="left", padx=8)

        # якщо нічого не знайдено - показую повідомлення
        if len(questions) == 0:
            ctk.CTkLabel(
                self.scroll, text="Нічого не знайдено",
                font=FONT_SUBTITLE, text_color=COLOR_TEXT_MUTED
            ).pack(pady=40)
            return

        # малюю кожне питання як рядок
        # ОПТИМІЗАЦІЯ: малюю максимум 100 рядків за раз
        # бо CustomTkinter дуже повільно створює віджети, а в банку 500+ питань
        # для пошуку всі питання все одно доступні через filter_questions
        max_to_show = 100
        questions_to_draw = questions[:max_to_show]

        # малюю кожне питання як рядок
        for title, qtype, complexity in questions_to_draw:
            row = ctk.CTkFrame(self.scroll, fg_color="transparent", height=32)
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=title, font=FONT_SUBTITLE,
                         text_color=COLOR_TEXT, width=400, anchor="w").pack(side="left", padx=12)
            ctk.CTkLabel(row, text=qtype, font=FONT_SUBTITLE,
                         text_color=COLOR_TEXT_MUTED, width=100, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=complexity, font=FONT_LABEL,
                         text_color=COLOR_PRIMARY, width=60, anchor="e").pack(side="left", padx=8)

        # якщо питань більше ніж max_to_show - показую повідомлення внизу
        if len(questions) > max_to_show:
            hidden_count = len(questions) - max_to_show
            info_row = ctk.CTkFrame(self.scroll, fg_color=COLOR_PRIMARY_LIGHT, corner_radius=4)
            info_row.pack(fill="x", pady=(8, 4))
            ctk.CTkLabel(
                info_row,
                text=f"Показано {max_to_show} з {len(questions)}. Ще {hidden_count} питань — використайте пошук",
                font=FONT_SUBTITLE,
                text_color=COLOR_PRIMARY_DARK
            ).pack(pady=8)

    def filter_questions(self, event):
        # беру що ввів юзер, переводжу в нижній регістр
        query = self.search_entry.get().lower()

        # фільтрую: залишаю тільки ті де query є в назві
        filtered = []
        for question in self.all_questions:
            title = question[0].lower()
            if query in title:
                filtered.append(question)

        # перемальовую список з відфільтрованими
        self.draw_questions(filtered)

    # ====== ЕКРАН 4: Вибір тем ======
    def show_screen_4_topics(self):
        self.clear_container()
        self.draw_progress_bar(step=2, total=5)

        # отримую список тем з бекенду для обраного предмета
        # backend.on_subject_select повертає список ключів з JSON
        # для math_analysis: ["Інтеграли", "Похідні", "Множини", "Ліміти", "Ряди", "Диф. рівняння"]
        # для physics: ["Механіка", "Термодинаміка", "Оптика", "Електрика", "Квантова фізика"]
        all_topics = self.backend.on_subject_select(self.selected_subject)

        # якщо щось пішло не так - бекенд може повернути порожній список
        # тоді показую повідомлення замість сітки тем
        if len(all_topics) == 0:
            ctk.CTkLabel(
                self.container,
                text="Не вдалось завантажити теми",
                font=FONT_TITLE,
                text_color=COLOR_RED
            ).place(relx=0.5, rely=0.5, anchor="center")
            self.draw_back_button(self.show_screen_2_subject)
            return

        # центральний блок
        center = ctk.CTkFrame(self.container, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # заголовок
        ctk.CTkLabel(
            center, text="Виберіть теми",
            font=FONT_TITLE, text_color=COLOR_PRIMARY_DARK
        ).pack(pady=(0, 4))

        # лічильник вибраних — буде оновлюватись
        # зберігаю в self щоб можна було оновлювати з інших методів
        self.topics_counter = ctk.CTkLabel(
            center,
            text=self.get_topics_counter_text(len(all_topics)),
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT_MUTED
        )
        self.topics_counter.pack(pady=(0, 18))

        # сітка з темами 2 колонки x 3 рядки
        grid = ctk.CTkFrame(center, fg_color="transparent")
        grid.pack()

        # зберігаю кнопки тем щоб потім перемальовувати
        self.topic_buttons = {}

        for index, topic in enumerate(all_topics):
            row = index // 2  # цілочисельне ділення на 2 = номер рядка
            col = index % 2   # залишок від ділення = номер колонки

            btn = ctk.CTkButton(
                grid,
                text=topic,
                font=FONT_BUTTON,
                # стиль залежить від того чи вже вибрана
                fg_color=self.get_topic_bg(topic),
                hover_color="#D5E8F8",
                text_color=self.get_topic_text(topic),
                border_color=self.get_topic_border(topic),
                border_width=2,
                corner_radius=8,
                width=180,
                height=42,
                command=lambda t=topic: self.toggle_topic(t)
                # lambda t=topic потрібен щоб для кожної кнопки
                # зберігалось саме її значення topic
            )
            btn.grid(row=row, column=col, padx=6, pady=4)

            # запам'ятовую кнопку
            self.topic_buttons[topic] = btn

        # кнопки навігації
        self.draw_nav_buttons_for_topics()

    def get_topics_counter_text(self, total):
        # формую текст для лічильника
        selected = len(self.selected_topics)
        return f"Обрано: {selected} із {total}"

    def get_topic_bg(self, topic):
        # колір фону кнопки в залежності від того чи обрана
        if topic in self.selected_topics:
            return COLOR_PRIMARY_LIGHT  # блакитний фон якщо обрана
        return COLOR_WHITE  # білий якщо не обрана

    def get_topic_text(self, topic):
        # колір тексту
        if topic in self.selected_topics:
            return COLOR_PRIMARY_DARK
        return COLOR_TEXT_MUTED

    def get_topic_border(self, topic):
        # колір рамки
        if topic in self.selected_topics:
            return COLOR_PRIMARY  # синя рамка якщо обрана
        return COLOR_BORDER  # сіра рамка якщо ні

    def toggle_topic(self, topic):
        # додаю або видаляю тему зі списку
        if topic in self.selected_topics:
            self.selected_topics.remove(topic)
        else:
            self.selected_topics.append(topic)

        # перемальовую кнопку цієї теми
        btn = self.topic_buttons[topic]
        btn.configure(
            fg_color=self.get_topic_bg(topic),
            text_color=self.get_topic_text(topic),
            border_color=self.get_topic_border(topic)
        )

        # оновлюю лічильник
        total = len(self.topic_buttons)
        self.topics_counter.configure(text=self.get_topics_counter_text(total))

        # оновлюю стан кнопки "Далі"
        self.update_next_button_state()

    def draw_nav_buttons_for_topics(self):
        # кнопка назад звичайна
        ctk.CTkButton(
            self.container, text="← Назад",
            font=FONT_SUBTITLE, fg_color=COLOR_WHITE, hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_TEXT_MUTED, border_color=COLOR_BORDER, border_width=1,
            corner_radius=6, width=110, height=32,
            command=self.show_screen_2_subject
        ).place(relx=0.04, rely=0.92, anchor="sw")

        # кнопка далі - зберігаю в self щоб можна було вмикати/вимикати
        self.next_button = ctk.CTkButton(
            self.container, text="Далі →",
            font=FONT_BUTTON, fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            text_color=COLOR_WHITE, corner_radius=6, width=110, height=32,
            command=self.show_screen_5_params
        )
        self.next_button.place(relx=0.96, rely=0.92, anchor="se")

        # одразу перевіряю чи треба заблокувати
        self.update_next_button_state()

    def update_next_button_state(self):
        # якщо нічого не вибрано - блокую кнопку
        if len(self.selected_topics) == 0:
            self.next_button.configure(
                state="disabled",
                fg_color=COLOR_DISABLED_BG,
                text_color=COLOR_DISABLED_TEXT
            )
        else:
            self.next_button.configure(
                state="normal",
                fg_color=COLOR_PRIMARY,
                text_color=COLOR_WHITE
            )

# ====== ЕКРАН 5: Структура білета ======
    # юзер обирає скільки легких/середніх/важких питань у білеті
    # бали обчислюються автоматично знизу
    def show_screen_5_params(self):
        self.clear_container()
        self.draw_progress_bar(step=3, total=5)

        center = ctk.CTkFrame(self.container, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # заголовок
        ctk.CTkLabel(
            center, text="Налаштуйте білет",
            font=FONT_TITLE, text_color=COLOR_PRIMARY_DARK
        ).pack(pady=(0, 4))

        # підзаголовок
        ctk.CTkLabel(
            center, text="Створіть структуру одного білета",
            font=FONT_SUBTITLE, text_color=COLOR_TEXT_MUTED
        ).pack(pady=(0, 14))

        # ===== три категорії складності =====
        # роблю однаково для трьох - легкі, середні, важкі
        self.create_difficulty_row(center, "Легких", "easy_count")
        self.create_difficulty_row(center, "Середніх", "medium_count")
        self.create_difficulty_row(center, "Важких", "hard_count")
        self.create_total_points_row(center)

        # ===== підсумок внизу =====
        # розділова лінія
        sep = ctk.CTkFrame(center, fg_color=COLOR_BORDER_LIGHT, height=1)
        sep.pack(fill="x", pady=(8, 6), padx=20)

        # лейбл з підсумком - буде оновлюватись
        self.summary_label = ctk.CTkLabel(
            center,
            text=self.get_summary_text(),
            font=FONT_LABEL,
            text_color=COLOR_PRIMARY_DARK
        )
        self.summary_label.pack(pady=(0, 4))

        # кнопки навігації
        # тут створюю кнопку назад руками (без draw_nav_buttons)
        kn_back = ctk.CTkButton(
            self.container,
            text="← Назад",
            font=FONT_SUBTITLE,
            fg_color=COLOR_WHITE,
            hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_TEXT_MUTED,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=6,
            width=110,
            height=32,
            command=self.show_screen_4_topics
        )
        kn_back.place(relx=0.04, rely=0.92, anchor="sw")

        # кнопка далі
        # перевіряю чи можна йти далі - має бути хоча б 1 питання
        kn_next = ctk.CTkButton(
            self.container,
            text="Далі →",
            font=FONT_BUTTON,
            fg_color="#185FA5",
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="white",
            corner_radius=6,
            width=110,
            height=32,
            command=self.show_screen_6_count
        )
        kn_next.place(relx=0.96, rely=0.92, anchor="se")

        # зберігаю кнопку щоб блокувати її
        self.next_button_e5 = kn_next
        self.update_next_button_e5()

    def create_difficulty_row(self, parent, name, attr_name):
        # створюю один рядок для категорії складності
        # name - "Легких", "Середніх", "Важких"
        # attr_name - "easy_count", "medium_count" чи "hard_count"

        # фрейм для одного рядка
        row = ctk.CTkFrame(parent, fg_color=COLOR_PRIMARY_LIGHT, corner_radius=8)
        row.pack(fill="x", pady=4, padx=20)

        # підпис ліворуч
        ctk.CTkLabel(
            row,
            text=name,
            font=FONT_LABEL,
            text_color=COLOR_PRIMARY_DARK,
            anchor="w"
        ).pack(side="left", padx=14, pady=8)

        # фрейм для кнопок і числа праворуч
        controls = ctk.CTkFrame(row, fg_color="transparent")
        controls.pack(side="right", padx=14, pady=8)

        # кнопка мінус
        ctk.CTkButton(
            controls, text="−",
            font=("Arial", 14, "bold"),
            fg_color=COLOR_WHITE, hover_color=COLOR_PRIMARY_LIGHT,
            text_color=COLOR_PRIMARY,
            border_color=COLOR_PRIMARY, border_width=1,
            corner_radius=6, width=32, height=28,
            command=lambda: self.change_difficulty(attr_name, -1)
        ).pack(side="left", padx=2)

        # лейбл з числом
        # використовую setattr щоб динамічно створити атрибут
        # типу self.easy_count_label, self.medium_count_label, self.hard_count_label
        value_label = ctk.CTkLabel(
            controls,
            text=str(getattr(self, attr_name)),
            font=("Arial", 14, "bold"),
            text_color=COLOR_PRIMARY_DARK,
            width=32
        )
        value_label.pack(side="left", padx=4)
        # запам'ятовую цей лейбл
        setattr(self, f"{attr_name}_label", value_label)

        # кнопка плюс
        ctk.CTkButton(
            controls, text="+",
            font=("Arial", 14, "bold"),
            fg_color=COLOR_WHITE, hover_color=COLOR_PRIMARY_LIGHT,
            text_color=COLOR_PRIMARY,
            border_color=COLOR_PRIMARY, border_width=1,
            corner_radius=6, width=32, height=28,
            command=lambda: self.change_difficulty(attr_name, 1)
        ).pack(side="left", padx=2)

    def create_total_points_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color=COLOR_WHITE, corner_radius=8)
        row.pack(fill="x", pady=(8, 4), padx=20)

        ctk.CTkLabel(
            row,
            text="Балів за білет",
            font=FONT_LABEL,
            text_color=COLOR_PRIMARY_DARK,
            anchor="w"
        ).pack(side="left", padx=14, pady=8)

        controls = ctk.CTkFrame(row, fg_color="transparent")
        controls.pack(side="right", padx=14, pady=8)

        ctk.CTkButton(
            controls, text="−",
            font=("Arial", 14, "bold"),
            fg_color=COLOR_WHITE, hover_color=COLOR_PRIMARY_LIGHT,
            text_color=COLOR_PRIMARY,
            border_color=COLOR_PRIMARY, border_width=1,
            corner_radius=6, width=32, height=28,
            command=lambda: self.change_total_points(-5)
        ).pack(side="left", padx=2)

        self.total_points_label = ctk.CTkLabel(
            controls,
            text=str(self.total_points),
            font=("Arial", 14, "bold"),
            text_color=COLOR_PRIMARY_DARK,
            width=44
        )
        self.total_points_label.pack(side="left", padx=4)

        ctk.CTkButton(
            controls, text="+",
            font=("Arial", 14, "bold"),
            fg_color=COLOR_WHITE, hover_color=COLOR_PRIMARY_LIGHT,
            text_color=COLOR_PRIMARY,
            border_color=COLOR_PRIMARY, border_width=1,
            corner_radius=6, width=32, height=28,
            command=lambda: self.change_total_points(5)
        ).pack(side="left", padx=2)

    def change_difficulty(self, attr_name, delta):
        # коли натиснули + або - на одній з категорій
        current = getattr(self, attr_name)
        new_value = current + delta

        # обмежую від 0 до 20 (на одну категорію)
        if new_value < 0:
            new_value = 0
        if new_value > 20:
            new_value = 20

        # оновлюю значення
        setattr(self, attr_name, new_value)

        # оновлюю лейбл цієї категорії
        label = getattr(self, f"{attr_name}_label")
        label.configure(text=str(new_value))

        if self.total_points < self.get_total_questions():
            self.total_points = self.get_total_questions()
            if hasattr(self, "total_points_label"):
                self.total_points_label.configure(text=str(self.total_points))

        # оновлюю підсумок внизу
        self.summary_label.configure(text=self.get_summary_text())

        # оновлюю стан кнопки далі
        self.update_next_button_e5()

    def change_total_points(self, delta):
        new_value = self.total_points + delta
        minimum_points = max(1, self.get_total_questions())
        if new_value < minimum_points:
            new_value = minimum_points
        if new_value > 1000:
            new_value = 1000

        self.total_points = new_value
        self.total_points_label.configure(text=str(new_value))
        self.summary_label.configure(text=self.get_summary_text())
        self.update_next_button_e5()

    def get_summary_text(self):
        # формую текст підсумку
        total_q = self.get_total_questions()
        total_p = self.get_total_points()
        return f"Всього: {total_q} питань · {total_p} балів за білет"

    def get_total_questions(self):
        # обчислюю загальну кількість питань
        return self.easy_count + self.medium_count + self.hard_count

    def get_total_points(self):
        # загальна кількість балів задається користувачем,
        # а engine розподіляє її між питаннями за складністю
        return self.total_points

    def update_next_button_e5(self):
        # блокую далі якщо нічого не вибрано
        if self.get_total_questions() == 0 or self.get_total_points() <= 0:
            self.next_button_e5.configure(
                state="disabled",
                fg_color=COLOR_DISABLED_BG,
                text_color=COLOR_DISABLED_TEXT
            )
        else:
            self.next_button_e5.configure(
                state="normal",
                fg_color=COLOR_PRIMARY,
                text_color=COLOR_WHITE
            )

# ====== ЕКРАН 6: Кількість білетів ======
    def show_screen_6_count(self):
        self.clear_container()
        self.draw_progress_bar(step=4, total=5)

        center = ctk.CTkFrame(self.container, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # заголовок
        ctk.CTkLabel(
            center, text="Скільки білетів?",
            font=FONT_TITLE, text_color=COLOR_PRIMARY_DARK
        ).pack(pady=(0, 4))

        # підзаголовок
        ctk.CTkLabel(
            center, text="Усі будуть рівносильні за складністю",
            font=FONT_SUBTITLE, text_color=COLOR_TEXT_MUTED
        ).pack(pady=(0, 24))

        # ===== блок зі слайдером =====
        slider_block = ctk.CTkFrame(center, fg_color="transparent")
        slider_block.pack(pady=(0, 14))

        # рядок: слайдер ліворуч, число праворуч
        slider_row = ctk.CTkFrame(slider_block, fg_color="transparent")
        slider_row.pack()

        # сам слайдер
        self.tickets_slider = ctk.CTkSlider(
            slider_row,
            from_=1,
            to=50,
            number_of_steps=49,
            width=380,
            height=18,
            fg_color=COLOR_BORDER_LIGHT,
            progress_color=COLOR_PRIMARY,
            button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_PRIMARY_HOVER,
            command=self.on_slider_change
        )
        self.tickets_slider.set(self.tickets_count)
        self.tickets_slider.pack(side="left", padx=(0, 12))

        # поле з числом справа від слайдера
        self.tickets_value_label = ctk.CTkLabel(
            slider_row,
            text=str(self.tickets_count),
            font=("Arial", 16, "bold"),
            text_color=COLOR_PRIMARY_DARK,
            fg_color=COLOR_PRIMARY_LIGHT,
            corner_radius=6,
            width=50,
            height=32
        )
        self.tickets_value_label.pack(side="left")

        # підписи "1" і "50" під слайдером
        labels_row = ctk.CTkFrame(slider_block, fg_color="transparent")
        labels_row.pack(fill="x", padx=(0, 65), pady=(4, 0))

        ctk.CTkLabel(
            labels_row, text="1",
            font=FONT_SMALL, text_color=COLOR_DISABLED_TEXT
        ).pack(side="left")

        ctk.CTkLabel(
            labels_row, text="50",
            font=FONT_SMALL, text_color=COLOR_DISABLED_TEXT
        ).pack(side="right")

        # ===== швидкі кнопки 10 / 25 / 30 =====
        quick_buttons_frame = ctk.CTkFrame(center, fg_color="transparent")
        quick_buttons_frame.pack(pady=(20, 0))

        self.quick_buttons = {}

        for value in [10, 25, 30]:
            btn = ctk.CTkButton(
                quick_buttons_frame,
                text=str(value),
                font=FONT_BUTTON,
                fg_color=self.get_quick_btn_bg(value),
                hover_color=COLOR_PRIMARY_LIGHT,
                text_color=self.get_quick_btn_text(value),
                border_color=self.get_quick_btn_border(value),
                border_width=self.get_quick_btn_border_width(value),
                corner_radius=8,
                width=100,
                height=44,
                command=lambda v=value: self.on_quick_button_click(v)
            )
            btn.pack(side="left", padx=4)

            self.quick_buttons[value] = btn

        # кнопки навігації
        self.draw_nav_buttons(self.show_screen_5_params, self.show_screen_7_confirm)

    def on_slider_change(self, value):
        self.tickets_count = int(value)
        self.tickets_value_label.configure(text=str(self.tickets_count))
        self.refresh_quick_buttons()

    def on_quick_button_click(self, value):
        self.tickets_count = value
        self.tickets_slider.set(value)
        self.tickets_value_label.configure(text=str(value))
        self.refresh_quick_buttons()

    def refresh_quick_buttons(self):
        for value, btn in self.quick_buttons.items():
            btn.configure(
                fg_color=self.get_quick_btn_bg(value),
                text_color=self.get_quick_btn_text(value),
                border_color=self.get_quick_btn_border(value),
                border_width=self.get_quick_btn_border_width(value)
            )

    def get_quick_btn_bg(self, value):
        if value == self.tickets_count:
            return COLOR_PRIMARY_LIGHT
        return COLOR_WHITE

    def get_quick_btn_text(self, value):
        if value == self.tickets_count:
            return COLOR_PRIMARY_DARK
        return COLOR_PRIMARY

    def get_quick_btn_border(self, value):
        if value == self.tickets_count:
            return COLOR_PRIMARY
        return COLOR_BORDER_LIGHT

    def get_quick_btn_border_width(self, value):
        if value == self.tickets_count:
            return 2
        return 1

# ====== ЕКРАН 7: Підтвердження ======
    def show_screen_7_confirm(self):
        self.clear_container()
        self.draw_progress_bar(step=5, total=5)

        center = ctk.CTkFrame(self.container, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # заголовок
        ctk.CTkLabel(
            center, text="Готові згенерувати?",
            font=FONT_TITLE, text_color=COLOR_PRIMARY_DARK
        ).pack(pady=(0, 4))

        # підзаголовок
        ctk.CTkLabel(
            center, text="Перевірте налаштування",
            font=FONT_SUBTITLE, text_color=COLOR_TEXT_MUTED
        ).pack(pady=(0, 16))

        # ===== картка зі зведенням =====
        summary_card = ctk.CTkFrame(
            center,
            fg_color=COLOR_PRIMARY_LIGHT,
            corner_radius=10,
            width=400
        )
        summary_card.pack(pady=(0, 16))

        subject_name = self.get_subject_display_name()

        if len(self.selected_topics) == 0:
            topics_text = "—"
        else:
            topics_text = ", ".join(self.selected_topics)

        # формую розкладку для виводу
        breakdown = f"{self.easy_count} легких + {self.medium_count} середніх + {self.hard_count} важких"
        totals = f"{self.get_total_questions()} питань · {self.get_total_points()} балів"

        # пари (поле, значення) для виводу
        summary_data = [
            ("Предмет", subject_name),
            ("Теми", topics_text),
            ("Розкладка", breakdown),
            ("Всього", totals),
            ("Білетів", str(self.tickets_count)),
        ]

        # малюю кожну пару як рядок
        for index, (label, value) in enumerate(summary_data):
            # для довгих рядків (Теми, Розкладка) роблю вертикальний layout
            if label in ("Теми", "Розкладка"):
                row = ctk.CTkFrame(summary_card, fg_color="transparent")
                row.pack(fill="x", padx=14, pady=4)

                ctk.CTkLabel(
                    row, text=label,
                    font=FONT_SUBTITLE, text_color=COLOR_PRIMARY,
                    anchor="w"
                ).pack(anchor="w")

                ctk.CTkLabel(
                    row, text=value,
                    font=("Arial", 12, "bold"), text_color=COLOR_PRIMARY_DARK,
                    anchor="w",
                    wraplength=370,
                    justify="left"
                ).pack(anchor="w", pady=(2, 0))
            else:
                row = ctk.CTkFrame(summary_card, fg_color="transparent")
                row.pack(fill="x", padx=14, pady=4)

                ctk.CTkLabel(
                    row, text=label,
                    font=FONT_SUBTITLE, text_color=COLOR_PRIMARY,
                    anchor="w"
                ).pack(side="left")

                ctk.CTkLabel(
                    row, text=value,
                    font=("Arial", 12, "bold"), text_color=COLOR_PRIMARY_DARK,
                    anchor="e"
                ).pack(side="right")

            if index < len(summary_data) - 1:
                separator = ctk.CTkFrame(
                    summary_card,
                    fg_color=COLOR_BORDER_LIGHT,
                    height=1
                )
                separator.pack(fill="x", padx=14)

        # головна кнопка генерації
        # тепер замість прямого переходу на Е8 - спочатку викликаю бекенд
        ctk.CTkButton(
            center, text="Згенерувати білети  →",
            font=FONT_BUTTON,
            fg_color="#185FA5",
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="white",
            corner_radius=10,
            width=BUTTON_WIDTH,
            height=BUTTON_HEIGHT,
            command=self.generate_tickets_and_continue
        ).pack(pady=(8, 0))

        # кнопка назад внизу
        ctk.CTkButton(
            self.container, text="← Назад",
            font=FONT_SUBTITLE, fg_color=COLOR_WHITE, hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_TEXT_MUTED, border_color=COLOR_BORDER, border_width=1,
            corner_radius=6, width=110, height=32,
            command=self.show_screen_6_count
        ).place(relx=0.04, rely=0.92, anchor="sw")

    def generate_tickets_and_continue(self):
        # передаю всі налаштування юзера в бекенд
        # бекенд (ExamApp) очікує саме ці поля - дивись main.py
        self.backend.selected_topics = self.selected_topics
        self.backend.recipe = {
            "Easy": self.easy_count,
            "Medium": self.medium_count,
            "Hard": self.hard_count
        }
        self.backend.ticket_count = self.tickets_count
        self.backend.total_points = self.total_points

        # викликаю генерацію
        # бекенд внутрішньо викликає engine.generate_exam(...)
        # і повертає список згенерованих білетів
        try:
            tickets = self.backend.on_generate_click()

            if tickets is None or len(tickets) == 0:
                # якщо бекенд не зміг згенерувати - показую помилку
                self.show_generation_error("Не вдалось згенерувати білети")
                return

            # генерація пройшла успішно - переходжу на екран успіху
            self.generated_tickets = tickets
            self.show_screen_8_done()

        except Exception as e:
            # ловлю будь-які помилки бекенду
            print(f"Помилка генерації: {e}")
            self.show_generation_error(str(e))

    def show_generation_error(self, message):
        # просте діалогове вікно з помилкою
        # використовую CTkFrame поверх контейнера
        error_overlay = ctk.CTkFrame(
            self.container,
            fg_color=COLOR_WHITE,
            border_color=COLOR_RED,
            border_width=2,
            corner_radius=10,
            width=500,
            height=180
        )
        error_overlay.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            error_overlay, text="⚠️ " + message,
            font=FONT_BUTTON, text_color=COLOR_RED,
            wraplength=450,
            justify="left"
        ).pack(pady=(20, 10), padx=18)

        ctk.CTkButton(
            error_overlay, text="OK",
            font=FONT_SUBTITLE,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            text_color="white",
            corner_radius=6, width=100, height=30,
            command=error_overlay.destroy
        ).pack()

    def get_subject_display_name(self, subject_id=None):
        subject = subject_id if subject_id is not None else self.selected_subject
        if subject == "math_analysis":
            return "Мат. аналіз"
        if subject == "physics":
            return "Фізика"
        if subject:
            return subject.replace("_", " ").capitalize()
        return "—"

# ====== ЕКРАН 8: Готово ======
    def show_screen_8_done(self):
        self.clear_container()
        if self.winfo_height() < 600:
            self.geometry(f"{WINDOW_WIDTH}x{620}")

        self.last_saved_file = f"{self.selected_subject}_report.pdf"
        self.last_saved_path = None
        self.preview_ticket_index = 0

        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(18, 8))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box, text="Передпогляд білетів",
            font=FONT_TITLE, text_color=COLOR_PRIMARY_DARK, anchor="w"
        ).pack(anchor="w")

        subtitle = f"{self.get_subject_display_name()} · {len(self.generated_tickets)} білетів · {self.total_points} балів"
        ctk.CTkLabel(
            title_box, text=subtitle,
            font=FONT_SUBTITLE, text_color=COLOR_TEXT_MUTED, anchor="w"
        ).pack(anchor="w")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")

        ctk.CTkButton(
            actions, text="Зберегти PDF",
            font=FONT_BUTTON, fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            text_color=COLOR_WHITE, corner_radius=6,
            width=140, height=34,
            command=self.on_save_clicked
        ).pack(side="left", padx=4)

        self.open_pdf_button = ctk.CTkButton(
            actions, text="Відкрити PDF",
            font=FONT_BUTTON, fg_color=COLOR_DISABLED_BG, hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_DISABLED_TEXT, corner_radius=6,
            width=130, height=34,
            state="disabled",
            command=self.open_saved_pdf
        )
        self.open_pdf_button.pack(side="left", padx=4)

        ctk.CTkButton(
            actions, text="На головну",
            font=FONT_SUBTITLE, fg_color=COLOR_WHITE, hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_TEXT_MUTED, border_color=COLOR_BORDER, border_width=1,
            corner_radius=6, width=110, height=34,
            command=self.reset_and_go_home
        ).pack(side="left", padx=4)

        content = ctk.CTkFrame(self.container, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        self.ticket_list_frame = ctk.CTkScrollableFrame(
            content,
            fg_color=COLOR_WHITE,
            border_width=1,
            border_color=COLOR_PRIMARY_LIGHT,
            corner_radius=8,
            width=185,
            height=360
        )
        self.ticket_list_frame.pack(side="left", fill="y", padx=(0, 12))

        self.ticket_preview_frame = ctk.CTkFrame(
            content,
            fg_color=COLOR_WHITE,
            border_width=1,
            border_color=COLOR_PRIMARY_LIGHT,
            corner_radius=8
        )
        self.ticket_preview_frame.pack(side="left", fill="both", expand=True)

        self.draw_ticket_list()
        self.draw_ticket_preview()

    def draw_ticket_list(self):
        for widget in self.ticket_list_frame.winfo_children():
            widget.destroy()

        for index, ticket in enumerate(self.generated_tickets):
            is_active = index == self.preview_ticket_index
            btn = ctk.CTkButton(
                self.ticket_list_frame,
                text=f"Білет №{ticket.get('number', index + 1)}\n{ticket.get('total_points', 0)} б. · скл. {ticket.get('difficulty_score', 0)}",
                font=FONT_SUBTITLE,
                fg_color=COLOR_PRIMARY_LIGHT if is_active else COLOR_WHITE,
                hover_color=COLOR_PRIMARY_LIGHT,
                text_color=COLOR_PRIMARY_DARK if is_active else COLOR_TEXT_MUTED,
                border_color=COLOR_PRIMARY if is_active else COLOR_BORDER_LIGHT,
                border_width=2 if is_active else 1,
                corner_radius=6,
                width=150,
                height=54,
                command=lambda i=index: self.select_preview_ticket(i)
            )
            btn.pack(fill="x", padx=6, pady=4)

    def select_preview_ticket(self, index):
        self.preview_ticket_index = index
        self.draw_ticket_list()
        self.draw_ticket_preview()

    def get_current_preview_ticket(self):
        if not self.generated_tickets:
            return None
        return self.generated_tickets[self.preview_ticket_index]

    def draw_ticket_preview(self):
        for widget in self.ticket_preview_frame.winfo_children():
            widget.destroy()

        ticket = self.get_current_preview_ticket()
        if not ticket:
            return

        header = ctk.CTkFrame(self.ticket_preview_frame, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(14, 8))

        ctk.CTkLabel(
            header,
            text=f"Білет №{ticket.get('number', self.preview_ticket_index + 1)}",
            font=FONT_TITLE,
            text_color=COLOR_PRIMARY_DARK
        ).pack(side="left")

        meta = f"{ticket.get('total_points', 0)} балів · складність {ticket.get('difficulty_score', 0)}"
        ctk.CTkLabel(
            header,
            text=meta,
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT_MUTED
        ).pack(side="right")

        form_row = ctk.CTkFrame(self.ticket_preview_frame, fg_color=COLOR_PRIMARY_LIGHT, corner_radius=6)
        form_row.pack(fill="x", padx=18, pady=(0, 10))
        ctk.CTkLabel(
            form_row,
            text=f"Предмет: {self.get_subject_display_name()}    Студент: ____________________    Група: ______",
            font=FONT_SMALL,
            text_color=COLOR_PRIMARY_DARK
        ).pack(anchor="w", padx=12, pady=8)

        questions_frame = ctk.CTkScrollableFrame(
            self.ticket_preview_frame,
            fg_color=COLOR_WHITE,
            border_width=0,
            width=520,
            height=250
        )
        questions_frame.pack(fill="both", expand=True, padx=18, pady=(0, 10))

        for q_index, question in enumerate(ticket.get("questions", [])):
            row = ctk.CTkFrame(questions_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)

            text_box = ctk.CTkFrame(row, fg_color=COLOR_PRIMARY_LIGHT, corner_radius=6)
            text_box.pack(side="left", fill="x", expand=True, padx=(0, 8))

            q_title = question.get("title", "Питання без назви")
            q_points = question.get("points", 0)
            q_topic = question.get("topic", "—")
            q_category = question.get("category", "—")
            q_complexity = question.get("real_complexity", 0)

            ctk.CTkLabel(
                text_box,
                text=f"{q_index + 1}. {q_title}",
                font=FONT_SUBTITLE,
                text_color=COLOR_TEXT,
                anchor="w",
                wraplength=430,
                justify="left"
            ).pack(anchor="w", padx=10, pady=(7, 1))

            meta = f"{q_topic} · {q_category} · скл. {q_complexity} · {q_points} б."
            if question.get("is_repeat"):
                meta += " · повтор"
            ctk.CTkLabel(
                text_box,
                text=meta,
                font=FONT_SMALL,
                text_color=COLOR_TEXT_MUTED,
                anchor="w"
            ).pack(anchor="w", padx=10, pady=(0, 7))

            ctk.CTkButton(
                row,
                text="Замінити",
                font=FONT_SMALL,
                fg_color=COLOR_WHITE,
                hover_color=COLOR_PRIMARY_LIGHT,
                text_color=COLOR_PRIMARY,
                border_color=COLOR_PRIMARY,
                border_width=1,
                corner_radius=6,
                width=86,
                height=34,
                command=lambda qi=q_index: self.open_replace_dialog(qi)
            ).pack(side="right")

        footer = ctk.CTkFrame(self.ticket_preview_frame, fg_color="transparent")
        footer.pack(fill="x", padx=18, pady=(0, 14))

        prev_state = "normal" if self.preview_ticket_index > 0 else "disabled"
        next_state = "normal" if self.preview_ticket_index < len(self.generated_tickets) - 1 else "disabled"

        ctk.CTkButton(
            footer,
            text="← Попередній",
            font=FONT_SUBTITLE,
            fg_color=COLOR_WHITE,
            hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_TEXT_MUTED,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=6,
            width=120,
            height=30,
            state=prev_state,
            command=lambda: self.select_preview_ticket(self.preview_ticket_index - 1)
        ).pack(side="left")

        ctk.CTkButton(
            footer,
            text="Наступний →",
            font=FONT_SUBTITLE,
            fg_color=COLOR_WHITE,
            hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_TEXT_MUTED,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=6,
            width=120,
            height=30,
            state=next_state,
            command=lambda: self.select_preview_ticket(self.preview_ticket_index + 1)
        ).pack(side="right")


    def open_replace_dialog(self, question_index, reset_filters=True):
        self.replace_question_index = question_index
        if reset_filters:
            self.replacement_topic_scope = "same"
            self.replacement_difficulty_scope = "similar"
            self.replacement_search_query = ""

        self.replace_overlay = ctk.CTkFrame(
            self.container,
            fg_color=COLOR_WHITE,
            border_color=COLOR_PRIMARY,
            border_width=2,
            corner_radius=10,
            width=620,
            height=390
        )
        self.replace_overlay.place(relx=0.5, rely=0.52, anchor="center")
        self.replace_overlay.pack_propagate(False)

        ticket = self.get_current_preview_ticket()
        question = ticket["questions"][question_index]

        header = ctk.CTkFrame(self.replace_overlay, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(14, 6))

        ctk.CTkLabel(
            header,
            text="Замінити питання",
            font=FONT_TITLE,
            text_color=COLOR_PRIMARY_DARK
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="✕",
            font=("Arial", 14, "bold"),
            fg_color=COLOR_WHITE,
            hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_TEXT_MUTED,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=6,
            width=28,
            height=28,
            command=self.replace_overlay.destroy
        ).pack(side="right")

        current_text = (
            f"{question.get('title', 'Питання')}\n"
            f"{question.get('topic', '—')} · {question.get('category', '—')} · "
            f"скл. {question.get('real_complexity', 0)} · {question.get('points', 0)} б."
        )
        ctk.CTkLabel(
            self.replace_overlay,
            text=current_text,
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT,
            fg_color=COLOR_PRIMARY_LIGHT,
            corner_radius=6,
            wraplength=560,
            justify="left"
        ).pack(fill="x", padx=18, pady=(0, 10))

        filters = ctk.CTkFrame(self.replace_overlay, fg_color="transparent")
        filters.pack(fill="x", padx=18, pady=(0, 8))

        topic_box = ctk.CTkFrame(filters, fg_color="transparent")
        topic_box.pack(side="left")
        ctk.CTkLabel(
            topic_box, text="Теми", font=FONT_SMALL, text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w")
        topic_buttons = ctk.CTkFrame(topic_box, fg_color="transparent")
        topic_buttons.pack(anchor="w", pady=(3, 0))
        self.draw_replace_filter_button(topic_buttons, "Та сама", "topic", "same")
        self.draw_replace_filter_button(topic_buttons, "Обрані", "topic", "selected")
        self.draw_replace_filter_button(topic_buttons, "Усі", "topic", "all")

        difficulty_box = ctk.CTkFrame(filters, fg_color="transparent")
        difficulty_box.pack(side="right")
        ctk.CTkLabel(
            difficulty_box, text="Складність", font=FONT_SMALL, text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w")
        difficulty_buttons = ctk.CTkFrame(difficulty_box, fg_color="transparent")
        difficulty_buttons.pack(anchor="w", pady=(3, 0))
        self.draw_replace_filter_button(difficulty_buttons, "Схожа", "difficulty", "similar")
        self.draw_replace_filter_button(difficulty_buttons, "Та сама", "difficulty", "category")
        self.draw_replace_filter_button(difficulty_buttons, "Будь-яка", "difficulty", "any")

        search_row = ctk.CTkFrame(self.replace_overlay, fg_color="transparent")
        search_row.pack(fill="x", padx=18, pady=(0, 8))

        self.replace_search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Пошук питання або теми",
            font=FONT_SUBTITLE,
            text_color=COLOR_TEXT,
            fg_color=COLOR_WHITE,
            border_color=COLOR_PRIMARY_LIGHT,
            border_width=1,
            corner_radius=6,
            height=30
        )
        self.replace_search_entry.pack(side="left", fill="x", expand=True)
        self.replace_search_entry.insert(0, self.replacement_search_query)
        self.replace_search_entry.bind("<KeyRelease>", self.on_replacement_search_change)

        ctk.CTkButton(
            search_row,
            text="Очистити",
            font=FONT_SMALL,
            fg_color=COLOR_WHITE,
            hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_TEXT_MUTED,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=6,
            width=78,
            height=30,
            command=self.clear_replacement_search
        ).pack(side="right", padx=(8, 0))

        self.replace_results_frame = ctk.CTkScrollableFrame(
            self.replace_overlay,
            fg_color=COLOR_WHITE,
            border_width=1,
            border_color=COLOR_PRIMARY_LIGHT,
            corner_radius=8,
            width=570,
            height=195
        )
        self.replace_results_frame.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        self.draw_replacement_candidates()

    def draw_replace_filter_button(self, parent, text, group, value):
        is_active = (
            group == "topic" and self.replacement_topic_scope == value
        ) or (
            group == "difficulty" and self.replacement_difficulty_scope == value
        )

        ctk.CTkButton(
            parent,
            text=text,
            font=FONT_SMALL,
            fg_color=COLOR_PRIMARY_LIGHT if is_active else COLOR_WHITE,
            hover_color=COLOR_PRIMARY_LIGHT,
            text_color=COLOR_PRIMARY_DARK if is_active else COLOR_TEXT_MUTED,
            border_color=COLOR_PRIMARY if is_active else COLOR_BORDER,
            border_width=2 if is_active else 1,
            corner_radius=6,
            width=70,
            height=28,
            command=lambda: self.set_replacement_filter(group, value)
        ).pack(side="left", padx=2)

    def set_replacement_filter(self, group, value):
        if group == "topic":
            self.replacement_topic_scope = value
        else:
            self.replacement_difficulty_scope = value

        self.replace_overlay.destroy()
        self.open_replace_dialog(self.replace_question_index, reset_filters=False)

    def on_replacement_search_change(self, event):
        self.replacement_search_query = self.replace_search_entry.get().strip().lower()
        self.draw_replacement_candidates()

    def clear_replacement_search(self):
        self.replacement_search_query = ""
        self.replace_search_entry.delete(0, "end")
        self.draw_replacement_candidates()

    def get_used_question_titles(self, exclude_title=None):
        used_titles = set()
        for ticket in self.generated_tickets:
            for question in ticket.get("questions", []):
                title = question.get("title")
                if title and title != exclude_title:
                    used_titles.add(title)
        return used_titles

    def load_replacement_questions(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "..", "..", "data", f"{self.selected_subject}.json")

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Помилка читання банку для заміни: {e}")
            return []

        questions = []
        for topic, topic_questions in data.items():
            for question in topic_questions:
                normalized = dict(question)
                normalized["topic"] = topic
                questions.append(normalized)
        return questions

    def get_question_usage_counts(self, exclude_title=None):
        usage_counts = {}
        for ticket in self.generated_tickets:
            for question in ticket.get("questions", []):
                title = question.get("title")
                if not title or title == exclude_title:
                    continue
                usage_counts[title] = usage_counts.get(title, 0) + 1
        return usage_counts

    def collect_replacement_candidates(self, allow_reused=False):
        ticket = self.get_current_preview_ticket()
        current_question = ticket["questions"][self.replace_question_index]
        current_title = current_question.get("title")
        current_topic = current_question.get("topic")
        current_category = current_question.get("category")
        current_complexity = current_question.get("real_complexity", 0)
        used_titles = self.get_used_question_titles(exclude_title=current_title)
        usage_counts = self.get_question_usage_counts(exclude_title=current_title)

        if self.replacement_topic_scope == "same":
            allowed_topics = {current_topic}
        elif self.replacement_topic_scope == "selected":
            allowed_topics = set(self.selected_topics)
        else:
            allowed_topics = None

        candidates = []
        search_query = self.replacement_search_query
        for question in self.load_replacement_questions():
            title = question.get("title")
            if title == current_title:
                continue
            if not allow_reused and title in used_titles:
                continue
            if allowed_topics is not None and question.get("topic") not in allowed_topics:
                continue
            if search_query:
                searchable = f"{question.get('title', '')} {question.get('topic', '')}".lower()
                if search_query not in searchable:
                    continue

            normalized = self.backend.engine.normalize_question(question)
            complexity = normalized.get("real_complexity", 0)
            category = normalized.get("category")

            if self.replacement_difficulty_scope == "similar":
                allowed_delta = max(current_complexity * 0.15, 0.05)
                if category != current_category or abs(complexity - current_complexity) > allowed_delta:
                    continue
            elif self.replacement_difficulty_scope == "category":
                if category != current_category:
                    continue

            normalized["similarity_delta"] = abs(complexity - current_complexity)
            normalized["usage_count"] = usage_counts.get(title, 0)
            normalized["already_used"] = title in used_titles
            candidates.append(normalized)

        candidates.sort(
            key=lambda q: (
                q.get("usage_count", 0),
                q.get("similarity_delta", 0),
                q.get("title", ""),
            )
        )
        return candidates

    def get_replacement_candidates(self):
        candidates = self.collect_replacement_candidates(allow_reused=False)
        if not candidates:
            candidates = self.collect_replacement_candidates(allow_reused=True)

        search_query = self.replacement_search_query
        ticket = self.get_current_preview_ticket()
        current_topic = ticket["questions"][self.replace_question_index].get("topic")

        if self.replacement_topic_scope == "same" or search_query:
            return candidates[:20]

        grouped_by_topic = {}
        for candidate in candidates:
            grouped_by_topic.setdefault(candidate.get("topic", "—"), []).append(candidate)

        topic_order = sorted(
            grouped_by_topic,
            key=lambda topic: (
                topic != current_topic,
                grouped_by_topic[topic][0].get("similarity_delta", 0),
                topic
            )
        )

        balanced = []
        while len(balanced) < 20:
            added = False
            for topic in topic_order:
                if grouped_by_topic[topic]:
                    balanced.append(grouped_by_topic[topic].pop(0))
                    added = True
                    if len(balanced) >= 20:
                        break
            if not added:
                break

        return balanced

    def draw_replacement_candidates(self):
        for widget in self.replace_results_frame.winfo_children():
            widget.destroy()

        candidates = self.get_replacement_candidates()
        if not candidates:
            ctk.CTkLabel(
                self.replace_results_frame,
                text="Немає доступних замін з такими фільтрами",
                font=FONT_SUBTITLE,
                text_color=COLOR_TEXT_MUTED,
                wraplength=500
            ).pack(pady=48)
            return

        for candidate in candidates:
            row = ctk.CTkFrame(self.replace_results_frame, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=4)

            info = ctk.CTkFrame(row, fg_color=COLOR_PRIMARY_LIGHT, corner_radius=6)
            info.pack(side="left", fill="x", expand=True, padx=(0, 8))

            ctk.CTkLabel(
                info,
                text=candidate.get("title", "Питання"),
                font=FONT_SUBTITLE,
                text_color=COLOR_TEXT,
                anchor="w",
                wraplength=400,
                justify="left"
            ).pack(anchor="w", padx=10, pady=(7, 1))

            candidate_meta = (
                f"{candidate.get('topic', '—')} · {candidate.get('category', '—')} · "
                f"скл. {candidate.get('real_complexity', 0)}"
            )
            if candidate.get("already_used"):
                candidate_meta += " · уже в комплекті"
            ctk.CTkLabel(
                info,
                text=candidate_meta,
                font=FONT_SMALL,
                text_color=COLOR_TEXT_MUTED,
                anchor="w"
            ).pack(anchor="w", padx=10, pady=(0, 7))

            ctk.CTkButton(
                row,
                text="Обрати",
                font=FONT_SMALL,
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                text_color=COLOR_WHITE,
                corner_radius=6,
                width=74,
                height=32,
                command=lambda q=candidate: self.apply_question_replacement(q)
            ).pack(side="right")

    def apply_question_replacement(self, replacement_question):
        ticket = self.get_current_preview_ticket()
        ticket["questions"][self.replace_question_index] = replacement_question
        self.recalculate_ticket(ticket)
        self.backend.generated_data = self.generated_tickets

        self.last_saved_path = None
        if hasattr(self, "open_pdf_button"):
            self.open_pdf_button.configure(
                state="disabled",
                fg_color=COLOR_DISABLED_BG,
                hover_color=COLOR_DISABLED_BG,
                text_color=COLOR_DISABLED_TEXT
            )

        self.replace_overlay.destroy()
        self.draw_ticket_list()
        self.draw_ticket_preview()

    def recalculate_ticket(self, ticket):
        questions = ticket.get("questions", [])
        ticket["difficulty_score"] = round(self.backend.engine.calculate_ticket_score(questions), 3)
        self.backend.engine.distribute_ticket_points(questions, self.total_points)
        ticket["total_points"] = sum(q.get("points", 0) for q in questions)

    def on_save_clicked(self):
        # викликаю бекенд щоб він створив PDF
        # backend.on_save_pdf() внутрішньо викликає save_report_pdf(generated_data, subject_id)
        # який створює файл {subject_id}_report.pdf
        try:
            saved_path = self.backend.on_save_pdf()
            if not saved_path:
                return

            self.last_saved_path = saved_path
            self.last_saved_file = os.path.basename(saved_path)
            self.open_pdf_button.configure(
                state="normal",
                fg_color=COLOR_PRIMARY,
                hover_color=COLOR_PRIMARY_HOVER,
                text_color=COLOR_WHITE
            )
            # PDF успішно створений - показую підтвердження
            self.show_save_success()
        except Exception as e:
            # ловлю помилки збереження
            print(f"Помилка збереження PDF: {e}")
            self.show_save_error(f"Не вдалось зберегти: {str(e)[:50]}")

    def open_saved_pdf(self):
        if not self.last_saved_path or not os.path.exists(self.last_saved_path):
            self.show_save_error("PDF файл не знайдено")
            return

        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", self.last_saved_path])
            elif os.name == "nt":
                os.startfile(self.last_saved_path)
            else:
                subprocess.Popen(["xdg-open", self.last_saved_path])
        except Exception as e:
            self.show_save_error(f"Не вдалось відкрити PDF: {str(e)[:50]}")


    def show_save_success(self):
        # затемнюю весь екран напівпрозорим шаром
        # це "модальне" вікно - фокус на повідомленні, решта тьмяніє
        self.modal_shade = ctk.CTkFrame(
            self.container,
            fg_color=COLOR_PRIMARY_DARK,
            corner_radius=0
        )
        # розтягую шар на весь контейнер
        self.modal_shade.place(relx=0, rely=0, relwidth=1, relheight=1)

        # саме вікно - по центру поверх шару
        dialog = ctk.CTkFrame(
            self.modal_shade,
            fg_color=COLOR_WHITE,
            border_color=COLOR_PRIMARY,
            border_width=2,
            corner_radius=14,
            width=420,
            height=210
        )
        dialog.place(relx=0.5, rely=0.5, anchor="center")
        dialog.pack_propagate(False)

        # зелена галочка-кружок
        icon = ctk.CTkFrame(
            dialog, fg_color=COLOR_PRIMARY_LIGHT,
            corner_radius=28, width=56, height=56
        )
        icon.pack(pady=(24, 10))
        icon.pack_propagate(False)
        ctk.CTkLabel(
            icon, text="✓", font=("Arial", 26, "bold"),
            text_color=COLOR_PRIMARY
        ).pack(expand=True)

        # заголовок
        ctk.CTkLabel(
            dialog, text="PDF збережено!",
            font=FONT_BUTTON, text_color=COLOR_PRIMARY_DARK
        ).pack(pady=(0, 2))

        # назва файлу
        ctk.CTkLabel(
            dialog, text=self.last_saved_file,
            font=FONT_SMALL, text_color=COLOR_TEXT_MUTED
        ).pack(pady=(0, 14))

        # кнопка OK - закриває весь шар разом з вікном
        ctk.CTkButton(
            dialog, text="OK",
            font=FONT_SUBTITLE,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            text_color="white",
            corner_radius=8, width=120, height=34,
            command=self.modal_shade.destroy
        ).pack()

    def show_save_error(self, message):
        # той самий модальний підхід, але з червоним акцентом
        self.modal_shade = ctk.CTkFrame(
            self.container,
            fg_color=COLOR_PRIMARY_DARK,
            corner_radius=0
        )
        self.modal_shade.place(relx=0, rely=0, relwidth=1, relheight=1)

        dialog = ctk.CTkFrame(
            self.modal_shade,
            fg_color=COLOR_WHITE,
            border_color=COLOR_RED,
            border_width=2,
            corner_radius=14,
            width=420,
            height=200
        )
        dialog.place(relx=0.5, rely=0.5, anchor="center")
        dialog.pack_propagate(False)

        ctk.CTkLabel(
            dialog, text="⚠️", font=("Arial", 30),
            text_color=COLOR_RED
        ).pack(pady=(28, 6))

        ctk.CTkLabel(
            dialog, text=message,
            font=FONT_SUBTITLE, text_color=COLOR_RED,
            wraplength=360
        ).pack(pady=(0, 16))

        ctk.CTkButton(
            dialog, text="OK",
            font=FONT_SUBTITLE,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            text_color="white",
            corner_radius=8, width=120, height=34,
            command=self.modal_shade.destroy
        ).pack()

    def reset_and_go_home(self):
        # коли вертаюся на головну - очищаю стан попередньої генерації
        self.mode = None
        self.selected_subject = None
        self.selected_topics = []
        # повертаю дефолтну розкладку
        self.easy_count = 3
        self.medium_count = 2
        self.hard_count = 1
        self.tickets_count = 30
        self.total_points = 100
        self.last_saved_path = None
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.show_screen_1_main_menu()
# ====== допоміжні методи ======

    def draw_progress_bar(self, step, total):
        bar = ctk.CTkFrame(self.container, fg_color="transparent")
        bar.pack(anchor="nw", padx=30, pady=(20, 0))

        for i in range(1, total + 1):
            if i <= step:
                color = COLOR_PRIMARY
            else:
                color = COLOR_BORDER_LIGHT

            seg = ctk.CTkFrame(bar, fg_color=color, width=26, height=4, corner_radius=2)
            seg.pack(side="left", padx=2)
            seg.pack_propagate(False)

        ctk.CTkLabel(
            bar, text=f"  {step} / {total}",
            font=FONT_SMALL, text_color=COLOR_TEXT_MUTED
        ).pack(side="left", padx=8)

    def draw_back_button(self, callback):
        ctk.CTkButton(
            self.container, text="← Назад",
            font=FONT_SUBTITLE, fg_color=COLOR_WHITE, hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_TEXT_MUTED, border_color=COLOR_BORDER, border_width=1,
            corner_radius=6, width=110, height=32,
            command=callback
        ).place(relx=0.04, rely=0.92, anchor="sw")

    def draw_nav_buttons(self, back_cb, next_cb):
        ctk.CTkButton(
            self.container, text="← Назад",
            font=FONT_SUBTITLE, fg_color=COLOR_WHITE, hover_color=COLOR_DISABLED_BG,
            text_color=COLOR_TEXT_MUTED, border_color=COLOR_BORDER, border_width=1,
            corner_radius=6, width=110, height=32,
            command=back_cb
        ).place(relx=0.04, rely=0.92, anchor="sw")

        ctk.CTkButton(
            self.container, text="Далі →",
            font=FONT_BUTTON, fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            text_color=COLOR_WHITE, corner_radius=6, width=110, height=32,
            command=next_cb
        ).place(relx=0.96, rely=0.92, anchor="se")


# запуск
app = ExamAnalyzerApp()
app.mainloop()
