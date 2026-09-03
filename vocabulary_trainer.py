#!/usr/bin/env python3
"""互動式英文單詞練習器（僅使用 Python 標準函式庫）。"""

from __future__ import annotations

import json
import os
import random
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
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
    pattern: str
    memory: str


WORDS = [
    Word("apple", "蘋果", 1, "I eat an apple every morning.", "常用名詞；不必硬拆字根", "把 a + pp + le 分成三小段來拼。"),
    Word("water", "水；澆水", 1, "Please drink more water.", "可作名詞或動詞；不必硬拆字根", "想像 water 在杯子裡晃動。"),
    Word("family", "家庭；家人", 1, "My family eats dinner together.", "常用名詞；整個單詞一起記", "family 裡有 I：I love my family。"),
    Word("friend", "朋友", 1, "She is my best friend.", "常用名詞；不必硬拆字根", "記住固定順序：fri-end，朋友陪你到 end。"),
    Word("happy", "快樂的", 1, "The children look happy.", "-y：常見形容詞字尾", "happy 以雙 p 拼寫，結尾是 y。"),
    Word("school", "學校", 1, "The school is near my home.", "常用名詞；不必硬拆字根", "sch 開頭，後面是雙 o。"),
    Word("morning", "早晨；上午", 1, "I walk to work every morning.", "-ing：此處構成表示時段的名詞", "morn + ing，早晨這段時間。"),
    Word("listen", "聽；傾聽", 1, "Listen carefully to the question.", "常用動詞；不必硬拆字根", "t 不發音，但拼字時不能漏。"),
    Word("answer", "回答；答案", 1, "Can you answer this question?", "可作名詞或動詞；不必硬拆字根", "w 不發音：拼作 ans-wer。"),
    Word("enough", "足夠的；足夠地", 1, "We have enough food for everyone.", "可作形容詞或副詞；不必硬拆字根", "e-nough；gh 不發音，讀音近「依納夫」。"),
    Word("important", "重要的", 2, "Sleep is important for your health.", "-ant：常見形容詞字尾", "注意中間是 port，結尾是 -ant。"),
    Word("different", "不同的", 2, "This answer is different from mine.", "-ent：常見形容詞字尾", "different 中間有雙 f，結尾是 -ent。"),
    Word("remember", "記得；想起", 2, "Remember to lock the door.", "re- 常表示「再次」；此字以整體意思記憶", "把事情重新帶回腦中，就是 remember。"),
    Word("decide", "決定", 2, "We need to decide before noon.", "常用動詞；不必硬拆字根", "先記 de-ci-de 的拼寫節奏。"),
    Word("improve", "改善；進步", 2, "Reading daily will improve your English.", "im- 在此不是否定；不要一律解作「不」", "im + prove 合起來記成 improve。"),
    Word("prepare", "準備", 2, "I need to prepare for the meeting.", "pre-：常表示「在前、預先」", "事前 prepare，就是預先準備。"),
    Word("careful", "小心的；仔細的", 2, "Be careful when crossing the street.", "-ful：常見形容詞字尾，表示「充滿…的」", "care + ful＝充滿留意與關心。"),
    Word("possible", "可能的；可行的", 2, "Is it possible to finish today?", "-ible：常見形容詞字尾，表示「可以…的」", "possible 中間是雙 s，結尾是 -ible。"),
    Word("receive", "收到；接收", 2, "Did you receive my message?", "常用動詞；不必硬拆字根", "i before e，但 c 後面例外：receive。"),
    Word("because", "因為", 2, "I stayed home because it was raining.", "連接詞；不必硬拆字根", "拆成 be + cause 幫助記拼寫即可。"),
    Word("communicate", "溝通；傳達", 3, "Good teams communicate clearly.", "-ate：常見動詞字尾", "communicate 中間有雙 m。"),
    Word("experience", "經驗；經歷", 3, "Travel gives us valuable experience.", "-ence：常見名詞字尾；此字也可作動詞", "結尾固定拼成 -ence。"),
    Word("environment", "環境", 3, "We should protect the environment.", "-ment：常見名詞字尾", "environment＝environ + ment。"),
    Word("opportunity", "機會", 3, "This job is a great opportunity.", "-ity：常見名詞字尾", "注意中間是雙 p，結尾是 -ity。"),
    Word("responsible", "負責任的", 3, "You are responsible for this project.", "-ible：常見形容詞字尾", "respons + ible，注意不是 -able。"),
    Word("available", "可取得的；有空的", 3, "Is this seat available?", "-able：常見形容詞字尾，表示「可以…的」", "avail + able，兩段接起來。"),
    Word("recommend", "推薦；建議", 3, "I recommend the vegetable soup.", "常用動詞；re- 在此不必單獨硬譯", "recommend 中間是雙 m。"),
    Word("necessary", "必要的", 3, "A passport is necessary for the trip.", "-ary：常見形容詞字尾", "一個 c、雙 s：necessary。"),
    Word("successful", "成功的", 3, "Practice is the key to being successful.", "-ful：常見形容詞字尾", "success + ful；success 的雙 c、雙 s 要保留。"),
    Word("convenient", "方便的", 3, "Online banking is convenient.", "-ent：常見形容詞字尾", "conveni + ent，注意中間的 i。"),
    Word("significant", "重要的；顯著的", 4, "There was a significant improvement.", "-ant：常見形容詞字尾", "signific + ant，結尾不是 -ent。"),
    Word("perspective", "觀點；視角", 4, "Try to see it from her perspective.", "常用名詞；不必為了拆字而硬解釋", "想到從某個角度觀看，就連結 perspective。"),
    Word("efficient", "有效率的", 4, "This is a more efficient way to work.", "-ent：常見形容詞字尾", "efficient 中間有雙 f，結尾是 -cient。"),
    Word("consequence", "結果；後果", 4, "Every choice has a consequence.", "-ence：常見名詞字尾", "consequ + ence，結尾固定是 -ence。"),
    Word("essential", "不可或缺的；本質的", 4, "Trust is essential in a friendship.", "-ial：常見形容詞字尾", "essential 中間是雙 s。"),
    Word("maintain", "維持；保養", 4, "Exercise helps maintain good health.", "常用動詞；不必硬拆字根", "main + tain，兩段都有 ain。"),
    Word("independent", "獨立的；自主的", 4, "She became financially independent.", "in-：此處表否定；-ent：形容詞字尾", "in + dependent＝不依賴的。"),
    Word("appropriate", "合適的；恰當的", 4, "Wear appropriate clothes for the event.", "-ate：此處是形容詞字尾", "appropriate 中間有雙 p。"),
    Word("evaluate", "評估；評價", 4, "We need to evaluate the results.", "-ate：常見動詞字尾", "value 變成 evaluate，保留 valu 的拼寫。"),
    Word("acknowledge", "承認；確認收到", 4, "He acknowledged his mistake.", "常用動詞；不必硬拆字根", "先看成 ac + knowledge 來記拼寫。"),
]


