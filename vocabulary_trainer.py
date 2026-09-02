#!/usr/bin/env python3
"""互動式英文單詞練習器（僅使用 Python 標準函式庫）。"""

from __future__ import annotations

import json
import os
import random
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


def progress_file() -> Path:
    """使用可寫入的使用者資料夾，避免 Windows 安裝目錄權限問題。"""
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
        return base / "EverydayEnglish" / "vocabulary_progress.json"
    return Path.home() / ".everyday_english" / "vocabulary_progress.json"


DATA_FILE = progress_file()


@dataclass(frozen=True)
class Word:
    word: str
    meaning: str
    level: int
    example: str
    root: str
    memory: str


WORDS = [
    Word("apple", "蘋果", 1, "I eat an apple every morning.", "無常用字根（古英語詞）", "把 a + pp + le 分成三小段來拼。"),
    Word("water", "水；澆水", 1, "Please drink more water.", "無常用字根（古英語詞）", "想像 water 在杯子裡晃動。"),
    Word("family", "家庭；家人", 1, "My family eats dinner together.", "famili＝家庭、家族", "family 裡有 I：I love my family。"),
    Word("friend", "朋友", 1, "She is my best friend.", "friend＝愛、朋友（古英語）", "記住固定順序：fri-end，朋友陪你到 end。"),
    Word("happy", "快樂的", 1, "The children look happy.", "hap＝機會、好運", "好運 hap 發生，就會 happy。"),
    Word("school", "學校", 1, "The school is near my home.", "scholē＝閒暇、學習（希臘語）", "sch 開頭，後面是雙 o。"),
    Word("morning", "早晨；上午", 1, "I walk to work every morning.", "morn＝早晨", "morn + ing，早晨這段時間。"),
    Word("listen", "聽；傾聽", 1, "Listen carefully to the question.", "list＝聽（古英語）", "t 不發音，但拼字時不能漏。"),
    Word("answer", "回答；答案", 1, "Can you answer this question?", "無常用字根", "w 不發音：拼作 ans-wer。"),
    Word("enough", "足夠的；足夠地", 1, "We have enough food for everyone.", "無常用字根", "e-nough；gh 不發音，讀音近「依納夫」。"),
    Word("important", "重要的", 2, "Sleep is important for your health.", "im（進入）＋port（帶、運）", "被帶進來、需要注意的事，就是重要的。"),
    Word("different", "不同的", 2, "This answer is different from mine.", "dif（分開）＋fer（帶）", "往不同方向帶開，所以是不同的。"),
    Word("remember", "記得；想起", 2, "Remember to lock the door.", "re（再次）＋member（心中留存）", "再次把事情帶回心中。"),
    Word("decide", "決定", 2, "We need to decide before noon.", "de（離開）＋cid（切）", "切掉其他選項，留下決定。"),
    Word("improve", "改善；進步", 2, "Reading daily will improve your English.", "im（使成為）＋prove（證明、好）", "讓事情變得更好、更經得起證明。"),
    Word("prepare", "準備", 2, "I need to prepare for the meeting.", "pre（在前）＋pare（整理）", "事前整理，就是準備。"),
    Word("careful", "小心的；仔細的", 2, "Be careful when crossing the street.", "care（關心）＋ful（充滿）", "充滿關心與注意，所以很仔細。"),
    Word("possible", "可能的；可行的", 2, "Is it possible to finish today?", "poss（能夠）＋ible（可以…的）", "可以做到的，就是 possible。"),
    Word("receive", "收到；接收", 2, "Did you receive my message?", "re（回）＋ceive（拿取）", "i before e，但 c 後面例外：receive。"),
    Word("because", "因為", 2, "I stayed home because it was raining.", "by cause＝由於某個原因", "拆成 be + cause；cause 是原因。"),
    Word("communicate", "溝通；傳達", 3, "Good teams communicate clearly.", "com（共同）＋mun（分享）＋icate（使）", "使彼此共同分享資訊，就是溝通。"),
    Word("experience", "經驗；經歷", 3, "Travel gives us valuable experience.", "ex（向外）＋peri（嘗試）", "親自出去嘗試，累積成經驗。"),
    Word("environment", "環境", 3, "We should protect the environment.", "environ（圍繞）＋ment（名詞）", "圍繞在我們四周的事物。"),
    Word("opportunity", "機會", 3, "This job is a great opportunity.", "op（朝向）＋port（港口）", "船順利進港代表有利時機。"),
    Word("responsible", "負責任的", 3, "You are responsible for this project.", "re（回）＋spons（承諾）＋ible", "能對承諾作出回應的人。"),
    Word("available", "可取得的；有空的", 3, "Is this seat available?", "avail（有用、有價值）＋able", "可以使用、可以取得。"),
    Word("recommend", "推薦；建議", 3, "I recommend the vegetable soup.", "re（再次）＋commend（託付、稱讚）", "一再稱讚並託付給你，就是推薦。"),
    Word("necessary", "必要的", 3, "A passport is necessary for the trip.", "ne（不）＋cess（離開）", "不能離開、不可缺少，所以必要。"),
    Word("successful", "成功的", 3, "Practice is the key to being successful.", "suc（在後）＋cess（前進）＋ful", "一路接續前進，最後充滿成果。"),
    Word("convenient", "方便的", 3, "Online banking is convenient.", "con（一起）＋ven（來）＋ient", "需要的東西都來到一起，使用方便。"),
    Word("significant", "重要的；顯著的", 4, "There was a significant improvement.", "sign（記號）＋fic（做）＋ant", "做出明顯記號，表示影響顯著。"),
    Word("perspective", "觀點；視角", 4, "Try to see it from her perspective.", "per（穿過）＋spect（看）", "透過某個角度去看事情。"),
    Word("efficient", "有效率的", 4, "This is a more efficient way to work.", "ex/e（向外）＋fic（做）＋ient", "把成果有效做出來。"),
    Word("consequence", "結果；後果", 4, "Every choice has a consequence.", "con（一起）＋sequ（跟隨）", "跟隨行動而來的，就是結果。"),
    Word("essential", "不可或缺的；本質的", 4, "Trust is essential in a friendship.", "ess（存在、本質）＋ial", "關係到事物本質，所以不可缺少。"),
    Word("maintain", "維持；保養", 4, "Exercise helps maintain good health.", "main/man（手）＋tain（握住）", "用手持續握住某個狀態。"),
    Word("independent", "獨立的；自主的", 4, "She became financially independent.", "in（不）＋depend（依靠）＋ent", "不依靠別人，就是獨立。"),
    Word("appropriate", "合適的；恰當的", 4, "Wear appropriate clothes for the event.", "ap（朝向）＋propri（自己的、合宜的）", "對這個場合正好合宜。"),
    Word("evaluate", "評估；評價", 4, "We need to evaluate the results.", "e（向外）＋valu（價值）＋ate", "把價值衡量出來。"),
    Word("acknowledge", "承認；確認收到", 4, "He acknowledged his mistake.", "ac（朝向）＋knowledge（知道）", "明確表示自己知道了。"),
]


