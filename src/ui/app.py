# ExamAnalyzer - візуальна частина
# Робить Андрій

import customtkinter as ctk
import sys
import os

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
WINDOW_HEIGHT = 470

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
        # передаю назву, бали і атрибут (easy_count/medium_count/hard_count)
        self.create_difficulty_row(center, "Легких", 2, "easy_count")
        self.create_difficulty_row(center, "Середніх", 3, "medium_count")
        self.create_difficulty_row(center, "Важких", 5, "hard_count")

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

    def create_difficulty_row(self, parent, name, points, attr_name):
        # створюю один рядок для категорії складності
        # name - "Легких", "Середніх", "Важких"
        # points - 2, 3 або 5
        # attr_name - "easy_count", "medium_count" чи "hard_count"

        # фрейм для одного рядка
        row = ctk.CTkFrame(parent, fg_color=COLOR_PRIMARY_LIGHT, corner_radius=8)
        row.pack(fill="x", pady=4, padx=20)

        # підпис ліворуч
        ctk.CTkLabel(
            row,
            text=f"{name} (по {points} бали)",
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

        # оновлюю підсумок внизу
        self.summary_label.configure(text=self.get_summary_text())

        # оновлюю стан кнопки далі
        self.update_next_button_e5()

    def get_summary_text(self):
        # формую текст підсумку
        total_q = self.get_total_questions()
        total_p = self.get_total_points()
        return f"Всього: {total_q} питань · {total_p} балів"

    def get_total_questions(self):
        # обчислюю загальну кількість питань
        return self.easy_count + self.medium_count + self.hard_count

    def get_total_points(self):
        # обчислюю загальну кількість балів
        return self.easy_count * 2 + self.medium_count * 3 + self.hard_count * 5

    def update_next_button_e5(self):
        # блокую далі якщо нічого не вибрано
        if self.get_total_questions() == 0:
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
            self.show_generation_error(f"Помилка: {str(e)[:50]}")

    def show_generation_error(self, message):
        # просте діалогове вікно з помилкою
        # використовую CTkFrame поверх контейнера
        error_overlay = ctk.CTkFrame(
            self.container,
            fg_color=COLOR_WHITE,
            border_color=COLOR_RED,
            border_width=2,
            corner_radius=10,
            width=400,
            height=120
        )
        error_overlay.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            error_overlay, text="⚠️ " + message,
            font=FONT_BUTTON, text_color=COLOR_RED,
            wraplength=360
        ).pack(pady=(20, 8))

        ctk.CTkButton(
            error_overlay, text="OK",
            font=FONT_SUBTITLE,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            text_color="white",
            corner_radius=6, width=100, height=30,
            command=error_overlay.destroy
        ).pack()

    def get_subject_display_name(self):
        # перетворюю id предмета з банку на читабельну назву
        if self.selected_subject == "math_analysis":
            return "Мат. аналіз"
        elif self.selected_subject == "physics":
            return "Фізика"
        else:
            return "—"

