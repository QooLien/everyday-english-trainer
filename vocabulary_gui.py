#!/usr/bin/env python3
"""Everyday English 的 Windows Tkinter 圖形介面。"""

from __future__ import annotations

import tkinter as tk
import calendar
from datetime import date
from tkinter import messagebox, ttk

import vocabulary_trainer as core


BG = "#F3F6FB"
CARD = "#FFFFFF"
INK = "#15213B"
MUTED = "#64748B"
BLUE = "#2563EB"
GREEN = "#0F8F63"
RED = "#D13C4B"
BORDER = "#DCE5F0"
NAVY = "#17213A"


class VocabularyApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Everyday English｜英文單詞練習器")
        self.geometry("1020x760")
        self.minsize(880, 650)
        self.configure(bg=BG)
        self.protocol("WM_DELETE_WINDOW", self.close_app)

        self.progress_data = core.load_progress()
        settings = self.progress_data.setdefault("settings", {})
        self.question_count = tk.IntVar(value=settings.get("new_words_per_day", 5))
        self.review_count = tk.IntVar(value=settings.get("review_words_per_day", 20))
        self.answer = tk.StringVar()
        self.custom_word = tk.StringVar()
        self.custom_meaning = tk.StringVar()
        self.custom_example = tk.StringVar()
        self.custom_pattern = tk.StringVar()
        self.custom_memory = tk.StringVar()
        self.custom_search = tk.StringVar()
        self.editing_custom_word: str | None = None
        self.pool: list[core.Word] = []
        self.recent: list[str] = []
        self.current: core.Word | None = None
        self.number = 0
        self.correct = 0
        self.hints = 0
        self.answered = False
        self.study_words: list[core.Word] = []
        self.study_index = 0
        self.exam_queue: list[core.Word] = []
        self.exam_total = 0
        self.retry_added: set[str] = set()
        self.session_kind = "learning"

        self._configure_style()
        self._build_navigation()
        self.container = tk.Frame(self, bg=BG, padx=38, pady=24)
        self.container.pack(fill="both", expand=True)
        self.show_home()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        for theme in ("clam", "aqua", "vista"):
            if theme in style.theme_names():
                style.theme_use(theme)
                break
        style.configure("TButton", font=("Arial", 13), padding=(16, 10))
        style.configure("Primary.TButton", foreground="white", background=BLUE)
        style.map("Primary.TButton", background=[("active", "#1D4ED8")])
        style.configure("Nav.TButton", foreground="#DDE7F6", background=NAVY,
                        borderwidth=0, padding=(11, 8), font=("Arial", 10))
        style.map("Nav.TButton", foreground=[("active", "white")],
                  background=[("active", "#263656")])
        style.configure("Active.Nav.TButton", foreground="white", background="#31589B",
                        borderwidth=0, padding=(11, 8), font=("Arial", 10, "bold"))
        style.configure("TEntry", font=("Arial", 18), padding=9)
        style.configure("TCombobox", font=("Arial", 12), padding=6)
        style.configure("Horizontal.TProgressbar", troughcolor="#E4E9F2", background=BLUE)
        style.configure("Treeview", rowheight=30, font=("Arial", 11),
                        background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), padding=(8, 8))

    def _build_navigation(self) -> None:
        bar = tk.Frame(self, bg=NAVY, padx=26, pady=12)
        bar.pack(fill="x")
        brand = tk.Frame(bar, bg=NAVY)
        brand.pack(side="left")
        tk.Label(brand, text="EVERYDAY", bg=NAVY, fg="#8FB5FF",
                 font=("Arial", 9, "bold")).pack(anchor="w")
        tk.Label(brand, text="English Trainer", bg=NAVY, fg="white",
                 font=("Arial", 16, "bold")).pack(anchor="w")
        nav = tk.Frame(bar, bg=NAVY)
        nav.pack(side="right", pady=4)
        items = (
            ("home", "首頁", self.show_home), ("review", "今日複習", self.start_due_review),
            ("wrong", "錯題本", self.show_wrong_book),
            ("custom", "自訂單詞", self.show_custom_words),
            ("guide", "字詞教材", self.show_word_parts_guide),
            ("report", "學習紀錄", self.show_report),
        )
        self.nav_buttons: dict[str, ttk.Button] = {}
        for key, label, command in items:
            button = ttk.Button(nav, text=label, style="Nav.TButton", command=command)
            button.pack(side="left", padx=2)
            self.nav_buttons[key] = button

    def set_active_nav(self, active: str) -> None:
        for key, button in self.nav_buttons.items():
            button.configure(style="Active.Nav.TButton" if key == active else "Nav.TButton")

    def clear(self) -> None:
        self.unbind("<Return>")
        for child in self.container.winfo_children():
            child.destroy()

    def heading(self, title: str, subtitle: str = "") -> None:
        tk.Label(self.container, text=title, bg=BG, fg=INK,
                 font=("Arial", 26, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(self.container, text=subtitle, bg=BG, fg=MUTED,
                     font=("Arial", 12), pady=6).pack(anchor="w")

    def card(self) -> tk.Frame:
        frame = tk.Frame(self.container, bg=CARD, padx=28, pady=24,
                         highlightbackground=BORDER, highlightthickness=1)
        frame.pack(fill="both", expand=True, pady=(18, 0))
        return frame

    def metric(self, parent: tk.Widget, column: int, value: str, label: str, color: str) -> None:
        tile = tk.Frame(parent, bg="white", padx=18, pady=14,
                        highlightbackground=BORDER, highlightthickness=1)
        tile.grid(row=0, column=column, padx=(0 if column == 0 else 8, 0), sticky="nsew")
        parent.columnconfigure(column, weight=1)
        tk.Label(tile, text=value, bg="white", fg=color,
                 font=("Arial", 24, "bold")).pack(anchor="w")
        tk.Label(tile, text=label, bg="white", fg=MUTED,
                 font=("Arial", 10)).pack(anchor="w")

    def show_home(self) -> None:
        self.clear()
        self.set_active_nav("home")
        self.heading("Everyday English", "看懂情境、親手拼字，讓錯題成為下一次的記憶。")
        due_count = len(core.due_words(self.progress_data))
        wrong_count = len(core.wrong_words(self.progress_data))
        custom_count = len(self.progress_data.get("custom_words", []))
        next_review = core.next_review_date(self.progress_data)
        if due_count:
            recommendation = f"建議下一步：先完成 {min(due_count, self.get_review_limit())} 個到期單詞"
        elif wrong_count:
            recommendation = "建議下一步：今天沒有到期項目，可集中練習錯題"
        else:
            recommendation = f"建議下一步：開始學習 {self.question_count.get()} 個新單詞"
        stats = tk.Frame(self.container, bg=BG)
        stats.pack(fill="x", pady=(12, 0))
        self.metric(stats, 0, str(due_count), "今日到期複習", BLUE)
        self.metric(stats, 1, str(wrong_count), "錯題本單詞", RED)
        self.metric(stats, 2, str(custom_count), "自訂單詞", GREEN)

        panel = self.card()
        tk.Label(panel, text="今日學習計畫", bg=CARD, fg=INK,
                 font=("Arial", 18, "bold")).pack(anchor="w", pady=(0, 14))

        row2 = tk.Frame(panel, bg=CARD)
        row2.pack(fill="x", pady=8)
        tk.Label(row2, text="今日單詞數", bg=CARD, fg=INK,
                 font=("Arial", 13), width=12, anchor="w").pack(side="left")
        ttk.Spinbox(row2, from_=5, to=30, increment=5, textvariable=self.question_count,
                    width=8, font=("Arial", 13)).pack(side="left")
        tk.Label(row2, text="每日複習上限", bg=CARD, fg=INK,
                 font=("Arial", 13), padx=28).pack(side="left")
        ttk.Spinbox(row2, from_=5, to=50, increment=5, textvariable=self.review_count,
                    width=8, font=("Arial", 13)).pack(side="left")

        info = tk.Label(panel, text=(
                            f"{recommendation}\n"
                            "每次只練一小組，答錯單詞會加入本輪回流與錯題本。"),
                        bg="#EEF4FF", fg="#294F9B", font=("Arial", 12),
                        padx=16, pady=14, justify="left", anchor="w")
        info.pack(fill="x", pady=(14, 18))

        primary = tk.Frame(panel, bg=CARD)
        primary.pack(fill="x", pady=(0, 12))
        review_text = f"複習到期單詞（{due_count}）"
        if not due_count and next_review:
            review_text = f"下次複習：{next_review}"
        review_button = ttk.Button(primary, text=review_text, command=self.start_due_review)
        review_button.pack(side="left")
        if not due_count:
            review_button.state(["disabled"])
        ttk.Button(primary, text="開始今日學習 →", style="Primary.TButton",
                   command=self.start_practice).pack(side="right")

        tools = tk.Frame(panel, bg=CARD)
        tools.pack(fill="x")
        ttk.Button(tools, text=f"錯題本（{wrong_count}）",
                   command=self.show_wrong_book).pack(side="left")
        ttk.Button(tools, text=f"自訂單詞庫（{custom_count}）",
                   command=self.show_custom_words).pack(side="left", padx=8)
        ttk.Button(tools, text="學習月曆", command=self.show_report).pack(side="left")
        ttk.Button(tools, text="字首字尾教材",
                   command=self.show_word_parts_guide).pack(side="left", padx=8)

        tk.Label(panel, text="詞彙資料基礎：Open English WordNet（CC BY 4.0）",
                 bg=CARD, fg=MUTED, font=("Arial", 10)).pack(anchor="w", pady=(22, 0))

    def start_practice(self) -> None:
        try:
            count = int(self.question_count.get())
        except (ValueError, tk.TclError):
            count = 10
        self.question_count.set(max(3, min(15, count)))
        self.progress_data.setdefault("settings", {})["new_words_per_day"] = self.question_count.get()
        indexed = list(enumerate(core.study_words(self.progress_data)))
        indexed.sort(key=lambda item: (core.stats_for(self.progress_data, item[1].word)["mastery"],
                                       item[1].level, item[0]))
        self.study_words = [word for _, word in indexed[:self.question_count.get()]]
        if not self.study_words:
            messagebox.showinfo("今日學習", "所有單詞都已標記為已掌握。可到錯題本調整單詞狀態。")
            return
        self.study_index = 0
        self.recent = []
        self.number = 0
        self.correct = 0
        self.session_kind = "learning"
        today = self.progress_data["days"].setdefault(date.today().isoformat(),
                                                       {"learned": 0, "tested": 0, "correct": 0, "completed": False})
        today["learned"] += len(self.study_words)
        core.save_progress(self.progress_data)
        self.show_learning_card()

    def show_learning_card(self) -> None:
        word = self.study_words[self.study_index]
        self.clear()
        self.set_active_nav("home")
        self.heading(f"先學習｜{self.study_index + 1} / {len(self.study_words)}", "看、讀、理解，再用鍵盤回想。")
        panel = self.card()
        word_row = tk.Frame(panel, bg=CARD)
        word_row.pack(fill="x")
        tk.Label(word_row, text=word.word, bg=CARD, fg=BLUE,
                 font=("Arial", 38, "bold")).pack(side="left")
        tk.Label(word_row, text=f"LEVEL {word.level}", bg="#E8F0FF", fg=BLUE,
                 font=("Arial", 10, "bold"), padx=12, pady=6).pack(side="right", pady=8)
        tk.Label(panel, text=word.meaning, bg=CARD, fg=INK,
                 font=("Arial", 20, "bold"), pady=12).pack(anchor="w")
        tk.Label(panel, text=f"例句  {word.example}", bg="#EEF4FF", fg="#294F9B",
                 font=("Arial", 13), padx=16, pady=14, wraplength=680,
                 justify="left", anchor="w").pack(fill="x", pady=8)
        insights = tk.Frame(panel, bg=CARD)
        insights.pack(fill="x", pady=14)
        insights.columnconfigure(0, weight=1)
        insights.columnconfigure(1, weight=1)
        for column, title, text in (
            (0, "字詞觀察", word.pattern), (1, "記憶連結", word.memory),
        ):
            box = tk.Frame(insights, bg="#F7F9FC", padx=16, pady=14,
                           highlightbackground=BORDER, highlightthickness=1)
            box.grid(row=0, column=column, padx=(0, 8) if column == 0 else (8, 0), sticky="nsew")
            tk.Label(box, text=title, bg="#F7F9FC", fg=MUTED,
                     font=("Arial", 10, "bold")).pack(anchor="w")
            tk.Label(box, text=text, bg="#F7F9FC", fg=INK, font=("Arial", 12),
                     wraplength=390, justify="left").pack(anchor="w", pady=(7, 0))
        label = "完成學習，開始考試 →" if self.study_index == len(self.study_words) - 1 else "我已理解，下一個 →"
        ttk.Button(panel, text=label, style="Primary.TButton",
                   command=self.next_learning_card).pack(side="bottom", anchor="e")

    def next_learning_card(self) -> None:
        self.study_index += 1
        if self.study_index < len(self.study_words):
            self.show_learning_card()
            return
        self.start_exam(self.study_words, "learning")

    def start_exam(self, words: list[core.Word], kind: str) -> None:
        self.exam_queue = words[:]
        __import__("random").shuffle(self.exam_queue)
        self.exam_total = len(self.exam_queue)
        self.retry_added = set()
        self.number = 0
        self.correct = 0
        self.session_kind = kind
        self.current = None
        self.answered = False
        self.next_question()

    def start_due_review(self) -> None:
        words = core.due_words(self.progress_data)
        if not words:
            messagebox.showinfo("今日複習", "目前沒有到期的單詞。完成學習後，系統會自動安排複習日期。")
            return
        limit = self.get_review_limit()
        self.progress_data.setdefault("settings", {})["review_words_per_day"] = limit
        core.save_progress(self.progress_data)
        self.start_exam(words[:limit], "review")

    def get_review_limit(self) -> int:
        try:
            limit = max(5, min(50, int(self.review_count.get())))
        except (ValueError, tk.TclError):
            limit = 20
        self.review_count.set(limit)
        self.progress_data.setdefault("settings", {})["review_words_per_day"] = limit
        return limit

    def start_wrong_review(self) -> None:
        words = core.wrong_words(self.progress_data)
        if not words:
            messagebox.showinfo("錯題本", "目前沒有錯題。")
            return
        self.start_exam(words[:self.get_review_limit()], "wrong")

    def start_custom_review(self) -> None:
        words = core.all_words(self.progress_data)[len(core.WORDS):]
        if not words:
            messagebox.showinfo("自訂單詞庫", "請先加入至少一個自訂單詞。")
            return
        self.start_exam(words[:self.get_review_limit()], "custom")

    def next_question(self) -> None:
        if not self.exam_queue:
            self.finish_session()
            return
        self.number += 1
        self.current = self.exam_queue.pop(0)
        self.recent.append(self.current.word)
        self.hints = 0
        self.answered = False
        self.answer.set("")
        self.show_question()

    def show_question(self) -> None:
        assert self.current is not None
        self.clear()
        active = {"review": "review", "wrong": "wrong", "custom": "custom"}.get(
            self.session_kind, "home"
        )
        self.set_active_nav(active)
        top = tk.Frame(self.container, bg=BG)
        top.pack(fill="x")
        mode_name = {
            "review": "到期複習", "wrong": "錯題複習", "custom": "自訂單詞練習",
        }.get(self.session_kind, "拼字考試")
        tk.Label(top, text=f"{mode_name}第 {self.number} 題｜尚餘 {len(self.exam_queue) + 1} 題",
                 bg=BG, fg=INK, font=("Arial", 15, "bold")).pack(side="left")
        ttk.Button(top, text="結束本輪", command=self.finish_session).pack(side="right")
        bar = ttk.Progressbar(self.container, maximum=max(1, self.exam_total),
                              value=min(self.number - 1, self.exam_total))
        bar.pack(fill="x", pady=(14, 0))

        panel = self.card()
        stat = core.stats_for(self.progress_data, self.current.word)
        tk.Label(panel, text=f"回想測驗   •   熟練度 {stat['mastery']}/5",
                 bg=CARD, fg=BLUE, font=("Arial", 11, "bold")).pack(anchor="w")
        tk.Label(panel, text=self.current.meaning, bg=CARD, fg=INK,
                 font=("Arial", 25, "bold"), pady=14).pack(anchor="w")
        blank = self.current.example.replace(self.current.word, "_____")
        blank = blank.replace(self.current.word.capitalize(), "_____")
        tk.Label(panel, text=blank, bg=CARD, fg=MUTED, font=("Arial", 14),
                 wraplength=680, justify="left").pack(anchor="w", pady=(0, 22))

        self.entry = ttk.Entry(panel, textvariable=self.answer)
        self.entry.pack(fill="x")
        self.bind("<Return>", self.handle_enter)
        self.entry.focus_set()

        self.hint_label = tk.Label(panel, text="", bg=CARD, fg="#75570A",
                                   font=("Arial", 12), wraplength=680, justify="left")
        self.hint_label.pack(anchor="w", pady=(12, 4))
        self.feedback = tk.Label(panel, text="", bg=CARD, fg=INK, font=("Arial", 12),
                                 wraplength=680, justify="left", anchor="nw")
        self.feedback.pack(fill="both", expand=True, pady=6)

        self.action_row = tk.Frame(panel, bg=CARD)
        self.action_row.pack(fill="x", side="bottom", pady=(12, 0))
        ttk.Button(self.action_row, text="給我提示", command=self.show_hint).pack(side="left")
        ttk.Button(self.action_row, text="跳過並講解", command=self.skip_word).pack(side="left", padx=10)
        ttk.Button(self.action_row, text="確認答案", style="Primary.TButton",
                   command=self.submit_answer).pack(side="right")

    def handle_enter(self, _event: tk.Event | None = None) -> str:
        """第一次 Enter 送出答案；結果顯示後再按 Enter 前往下一題。"""
        if self.current is None:
            return "break"
        if self.answered:
            self.next_question()
        else:
            self.submit_answer()
        return "break"

    def show_hint(self) -> None:
        if self.answered or self.current is None:
            return
        self.hints = min(3, self.hints + 1)
        self.hint_label.config(text="提示：" + core.reveal_hint(self.current, self.hints))

    def explanation(self, answer: str) -> str:
        assert self.current is not None
        typed = core.normalize(answer)
        spelling_note = ""
        if typed:
            mismatch = next((i for i, pair in enumerate(zip(typed, self.current.word))
                             if pair[0] != pair[1]), min(len(typed), len(self.current.word)))
            spelling_note = f"\n拼字觀察：前 {mismatch} 個字母正確；留意「{self.current.word[mismatch:]}」。"
        return (f"正確答案：{self.current.word}｜{self.current.meaning}{spelling_note}\n"
                f"字詞觀察：{self.current.pattern}\n記憶法：{self.current.memory}\n"
                f"例句：{self.current.example}\n這個字已加入錯題回流，稍後會再次出現。")

    def mark_wrong(self, answer: str) -> None:
        assert self.current is not None
        stat = core.record_result(self.progress_data, self.current.word, False)
        if self.current.word not in self.retry_added:
            self.exam_queue.append(self.current)
            self.retry_added.add(self.current.word)
            self.exam_total += 1
        self.finish_answer(
            self.explanation(answer) + f'\n下次複習：{stat["next_review"]}', RED
        )

    def submit_answer(self) -> None:
        if self.answered or self.current is None:
            return
        typed = self.answer.get().strip()
        if not typed:
            self.hint_label.config(text="請先輸入單詞，或選擇提示／跳過。", fg=RED)
            return
        if core.normalize(typed) == self.current.word:
            stat = core.record_result(
                self.progress_data, self.current.word, True,
                1 if self.hints < 2 else 0,
            )
            self.correct += 1
            text = (f"答對了！\n字詞觀察：{self.current.pattern}\n"
                    f"記憶法：{self.current.memory}\n下次複習：{stat['next_review']}")
            self.finish_answer(text, GREEN)
        else:
            self.mark_wrong(typed)

    def skip_word(self) -> None:
        if not self.answered and self.current is not None:
            self.mark_wrong("")

    def finish_answer(self, text: str, color: str) -> None:
        self.answered = True
        self.entry.config(state="disabled")
        self.feedback.config(text=text, fg=color)
        core.save_progress(self.progress_data)
        for child in self.action_row.winfo_children():
            child.destroy()
        ttk.Button(self.action_row, text="下一題 →", style="Primary.TButton",
                   command=self.next_question).pack(side="right")

    def finish_session(self) -> None:
        attempted = max(0, self.number - (0 if self.answered else 1))
        self.progress_data["sessions"] = self.progress_data.get("sessions", 0) + 1
        today = self.progress_data["days"].setdefault(date.today().isoformat(), {})
        today["tested"] = today.get("tested", 0) + attempted
        today["correct"] = today.get("correct", 0) + self.correct
        today["completed"] = attempted > 0
        core.save_progress(self.progress_data)
        self.clear()
        title = "複習完成" if self.session_kind in {"review", "wrong"} else "本輪完成"
        self.heading(title, "每次回想都在加深記憶連結。")
        panel = self.card()
        rate = self.correct / attempted if attempted else 0
        tk.Label(panel, text=f"{rate:.0%}", bg=CARD, fg=BLUE,
                 font=("Arial", 52, "bold")).pack(pady=(35, 4))
        tk.Label(panel, text=f"共作答 {attempted} 題，答對 {self.correct} 題",
                 bg=CARD, fg=MUTED, font=("Arial", 15)).pack()
        buttons = tk.Frame(panel, bg=CARD)
        buttons.pack(side="bottom", pady=28)
        ttk.Button(buttons, text="學習報告", command=self.show_report).pack(side="left", padx=6)
        ttk.Button(buttons, text="再練一輪", style="Primary.TButton",
                   command=self.show_home).pack(side="left", padx=6)

    def show_wrong_book(self) -> None:
        self.clear()
        self.set_active_nav("wrong")
        words = core.wrong_words(self.progress_data, include_improved=True)
        self.heading("錯題本", "追蹤待改善、改善中與已改善單詞；困難單詞會優先安排。")
        panel = self.card()
        if not words:
            tk.Label(panel, text="目前沒有錯題。", bg=CARD, fg=MUTED,
                     font=("Arial", 16)).pack(pady=100)
        else:
            columns = ("word", "meaning", "stage", "wrong", "mastery", "next")
            self.wrong_table = ttk.Treeview(panel, columns=columns, show="headings", height=12)
            settings = (
                ("word", "單詞", 125), ("meaning", "中文", 200),
                ("stage", "改善狀態", 95), ("wrong", "錯誤", 60),
                ("mastery", "熟練度", 75),
                ("next", "下次複習", 110),
            )
            for column, title, width in settings:
                self.wrong_table.heading(column, text=title)
                self.wrong_table.column(column, width=width, anchor="w")
            for word in words:
                stat = core.stats_for(self.progress_data, word.word)
                stage = core.wrong_stage(stat)
                if stat["known"]:
                    stage = "已掌握"
                elif stat["difficult"] and stage != "已改善":
                    stage = "★ " + stage
                self.wrong_table.insert("", "end", iid=word.word, values=(
                    word.word, word.meaning, stage, stat["wrong"],
                    f'{stat["mastery"]} / 5', stat.get("next_review", "今天"),
                ))
            self.wrong_table.pack(fill="both", expand=True)
        buttons = tk.Frame(panel, bg=CARD)
        buttons.pack(fill="x", pady=(16, 0))
        if words:
            ttk.Button(buttons, text="標記／取消困難",
                       command=self.toggle_selected_difficult).pack(side="left")
            ttk.Button(buttons, text="標記／取消已掌握",
                       command=self.toggle_selected_known).pack(side="left", padx=8)
        ttk.Button(buttons, text="開始複習錯題 →", style="Primary.TButton",
                   command=self.start_wrong_review).pack(side="right")

    def selected_wrong_word(self) -> str | None:
        selected = getattr(self, "wrong_table", None)
        if selected is None or not selected.selection():
            messagebox.showinfo("錯題本", "請先選取一個單詞。")
            return None
        return selected.selection()[0]

    def toggle_selected_difficult(self) -> None:
        spelling = self.selected_wrong_word()
        if spelling is None:
            return
        stat = core.stats_for(self.progress_data, spelling)
        core.set_word_flag(self.progress_data, spelling, "difficult", not stat["difficult"])
        core.save_progress(self.progress_data)
        self.show_wrong_book()

    def toggle_selected_known(self) -> None:
        spelling = self.selected_wrong_word()
        if spelling is None:
            return
        stat = core.stats_for(self.progress_data, spelling)
        core.set_word_flag(self.progress_data, spelling, "known", not stat["known"])
        core.save_progress(self.progress_data)
        self.show_wrong_book()

    def show_custom_words(self) -> None:
        self.clear()
        self.set_active_nav("custom")
        self.heading("自訂單詞庫", "加入自己的單詞、例句與記憶提示；之後會納入學習與複習。")
        panel = self.card()
        form = tk.Frame(panel, bg=CARD)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        fields = (
            (0, 0, "英文單詞", self.custom_word, 1, 1),
            (0, 2, "中文解釋", self.custom_meaning, 3, 1),
            (1, 0, "英文例句", self.custom_example, 1, 3),
            (2, 0, "字詞觀察", self.custom_pattern, 1, 3),
            (3, 0, "記憶提示", self.custom_memory, 1, 3),
        )
        for row, label_col, label, variable, entry_col, span in fields:
            tk.Label(form, text=label, bg=CARD, fg=INK, font=("Arial", 11)).grid(
                row=row, column=label_col, sticky="w", padx=(0, 8), pady=4
            )
            ttk.Entry(form, textvariable=variable, font=("Arial", 11)).grid(
                row=row, column=entry_col, columnspan=span, sticky="ew", padx=(0, 12), pady=4
            )
        self.save_custom_button = ttk.Button(
            form, text="儲存修改" if self.editing_custom_word else "加入單詞",
            style="Primary.TButton", command=self.add_custom_word,
        )
        self.save_custom_button.grid(row=4, column=3, sticky="e", pady=(6, 10))
        if self.editing_custom_word:
            ttk.Button(form, text="取消編輯", command=self.cancel_custom_edit).grid(
                row=4, column=2, sticky="e", padx=8, pady=(6, 10)
            )

        search = tk.Frame(panel, bg=CARD)
        search.pack(fill="x", pady=(0, 8))
        tk.Label(search, text="搜尋", bg=CARD, fg=INK,
                 font=("Arial", 11)).pack(side="left", padx=(0, 8))
        search_entry = ttk.Entry(search, textvariable=self.custom_search, font=("Arial", 11))
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind("<Return>", lambda _event: self.show_custom_words())
        ttk.Button(search, text="套用", command=self.show_custom_words).pack(side="left", padx=8)
        ttk.Button(search, text="清除", command=self.clear_custom_search).pack(side="left")

        custom = core.search_words(self.progress_data, self.custom_search.get(), custom_only=True)
        columns = ("word", "meaning", "example")
        toolbar = tk.Frame(panel, bg=CARD)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="練習自訂單詞", style="Primary.TButton",
                   command=self.start_custom_review).pack(side="left")
        ttk.Button(toolbar, text="刪除選取單詞",
                   command=self.delete_selected_custom_word).pack(side="left", padx=8)
        ttk.Button(toolbar, text="編輯選取單詞",
                   command=self.edit_selected_custom_word).pack(side="left")

        self.custom_table = ttk.Treeview(panel, columns=columns, show="headings", height=5)
        for column, title, width in (("word", "單詞", 130), ("meaning", "中文", 180),
                                     ("example", "例句", 390)):
            self.custom_table.heading(column, text=title)
            self.custom_table.column(column, width=width, anchor="w")
        for word in custom:
            self.custom_table.insert("", "end", iid=word.word,
                                     values=(word.word, word.meaning, word.example))
        self.custom_table.pack(fill="both", expand=True)
        self.custom_table.bind("<Double-1>", lambda _event: self.edit_selected_custom_word())

    def add_custom_word(self) -> None:
        try:
            values = (
                self.custom_word.get(), self.custom_meaning.get(), self.custom_example.get(),
                self.custom_pattern.get(), self.custom_memory.get(),
            )
            if self.editing_custom_word:
                core.update_custom_word(
                    self.progress_data, self.editing_custom_word, *values,
                )
            else:
                core.add_custom_word(self.progress_data, *values)
        except ValueError as error:
            messagebox.showerror("無法加入單詞", str(error))
            return
        core.save_progress(self.progress_data)
        self.editing_custom_word = None
        for variable in (self.custom_word, self.custom_meaning, self.custom_example,
                         self.custom_pattern, self.custom_memory):
            variable.set("")
        self.show_custom_words()

    def edit_selected_custom_word(self) -> None:
        selected = self.custom_table.selection()
        if not selected:
            messagebox.showinfo("編輯單詞", "請先在表格中選取一個自訂單詞。")
            return
        spelling = selected[0]
        word = next(
            (item for item in core.all_words(self.progress_data) if item.word == spelling),
            None,
        )
        if word is None:
            return
        self.editing_custom_word = spelling
        self.custom_word.set(word.word)
        self.custom_meaning.set(word.meaning)
        self.custom_example.set(word.example)
        self.custom_pattern.set(word.pattern)
        self.custom_memory.set(word.memory)
        self.show_custom_words()

    def cancel_custom_edit(self) -> None:
        self.editing_custom_word = None
        for variable in (self.custom_word, self.custom_meaning, self.custom_example,
                         self.custom_pattern, self.custom_memory):
            variable.set("")
        self.show_custom_words()

    def clear_custom_search(self) -> None:
        self.custom_search.set("")
        self.show_custom_words()

    def delete_selected_custom_word(self) -> None:
        selected = self.custom_table.selection()
        if not selected:
            messagebox.showinfo("刪除單詞", "請先在表格中選取一個自訂單詞。")
            return
        spelling = selected[0]
        if not messagebox.askyesno("刪除單詞", f"確定要刪除 {spelling} 及其學習紀錄嗎？"):
            return
        if core.delete_custom_word(self.progress_data, spelling):
            core.save_progress(self.progress_data)
        if self.editing_custom_word == spelling:
            self.editing_custom_word = None
        self.show_custom_words()

    def show_word_parts_guide(self) -> None:
        self.clear()
        self.set_active_nav("guide")
        self.heading("字首・字根・字尾教材", "先辨認常見規律，再用例字理解；不是每個單詞都需要硬拆。")
        panel = self.card()
        columns = ("category", "part", "meaning", "examples")
        table_area = tk.Frame(panel, bg=CARD)
        table_area.pack(fill="both", expand=True)
        table = ttk.Treeview(table_area, columns=columns, show="headings", height=16)
        settings = (
            ("category", "類別", 105),
            ("part", "字首／字根／字尾", 130),
            ("meaning", "常見功能", 230),
            ("examples", "教材例字", 220),
        )
        for column, title, width in settings:
            table.heading(column, text=title)
            table.column(column, width=width, anchor="w")
        for row in core.WORD_PARTS_GUIDE:
            table.insert("", "end", values=row)

        scrollbar = ttk.Scrollbar(table_area, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_report(self) -> None:
        self.clear()
        self.set_active_nav("report")
        self.heading("學習月曆", "每天完成學習與考試，留下可追蹤的學習紀錄。")
        panel = self.card()
        today = date.today()
        cal = calendar.Calendar(firstweekday=0)
        tk.Label(panel, text=f"{today.year} 年 {today.month} 月", bg=CARD, fg=INK,
                 font=("Arial", 17, "bold")).pack(anchor="w")
        grid = tk.Frame(panel, bg=CARD)
        grid.pack(fill="x", pady=(12, 18))
        for col, name in enumerate(("一", "二", "三", "四", "五", "六", "日")):
            tk.Label(grid, text=name, bg=CARD, fg=MUTED, font=("Arial", 10, "bold"),
                     width=8).grid(row=0, column=col, sticky="nsew")
            grid.columnconfigure(col, weight=1)
        for row, week in enumerate(cal.monthdayscalendar(today.year, today.month), 1):
            for col, day in enumerate(week):
                if not day:
                    continue
                key = date(today.year, today.month, day).isoformat()
                record = self.progress_data.get("days", {}).get(key, {})
                done = record.get("completed", False)
                text = f"{day}\n{'✓' if done else '·'}"
                tk.Label(grid, text=text, bg="#DDF5E9" if done else "#F5F7FA",
                         fg=GREEN if done else MUTED, font=("Arial", 11, "bold" if done else "normal"),
                         pady=5).grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
        attempted = [(w, self.progress_data["words"].get(w.word, {}))
                     for w in core.all_words(self.progress_data)]
        attempted = [(w, s) for w, s in attempted if s.get("correct", 0) + s.get("wrong", 0)]
        if not attempted:
            tk.Label(panel, text="還沒有練習紀錄，完成第一輪後就會看到成果。",
                     bg=CARD, fg=MUTED, font=("Arial", 14)).pack(pady=70)
        else:
            correct = sum(s["correct"] for _, s in attempted)
            wrong = sum(s["wrong"] for _, s in attempted)
            tk.Label(panel, text=f"累積 {correct + wrong} 題   •   正確率 {correct / (correct + wrong):.0%}",
                     bg=CARD, fg=INK, font=("Arial", 17, "bold")).pack(anchor="w", pady=(0, 16))
            columns = ("word", "meaning", "mastery", "wrong")
            table_area = tk.Frame(panel, bg=CARD)
            table_area.pack(fill="both", expand=True)
            table = ttk.Treeview(table_area, columns=columns, show="headings", height=4)
            for col, title, width in (("word", "單詞", 150), ("meaning", "解釋", 250),
                                      ("mastery", "熟練度", 100), ("wrong", "錯誤", 70)):
                table.heading(col, text=title)
                table.column(col, width=width, anchor="w")
            weak = sorted(attempted, key=lambda item: (item[1]["mastery"], -item[1]["wrong"]))
            for word, stat in weak:
                table.insert("", "end", values=(word.word, word.meaning,
                                                  f"{stat['mastery']} / 5", stat["wrong"]))
            scrollbar = ttk.Scrollbar(table_area, orient="vertical", command=table.yview)
            table.configure(yscrollcommand=scrollbar.set)
            table.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

    def close_app(self) -> None:
        try:
            self.progress_data.setdefault("settings", {})["review_words_per_day"] = self.get_review_limit()
            try:
                new_limit = max(3, min(15, int(self.question_count.get())))
            except (ValueError, tk.TclError):
                new_limit = 5
            self.progress_data["settings"]["new_words_per_day"] = new_limit
            core.save_progress(self.progress_data)
        finally:
            self.destroy()


if __name__ == "__main__":
    VocabularyApp().mainloop()