# 教材採「常見規律＋例字」呈現；不是每個單詞都適合機械式拆解。
WORD_PARTS_GUIDE = [
    ("否定字首", "un-", "不、相反", "unhappy, unfair"),
    ("否定字首", "in-", "不、非", "independent, incorrect"),
    ("否定字首", "im-", "否定時是 in- 的變形；並非所有 im- 都是否定", "impossible；improve 是例外"),
    ("否定字首", "il- / ir-", "in- 在 l／r 前的變形", "illegal, irregular"),
    ("常用字首", "re-", "再次、向後", "rewrite, return"),
    ("常用字首", "pre-", "在前、預先", "prepare, preview"),
    ("常用字首", "dis-", "不、分離、相反", "disagree, disconnect"),
    ("常用字首", "mis-", "錯誤地", "misunderstand, misspell"),
    ("核心字根", "port", "帶、運送", "transport, portable"),
    ("核心字根", "spect", "看", "inspect, spectator"),
    ("核心字根", "dict", "說、宣告", "predict, dictionary"),
    ("核心字根", "vis / vid", "看", "visible, video"),
    ("核心字根", "tract", "拉、牽引", "attract, contract"),
    ("核心字根", "form", "形狀、形成", "inform, transform"),
    ("核心字根", "graph", "寫、記錄", "autograph, paragraph"),
    ("核心字根", "phon", "聲音", "telephone, microphone"),
    ("核心字根", "struct", "建造", "construct, structure"),
    ("名詞字尾", "-tion / -sion", "動作、狀態、結果", "action, decision"),
    ("名詞字尾", "-ment", "動作、狀態、結果", "environment, improvement"),
    ("名詞字尾", "-ness", "性質、狀態", "happiness, kindness"),
    ("名詞字尾", "-ity", "性質、狀態", "opportunity, ability"),
    ("形容詞字尾", "-ful", "充滿…的", "careful, successful"),
    ("形容詞字尾", "-less", "沒有…的", "careless, hopeless"),
    ("形容詞字尾", "-able / -ible", "可以…的", "available, possible"),
    ("形容詞字尾", "-ant / -ent", "具有某種性質", "important, different"),
    ("形容詞字尾", "-al / -ial", "與…相關的", "natural, essential"),
    ("形容詞字尾", "-ive", "具有…性質的", "active, effective"),
    ("副詞字尾", "-ly", "以某種方式", "carefully, clearly"),
    ("動詞字尾", "-ate", "使成為、進行", "communicate, evaluate"),
    ("動詞字尾", "-ize / -ify", "使成為", "organize, simplify"),
]