def default_progress() -> dict:
    return {"words": {}, "days": {}, "sessions": 0, "last_session": None}


def load_progress() -> dict:
    if not DATA_FILE.exists():
        return default_progress()
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if not isinstance(data.get("words"), dict):
            raise ValueError
        data.setdefault("days", {})
        return data
    except (OSError, json.JSONDecodeError, ValueError):
        print("提醒：進度檔無法讀取，本次將使用新進度（原檔不會刪除）。")
        return default_progress()


def save_progress(progress: dict) -> None:
    progress["last_session"] = datetime.now().isoformat(timespec="seconds")
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = DATA_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(DATA_FILE)


def stats_for(progress: dict, spelling: str) -> dict:
    return progress["words"].setdefault(
        spelling, {"correct": 0, "wrong": 0, "streak": 0, "mastery": 0}
    )


def normalize(text: str) -> str:
    return re.sub(r"[^a-z]", "", text.lower())


def choose_word(pool: list[Word], progress: dict, recent: list[str]) -> Word:
    candidates = [word for word in pool if word.word not in recent[-2:]] or pool
    weights = []
    for word in candidates:
        stat = stats_for(progress, word.word)
        # 錯題及尚未熟練的字會更常出現；答對連續三次後降低頻率。
        weight = 2 + stat["wrong"] * 3 + max(0, 3 - stat["mastery"])
        weight += 5 if stat["wrong"] > 0 and stat["streak"] < 2 else 0
        weights.append(weight)
    return random.choices(candidates, weights=weights, k=1)[0]


def reveal_hint(word: Word, stage: int) -> str:
    if stage == 1:
        return f"首字母：{word.word[0].upper()}，共 {len(word.word)} 個字母"
    if stage == 2:
        shown = "".join(ch if i % 2 == 0 else "_" for i, ch in enumerate(word.word))
        return f"拼字骨架：{shown}"
    return f"字源提示：{word.root}"


