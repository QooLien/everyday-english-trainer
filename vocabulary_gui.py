#!/usr/bin/env python3
"""Everyday English 的跨平台 Tkinter 圖形介面。"""

from __future__ import annotations

import tkinter as tk
import calendar
from datetime import date
from tkinter import messagebox, ttk

import vocabulary_trainer as core


BG = "#F4F7FB"
CARD = "#FFFFFF"
INK = "#172033"
MUTED = "#667085"
BLUE = "#356AE6"
GREEN = "#16865C"
RED = "#C13B45"


class VocabularyApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Everyday English｜英文單詞練習器")
        self.geometry("820x650")
        self.minsize(680, 570)
        self.configure(bg=BG)
        self.protocol("WM_DELETE_WINDOW", self.close_app)

        self.progress_data = core.load_progress()
        self.question_count = tk.IntVar(value=5)
        self.answer = tk.StringVar()
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

        self._configure_style()
        self.container = tk.Frame(self, bg=BG, padx=34, pady=26)
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
        style.map("Primary.TButton", background=[("active", "#2857C5")])
        style.configure("TEntry", font=("Arial", 18), padding=9)
        style.configure("TCombobox", font=("Arial", 12), padding=6)
        style.configure("Horizontal.TProgressbar", troughcolor="#E4E9F2", background=BLUE)

    def clear(self) -> None:
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
                         highlightbackground="#DDE3EC", highlightthickness=1)
        frame.pack(fill="both", expand=True, pady=(18, 0))
        return frame

    def show_home(self) -> None:
        self.clear()
        self.heading("Everyday English", "看懂情境、親手拼字，讓錯題成為下一次的記憶。")
        panel = self.card()

        tk.Label(panel, text="今日學習計畫", bg=CARD, fg=INK,
                 font=("Arial", 18, "bold")).pack(anchor="w", pady=(0, 20))

        row2 = tk.Frame(panel, bg=CARD)
        row2.pack(fill="x", pady=8)
        tk.Label(row2, text="今日單詞數", bg=CARD, fg=INK,
                 font=("Arial", 13), width=12, anchor="w").pack(side="left")
        ttk.Spinbox(row2, from_=5, to=30, increment=5, textvariable=self.question_count,
                    width=8, font=("Arial", 13)).pack(side="left")

        info = tk.Label(panel, text="先逐字學習解釋、例句與字根，完成學習後才會開始考試。\n系統依常用度與難度自動由淺至深安排，不需選擇章節。",
                        bg="#EEF4FF", fg="#294F9B", font=("Arial", 12),
                        padx=16, pady=14, justify="left", anchor="w")
        info.pack(fill="x", pady=(24, 22))

        buttons = tk.Frame(panel, bg=CARD)
        buttons.pack(fill="x", side="bottom")
        ttk.Button(buttons, text="學習月曆", command=self.show_report).pack(side="left")
        ttk.Button(buttons, text="開始今日學習 →", style="Primary.TButton",
                   command=self.start_practice).pack(side="right")

        tk.Label(panel, text="詞彙資料基礎：Open English WordNet（CC BY 4.0）",
                 bg=CARD, fg=MUTED, font=("Arial", 10)).pack(side="bottom", anchor="w", pady=(18, 0))

    def start_practice(self) -> None:
        try:
            count = int(self.question_count.get())
        except (ValueError, tk.TclError):
            count = 10
        self.question_count.set(max(3, min(15, count)))
        indexed = list(enumerate(core.WORDS))
        indexed.sort(key=lambda item: (core.stats_for(self.progress_data, item[1].word)["mastery"],
                                       item[1].level, item[0]))
        self.study_words = [word for _, word in indexed[:self.question_count.get()]]
        self.study_index = 0
        self.recent = []
        self.number = 0
        self.correct = 0
        today = self.progress_data["days"].setdefault(date.today().isoformat(),
                                                       {"learned": 0, "tested": 0, "correct": 0, "completed": False})
        today["learned"] += len(self.study_words)
        core.save_progress(self.progress_data)
        self.show_learning_card()

    def show_learning_card(self) -> None:
        word = self.study_words[self.study_index]
        self.clear()
        self.heading(f"先學習｜{self.study_index + 1} / {len(self.study_words)}", "看、讀、理解，再用鍵盤回想。")
        panel = self.card()
        tk.Label(panel, text=word.word, bg=CARD, fg=BLUE,
                 font=("Arial", 38, "bold")).pack(anchor="w")
        tk.Label(panel, text=word.meaning, bg=CARD, fg=INK,
                 font=("Arial", 20, "bold"), pady=12).pack(anchor="w")
        tk.Label(panel, text=f"例句  {word.example}", bg="#EEF4FF", fg="#294F9B",
                 font=("Arial", 13), padx=16, pady=14, wraplength=680,
                 justify="left", anchor="w").pack(fill="x", pady=8)
        tk.Label(panel, text=f"字首／字根\n{word.root}\n\n記憶連結\n{word.memory}",
                 bg=CARD, fg=INK, font=("Arial", 13), wraplength=680,
                 justify="left").pack(anchor="w", pady=16)
        label = "完成學習，開始考試 →" if self.study_index == len(self.study_words) - 1 else "我已理解，下一個 →"
        ttk.Button(panel, text=label, style="Primary.TButton",
                   command=self.next_learning_card).pack(side="bottom", anchor="e")

    def next_learning_card(self) -> None:
        self.study_index += 1
        if self.study_index < len(self.study_words):
            self.show_learning_card()
            return
        self.exam_queue = self.study_words[:]
        __import__("random").shuffle(self.exam_queue)
        self.exam_total = len(self.exam_queue)
        self.retry_added = set()
        self.next_question()

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
        top = tk.Frame(self.container, bg=BG)
        top.pack(fill="x")
        tk.Label(top, text=f"考試第 {self.number} 題｜尚餘 {len(self.exam_queue) + 1} 題",
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
        self.entry.bind("<Return>", lambda _event: self.submit_answer())
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
                f"字首／字根：{self.current.root}\n記憶法：{self.current.memory}\n"
                f"例句：{self.current.example}\n這個字已加入錯題回流，稍後會再次出現。")

    def mark_wrong(self, answer: str) -> None:
        assert self.current is not None
        stat = core.stats_for(self.progress_data, self.current.word)
        stat["wrong"] += 1
        stat["streak"] = 0
        stat["mastery"] = max(0, stat["mastery"] - 1)
        if self.current.word not in self.retry_added:
            self.exam_queue.append(self.current)
            self.retry_added.add(self.current.word)
            self.exam_total += 1
        self.finish_answer(self.explanation(answer), RED)

    def submit_answer(self) -> None:
        if self.answered or self.current is None:
            return
        typed = self.answer.get().strip()
        if not typed:
            self.hint_label.config(text="請先輸入單詞，或選擇提示／跳過。", fg=RED)
            return
        if core.normalize(typed) == self.current.word:
            stat = core.stats_for(self.progress_data, self.current.word)
            stat["correct"] += 1
            stat["streak"] += 1
            stat["mastery"] = min(5, stat["mastery"] + (1 if self.hints < 2 else 0))
            self.correct += 1
            text = f"答對了！\n字首／字根：{self.current.root}\n記憶法：{self.current.memory}"
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
        self.heading("本輪完成", "每次回想都在加深記憶連結。")
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

    def show_report(self) -> None:
        self.clear()
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
        attempted = [(w, self.progress_data["words"].get(w.word, {})) for w in core.WORDS]
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
            table = ttk.Treeview(panel, columns=columns, show="headings", height=10)
            for col, title, width in (("word", "單詞", 150), ("meaning", "解釋", 250),
                                      ("mastery", "熟練度", 100), ("wrong", "錯誤", 70)):
                table.heading(col, text=title)
                table.column(col, width=width, anchor="w")
            weak = sorted(attempted, key=lambda item: (item[1]["mastery"], -item[1]["wrong"]))
            for word, stat in weak:
                table.insert("", "end", values=(word.word, word.meaning,
                                                  f"{stat['mastery']} / 5", stat["wrong"]))
            table.pack(fill="both", expand=True)
        ttk.Button(panel, text="← 返回首頁", command=self.show_home).pack(side="bottom", anchor="w", pady=(18, 0))

    def close_app(self) -> None:
        try:
            core.save_progress(self.progress_data)
        finally:
            self.destroy()


if __name__ == "__main__":
    VocabularyApp().mainloop()