def default_progress() -> dict:
    return {
        "words": {}, "days": {}, "custom_words": [],
        "settings": {"new_words_per_day": 5, "review_words_per_day": 20},
        "sessions": 0, "last_session": None,
    }


def load_progress() -> dict:
    if not DATA_FILE.exists():
        return default_progress()
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        if not isinstance(data.get("words"), dict):
            raise ValueError
        data.setdefault("days", {})
        data.setdefault("custom_words", [])
        if not isinstance(data["custom_words"], list):
            data["custom_words"] = []
        settings = data.setdefault("settings", {})
        if not isinstance(settings, dict):
            settings = data["settings"] = {}
        settings.setdefault("new_words_per_day", 5)
        settings.setdefault("review_words_per_day", 20)
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
    stat = progress["words"].setdefault(
        spelling, {"correct": 0, "wrong": 0, "streak": 0, "mastery": 0}
    )
    for key in ("correct", "wrong", "streak", "mastery"):
        stat.setdefault(key, 0)
    stat.setdefault("known", False)
    stat.setdefault("difficult", False)
    return stat


def all_words(progress: dict) -> list[Word]:
    """合併內建與使用者自訂單詞，忽略損壞的舊資料。"""
    result = list(WORDS)
    known = {word.word for word in result}
    for item in progress.get("custom_words", []):
        if not isinstance(item, dict):
            continue
        try:
            word = Word(
                word=str(item["word"]),
                meaning=str(item["meaning"]),
                level=int(item.get("level", 2)),
                example=str(item.get("example", "")),
                pattern=str(item.get("pattern", "自訂單詞；不必硬拆字根")),
                memory=str(item.get("memory", "配合自己的情境記憶。")),
            )
        except (KeyError, TypeError, ValueError):
            continue
        if re.fullmatch(r"[a-z]+", word.word) and word.word not in known:
            result.append(word)
            known.add(word.word)
    return result


def study_words(progress: dict) -> list[Word]:
    return [
        word for word in all_words(progress)
        if not progress.get("words", {}).get(word.word, {}).get("known", False)
    ]


def add_custom_word(
    progress: dict, spelling: str, meaning: str, example: str = "",
    pattern: str = "", memory: str = "",
) -> Word:
    spelling = spelling.strip().lower()
    meaning = meaning.strip()
    if not re.fullmatch(r"[a-z]+", spelling):
        raise ValueError("英文單詞只能包含英文字母。")
    if not meaning:
        raise ValueError("請輸入中文解釋。")
    if spelling in {word.word for word in all_words(progress)}:
        raise ValueError("這個單詞已經存在。")
    word = Word(
        spelling,
        meaning,
        2,
        example.strip() or f'I am learning the word "{spelling}".',
        pattern.strip() or "自訂單詞；不必硬拆字根",
        memory.strip() or "配合自己的情境記憶。",
    )
    progress.setdefault("custom_words", []).append(asdict(word))
    return word


def delete_custom_word(progress: dict, spelling: str) -> bool:
    custom = progress.setdefault("custom_words", [])
    remaining = [
        item for item in custom
        if not isinstance(item, dict) or item.get("word") != spelling
    ]
    if len(remaining) == len(custom):
        return False
    progress["custom_words"] = remaining
    progress.get("words", {}).pop(spelling, None)
    return True


def update_custom_word(
    progress: dict, original: str, spelling: str, meaning: str, example: str = "",
    pattern: str = "", memory: str = "",
) -> Word:
    spelling = spelling.strip().lower()
    meaning = meaning.strip()
    if not re.fullmatch(r"[a-z]+", spelling):
        raise ValueError("英文單詞只能包含英文字母。")
    if not meaning:
        raise ValueError("請輸入中文解釋。")
    existing = {word.word for word in all_words(progress) if word.word != original}
    if spelling in existing:
        raise ValueError("這個單詞已經存在。")
    custom = progress.setdefault("custom_words", [])
    index = next(
        (i for i, item in enumerate(custom)
         if isinstance(item, dict) and item.get("word") == original),
        None,
    )
    if index is None:
        raise ValueError("找不到要編輯的自訂單詞。")
    word = Word(
        spelling, meaning, int(custom[index].get("level", 2)),
        example.strip() or f'I am learning the word "{spelling}".',
        pattern.strip() or "自訂單詞；不必硬拆字根",
        memory.strip() or "配合自己的情境記憶。",
    )
    custom[index] = asdict(word)
    if spelling != original and original in progress.get("words", {}):
        progress["words"][spelling] = progress["words"].pop(original)
    return word


def search_words(progress: dict, query: str, custom_only: bool = False) -> list[Word]:
    query = query.strip().lower()
    words = all_words(progress)
    if custom_only:
        words = words[len(WORDS):]
    if not query:
        return words
    return [
        word for word in words
        if query in word.word.lower() or query in word.meaning.lower()
        or query in word.example.lower() or query in word.pattern.lower()
    ]