def explain_mistake(word: Word, answer: str) -> None:
    answer = normalize(answer)
    print(f"\n  正確答案：{word.word}  /  {word.meaning}")
    if answer:
        mismatch = next(
            (i for i, pair in enumerate(zip(answer, word.word)) if pair[0] != pair[1]),
            min(len(answer), len(word.word)),
        )
        print(f"  拼字觀察：前 {mismatch} 個字母正確；請留意後面的「{word.word[mismatch:]}」。")
    print(f"  字首／字根：{word.root}")
    print(f"  記憶法：{word.memory}")
    print(f"  例句：{word.example}")
    print("  這個字已加入錯題回流，稍後會再次出現。")


def ask_word(word: Word, progress: dict, number: int, total: int) -> bool | None:
    stat = stats_for(progress, word.word)
    print(f"\n[{number}/{total}] Level {word.level}｜熟練度 {stat['mastery']}/5")
    print(f"中文：{word.meaning}")
    print(f"例句：{word.example.replace(word.word, '_____').replace(word.word.capitalize(), '_____')}")
    hints = 0
    while True:
        raw = input("請輸入英文（? 提示／s 跳過／q 結束）：").strip()
        command = raw.lower()
        if command == "q":
            return None
        if command == "?":
            hints = min(hints + 1, 3)
            print("  " + reveal_hint(word, hints))
            continue
        if command == "s":
            explain_mistake(word, "")
            stat["wrong"] += 1
            stat["streak"] = 0
            stat["mastery"] = max(0, stat["mastery"] - 1)
            return False
        if normalize(raw) == word.word:
            stat["correct"] += 1
            stat["streak"] += 1
            gain = 1 if hints < 2 else 0
            stat["mastery"] = min(5, stat["mastery"] + gain)
            print(f"  ✓ 正確！{word.root}")
            print(f"  {word.memory}")
            return True
        stat["wrong"] += 1
        stat["streak"] = 0
        stat["mastery"] = max(0, stat["mastery"] - 1)
        explain_mistake(word, raw)
        return False


def select_number(prompt: str, minimum: int, maximum: int, default: int) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw:
            return default
        if raw.isdigit() and minimum <= int(raw) <= maximum:
            return int(raw)
        print(f"請輸入 {minimum}～{maximum} 的數字。")


def show_report(progress: dict) -> None:
    attempted = [(w, progress["words"].get(w.word, {})) for w in WORDS]
    attempted = [(w, s) for w, s in attempted if s.get("correct", 0) + s.get("wrong", 0)]
    if not attempted:
        print("\n還沒有練習紀錄。")
        return
    correct = sum(s["correct"] for _, s in attempted)
    wrong = sum(s["wrong"] for _, s in attempted)
    print(f"\n累積作答：{correct + wrong} 題｜正確率：{correct / (correct + wrong):.0%}")
    weak = sorted(attempted, key=lambda item: (item[1]["mastery"], -item[1]["wrong"]))[:8]
    print("待加強：")
    for word, stat in weak:
        print(f"  {word.word:<15} {word.meaning:<14} 熟練度 {stat['mastery']}/5")


def practice(progress: dict) -> None:
    level = select_number("選擇最高難度 1～4（預設 1）：", 1, 4, 1)
    count = select_number("本輪題數 5～30（預設 10）：", 5, 30, 10)
    pool = [word for word in WORDS if word.level <= level]
    recent: list[str] = []
    session_correct = 0
    answered = 0
    print("\n開始練習。大小寫不影響答案；輸入 ? 可逐步取得提示。")
    for number in range(1, count + 1):
        word = choose_word(pool, progress, recent)
        recent.append(word.word)
        result = ask_word(word, progress, number, count)
        if result is None:
            break
        answered += 1
        session_correct += int(result)
        save_progress(progress)
    progress["sessions"] = progress.get("sessions", 0) + 1
    save_progress(progress)
    if answered:
        print(f"\n本輪完成：{answered} 題，答對 {session_correct} 題（{session_correct / answered:.0%}）。")


def main() -> None:
    progress = load_progress()
    print("=" * 46)
    print("  Everyday English｜英文單詞練習器")
    print("  看中文、讀情境、親手拼出英文")
    print("=" * 46)
    while True:
        print("\n1. 開始練習   2. 查看學習報告   3. 離開")
        choice = input("請選擇：").strip()
        if choice == "1":
            practice(progress)
        elif choice == "2":
            show_report(progress)
        elif choice in {"3", "q", "Q"}:
            save_progress(progress)
            print("進度已保存。每天練一點，會比一次背很多更牢固！")
            break
        else:
            print("請輸入 1、2 或 3。")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n練習已結束。")