# ====== ЕКРАН 8: Готово ======
    def show_screen_8_done(self):
        self.clear_container()

        # формую назву PDF файлу - так само як це робить file_manager
        # save_report_pdf зберігає файл з назвою {subject_id}_report.pdf
        # у поточну директорію звідки запускається апка
        self.last_saved_file = f"{self.selected_subject}_report.pdf"

        center = ctk.CTkFrame(self.container, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # кружок з галочкою
        icon = ctk.CTkFrame(
            center,
            fg_color=COLOR_PRIMARY_LIGHT,
            corner_radius=35,
            width=70,
            height=70
        )
        icon.pack(pady=(0, 14))
        icon.pack_propagate(False)

        ctk.CTkLabel(
            icon, text="✓",
            font=("Arial", 32, "bold"),
            text_color=COLOR_PRIMARY
        ).pack(expand=True)

        # заголовок
        ctk.CTkLabel(
            center, text="Готово!",
            font=FONT_TITLE, text_color=COLOR_PRIMARY_DARK
        ).pack()

        # реальна кількість білетів зі стану
        ctk.CTkLabel(
            center,
            text=f"{self.tickets_count} білетів згенеровано",
            font=FONT_SUBTITLE, text_color=COLOR_TEXT_MUTED
        ).pack(pady=(0, 4))

        # додатковий рядок з деталями (з реальною розкладкою)
        details_text = f"{self.get_subject_display_name()} · {self.get_total_questions()} питань у білеті"
        ctk.CTkLabel(
            center,
            text=details_text,
            font=FONT_SMALL, text_color=COLOR_DISABLED_TEXT
        ).pack(pady=(0, 16))

        # рядок з шляхом до файлу
        file_info = ctk.CTkFrame(
            center,
            fg_color=COLOR_PRIMARY_LIGHT,
            corner_radius=8,
            width=320,
            height=36
        )
        file_info.pack(pady=(0, 14))
        file_info.pack_propagate(False)

        ctk.CTkLabel(
            file_info,
            text=f"📁  {self.last_saved_file}",
            font=FONT_SMALL,
            text_color=COLOR_PRIMARY
        ).pack(expand=True)

        # кнопка зберегти
        ctk.CTkButton(
            center, text="Зберегти на комп'ютер",
            font=FONT_BUTTON, fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            text_color=COLOR_WHITE, corner_radius=8,
            width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
            command=self.on_save_clicked
        ).pack(pady=4)

        # кнопка повернутись на головну
        ctk.CTkButton(
            center, text="На головну",
            font=FONT_BUTTON, fg_color=COLOR_WHITE, hover_color=COLOR_PRIMARY_LIGHT,
            text_color=COLOR_PRIMARY, border_color=COLOR_PRIMARY, border_width=2,
            corner_radius=8, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
            command=self.reset_and_go_home
        ).pack(pady=4)

    def on_save_clicked(self):
        # викликаю бекенд щоб він створив PDF
        # backend.on_save_pdf() внутрішньо викликає save_report_pdf(generated_data, subject_id)
        # який створює файл {subject_id}_report.pdf
        try:
            self.backend.on_save_pdf()
            # PDF успішно створений - показую підтвердження
            self.show_save_success()
        except Exception as e:
            # ловлю помилки збереження
            print(f"Помилка збереження PDF: {e}")
            self.show_save_error(f"Не вдалось зберегти: {str(e)[:50]}")

    def show_save_success(self):
        # маленьке вікно успіху після збереження
        success_overlay = ctk.CTkFrame(
            self.container,
            fg_color=COLOR_WHITE,
            border_color=COLOR_PRIMARY,
            border_width=2,
            corner_radius=10,
            width=380,
            height=120
        )
        success_overlay.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            success_overlay, text="✓ PDF збережено!",
            font=FONT_BUTTON, text_color=COLOR_PRIMARY_DARK
        ).pack(pady=(18, 4))

        ctk.CTkLabel(
            success_overlay,
            text=f"Файл: {self.last_saved_file}",
            font=FONT_SMALL, text_color=COLOR_TEXT_MUTED
        ).pack(pady=(0, 8))

        ctk.CTkButton(
            success_overlay, text="OK",
            font=FONT_SUBTITLE,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            text_color="white",
            corner_radius=6, width=100, height=28,
            command=success_overlay.destroy
        ).pack()

    def show_save_error(self, message):
        # помилка збереження
        error_overlay = ctk.CTkFrame(
            self.container,
            fg_color=COLOR_WHITE,
            border_color=COLOR_RED,
            border_width=2,
            corner_radius=10,
            width=400,
            height=120
        )
        error_overlay.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            error_overlay, text="⚠️ " + message,
            font=FONT_BUTTON, text_color=COLOR_RED,
            wraplength=360
        ).pack(pady=(20, 8))

        ctk.CTkButton(
            error_overlay, text="OK",
            font=FONT_SUBTITLE,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            text_color="white",
            corner_radius=6, width=100, height=30,
            command=error_overlay.destroy
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