def set_word_flag(progress: dict, spelling: str, flag: str, value: bool) -> dict:
    if flag not in {"known", "difficult"}:
        raise ValueError("不支援的單詞狀態。")
    stat = stats_for(progress, spelling)
    stat[flag] = bool(value)
    if flag == "known" and value:
        stat["difficult"] = False
    return stat


def wrong_stage(stat: dict) -> str:
    if stat.get("wrong", 0) <= 0:
        return ""
    if stat.get("mastery", 0) >= 4 and stat.get("streak", 0) >= 3:
        return "已改善"
    if stat.get("wrong", 0) >= 5 and stat.get("mastery", 0) <= 2:
        return "頑固單詞"
    if stat.get("streak", 0) >= 1:
        return "改善中"
    return "待改善"


def record_result(progress: dict, spelling: str, correct: bool, mastery_gain: int = 1) -> dict:
    """記錄答題並安排下次複習；答對越熟練，間隔越長。"""
    stat = stats_for(progress, spelling)
    today = date.today()
    stat["last_review"] = today.isoformat()
    if correct:
        stat["correct"] += 1
        stat["streak"] += 1
        stat["mastery"] = min(5, stat["mastery"] + mastery_gain)
        interval = (1, 1, 3, 7, 14, 30)[stat["mastery"]]
        if stat["difficult"]:
            interval = max(1, interval // 2)
        stat["last_result"] = "correct"
    else:
        stat["wrong"] += 1
        stat["streak"] = 0
        stat["mastery"] = max(0, stat["mastery"] - 1)
        interval = 1
        stat["last_result"] = "wrong"
        if stat["wrong"] >= 5:
            stat["difficult"] = True
    stat["next_review"] = (today + timedelta(days=interval)).isoformat()
    return stat


def due_words(progress: dict, on_date: date | None = None) -> list[Word]:
    target_date = on_date or date.today()
    target = target_date.isoformat()
    due = []
    for word in study_words(progress):
        stat = progress.get("words", {}).get(word.word, {})
        attempts = stat.get("correct", 0) + stat.get("wrong", 0)
        next_review = stat.get("next_review")
        if attempts and (not isinstance(next_review, str) or next_review <= target):
            due.append(word)
    def priority(word: Word) -> tuple:
        stat = stats_for(progress, word.word)
        try:
            due_date = date.fromisoformat(stat.get("next_review", target))
        except (TypeError, ValueError):
            due_date = target_date
        overdue = max(0, (target_date - due_date).days)
        return (-int(stat["difficult"]), -overdue, stat["mastery"], -stat["wrong"], word.word)
    return sorted(due, key=priority)


def wrong_words(progress: dict, include_improved: bool = False) -> list[Word]:
    return sorted(
        [
            word for word in all_words(progress)
            if progress.get("words", {}).get(word.word, {}).get("wrong", 0)
            and (include_improved or wrong_stage(stats_for(progress, word.word)) != "已改善")
            and (include_improved or not stats_for(progress, word.word)["known"])
        ],
        key=lambda word: (
            {"頑固單詞": 0, "待改善": 1, "改善中": 2, "已改善": 3}.get(
                wrong_stage(stats_for(progress, word.word)), 4
            ),
            -stats_for(progress, word.word)["wrong"], word.word,
        ),
    )


def next_review_date(progress: dict, after: date | None = None) -> str | None:
    boundary = (after or date.today()).isoformat()
    dates = [
        stats_for(progress, word.word).get("next_review")
        for word in study_words(progress)
    ]
    future = sorted(value for value in dates if isinstance(value, str) and value > boundary)
    return future[0] if future else None


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
    return f"字詞提示：{word.pattern}"


def explain_mistake(word: Word, answer: str) -> None:
    answer = normalize(answer)
    print(f"\n  正確答案：{word.word}  /  {word.meaning}")
    if answer:
        mismatch = next(
            (i for i, pair in enumerate(zip(answer, word.word)) if pair[0] != pair[1]),
            min(len(answer), len(word.word)),
        )
        print(f"  拼字觀察：前 {mismatch} 個字母正確；請留意後面的「{word.word[mismatch:]}」。")
    print(f"  字詞觀察：{word.pattern}")
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
            record_result(progress, word.word, False)
            return False
        if normalize(raw) == word.word:
            gain = 1 if hints < 2 else 0
            record_result(progress, word.word, True, gain)
            print(f"  ✓ 正確！{word.pattern}")
            print(f"  {word.memory}")
            return True
        record_result(progress, word.word, False)
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
    attempted = [(w, progress["words"].get(w.word, {})) for w in all_words(progress)]
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
    pool = [word for word in all_words(progress) if word.level <= level]
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
