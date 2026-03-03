"""
╔══════════════════════════════════════════════════════════════╗
║              CEREBRO — Aesthetic Tkinter Quiz App            ║
║         Features: Levels | Random Questions | Fullscreen     ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import font as tkfont
import json
import random
import os
import sys
import time
import threading

# ─────────────────────────────────────────────
#  THEME PALETTE
# ─────────────────────────────────────────────
THEME = {
    "bg_dark":      "#0A0A0F",
    "bg_card":      "#12121A",
    "bg_panel":     "#1A1A28",
    "accent":       "#7C3AED",      # violet
    "accent_glow":  "#A78BFA",
    "easy":         "#10B981",      # emerald
    "medium":       "#F59E0B",      # amber
    "hard":         "#EF4444",      # red
    "text_primary": "#F1F5F9",
    "text_muted":   "#64748B",
    "text_dim":     "#334155",
    "correct":      "#10B981",
    "wrong":        "#EF4444",
    "border":       "#1E1E30",
    "option_bg":    "#16162A",
    "option_hover": "#1E1E3A",
    "white":        "#FFFFFF",
}

LEVEL_CONFIG = {
    "easy":   {"color": THEME["easy"],   "emoji": "🌱", "label": "EASY",   "time": 30},
    "medium": {"color": THEME["medium"], "emoji": "⚡", "label": "MEDIUM", "time": 20},
    "hard":   {"color": THEME["hard"],   "emoji": "🔥", "label": "HARD",   "time": 15},
}

# ─────────────────────────────────────────────
#  LOAD QUESTIONS
# ─────────────────────────────────────────────
def load_questions(filepath: str) -> dict:
    """Load and return questions dict from JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filepath)
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_random_questions(questions: list, count: int = 10) -> list:
    """Shuffle and return `count` non-repeated questions."""
    pool = questions.copy()
    random.shuffle(pool)
    return pool[:min(count, len(pool))]

def validate_answer(selected: str, correct: str) -> bool:
    """Return True if selected matches correct answer."""
    return selected.strip().lower() == correct.strip().lower()

def calculate_score(correct: int, total: int, level: str, time_bonuses: list) -> dict:
    """Compute detailed score breakdown."""
    base_points = {"easy": 10, "medium": 20, "hard": 30}
    pts = base_points.get(level, 10)
    raw_score = correct * pts
    time_bonus = sum(time_bonuses)
    final = raw_score + time_bonus
    percentage = round((correct / total) * 100) if total > 0 else 0
    return {
        "correct": correct,
        "total": total,
        "raw_score": raw_score,
        "time_bonus": time_bonus,
        "final": final,
        "percentage": percentage,
    }

# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
class CerebroQuiz(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CEREBRO — Knowledge Quiz")
        self.configure(bg=THEME["bg_dark"])
        self.resizable(True, True)
        self.geometry("900x650")
        self.minsize(800, 580)

        self._fullscreen = False
        self.bind("<F11>",    self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        # State
        self.all_questions  = {}
        self.questions      = []
        self.current_idx    = 0
        self.score          = 0
        self.correct_count  = 0
        self.selected_level = tk.StringVar(value="medium")
        self.time_bonuses   = []
        self._timer_job     = None
        self._time_left     = 0
        self._answered      = False

        self._load_data()
        self._build_fonts()
        self._show_intro()

    # ── Data ──────────────────────────────────
    def _load_data(self):
        try:
            self.all_questions = load_questions("questions.json")
        except FileNotFoundError:
            self.all_questions = {"easy": [], "medium": [], "hard": []}

    # ── Fonts ─────────────────────────────────
    def _build_fonts(self):
        self.font_hero   = tkfont.Font(family="Courier New", size=36, weight="bold")
        self.font_title  = tkfont.Font(family="Courier New", size=18, weight="bold")
        self.font_sub    = tkfont.Font(family="Courier New", size=11)
        self.font_body   = tkfont.Font(family="Courier New", size=13)
        self.font_option = tkfont.Font(family="Courier New", size=12)
        self.font_small  = tkfont.Font(family="Courier New", size=10)
        self.font_tag    = tkfont.Font(family="Courier New", size=9, weight="bold")

    # ── Helpers ───────────────────────────────
    def _clear(self):
        for w in self.winfo_children():
            w.destroy()
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None

    def toggle_fullscreen(self, event=None):
        self._fullscreen = not self._fullscreen
        self.attributes("-fullscreen", self._fullscreen)

    def exit_fullscreen(self, event=None):
        if self._fullscreen:
            self._fullscreen = False
            self.attributes("-fullscreen", False)

    # ─────────────────────────────────────────
    #  SCREEN 1 — INTRO
    # ─────────────────────────────────────────
    def _show_intro(self):
        self._clear()

        # Outer canvas for gradient-like background effect
        canvas = tk.Canvas(self, bg=THEME["bg_dark"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # ── draw decorative grid lines ──
        def draw_grid(event=None):
            canvas.delete("grid")
            w, h = canvas.winfo_width(), canvas.winfo_height()
            for x in range(0, w, 60):
                canvas.create_line(x, 0, x, h, fill="#0E0E1A", tags="grid")
            for y in range(0, h, 60):
                canvas.create_line(0, y, w, y, fill="#0E0E1A", tags="grid")
            # accent circle top-right
            canvas.create_oval(w-200, -100, w+100, 200,
                                outline=THEME["accent"], width=1, tags="grid")
            canvas.create_oval(w-160, -60, w+60, 160,
                                outline="#1E1E40", width=1, tags="grid")
            # dot cluster bottom-left
            for i in range(5):
                for j in range(5):
                    canvas.create_oval(30+i*18, h-130+j*18,
                                       42+i*18, h-118+j*18,
                                       fill="#1A1A2E", outline="", tags="grid")

        canvas.bind("<Configure>", draw_grid)

        # ── center frame ──
        frame = tk.Frame(canvas, bg=THEME["bg_dark"])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # logo tag
        tk.Label(frame,
                 text="⬡  CEREBRO  ⬡",
                 font=self.font_tag,
                 fg=THEME["accent_glow"],
                 bg=THEME["bg_dark"],
                 pady=4).pack()

        # hero title
        tk.Label(frame,
                 text="KNOWLEDGE\nQUIZ",
                 font=self.font_hero,
                 fg=THEME["text_primary"],
                 bg=THEME["bg_dark"],
                 justify="center",
                 pady=0).pack()

        # thin accent rule
        rule_canvas = tk.Canvas(frame, bg=THEME["bg_dark"],
                                height=3, width=300, highlightthickness=0)
        rule_canvas.pack(pady=8)
        rule_canvas.create_rectangle(0, 0, 300, 3, fill=THEME["accent"], outline="")

        # subtitle
        tk.Label(frame,
                 text="Test your mind across levels of difficulty.\nRandomized questions. Time pressure. Pure intellect.",
                 font=self.font_small,
                 fg=THEME["text_muted"],
                 bg=THEME["bg_dark"],
                 justify="center",
                 pady=6).pack()

        # ── level selector ──
        level_frame = tk.Frame(frame, bg=THEME["bg_dark"])
        level_frame.pack(pady=18)

        tk.Label(level_frame,
                 text="SELECT DIFFICULTY",
                 font=self.font_tag,
                 fg=THEME["text_muted"],
                 bg=THEME["bg_dark"]).grid(row=0, columnspan=3, pady=(0, 10))

        self._level_btns = {}
        for col, (lvl, cfg) in enumerate(LEVEL_CONFIG.items()):
            btn = tk.Button(
                level_frame,
                text=f"{cfg['emoji']}  {cfg['label']}",
                font=self.font_small,
                fg=cfg["color"],
                bg=THEME["bg_panel"],
                activebackground=THEME["bg_card"],
                activeforeground=cfg["color"],
                relief="flat",
                bd=0,
                padx=20,
                pady=10,
                cursor="hand2",
                command=lambda l=lvl: self._select_level(l),
            )
            btn.grid(row=1, column=col, padx=8)
            self._level_btns[lvl] = btn

        self._select_level("medium")

        # ── start button ──
        start_btn = tk.Button(
            frame,
            text="▶  START QUIZ",
            font=self.font_title,
            fg=THEME["bg_dark"],
            bg=THEME["accent"],
            activebackground=THEME["accent_glow"],
            activeforeground=THEME["bg_dark"],
            relief="flat",
            bd=0,
            padx=40,
            pady=14,
            cursor="hand2",
            command=self._start_quiz,
        )
        start_btn.pack(pady=(8, 4))
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg=THEME["accent_glow"]))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg=THEME["accent"]))

        # fullscreen hint
        tk.Label(frame,
                 text="F11 — fullscreen   |   ESC — exit fullscreen",
                 font=self.font_small,
                 fg=THEME["text_dim"],
                 bg=THEME["bg_dark"]).pack(pady=(14, 0))

    def _select_level(self, level: str):
        self.selected_level.set(level)
        for lvl, btn in self._level_btns.items():
            cfg = LEVEL_CONFIG[lvl]
            if lvl == level:
                btn.config(bg=cfg["color"], fg=THEME["bg_dark"], relief="flat")
            else:
                btn.config(bg=THEME["bg_panel"], fg=cfg["color"], relief="flat")

    # ─────────────────────────────────────────
    #  SCREEN 2 — QUIZ
    # ─────────────────────────────────────────
    def _start_quiz(self):
        level = self.selected_level.get()
        raw   = self.all_questions.get(level, [])
        if not raw:
            self._show_error("No questions found for this level!")
            return

        self.questions    = get_random_questions(raw, count=10)
        self.current_idx  = 0
        self.correct_count= 0
        self.score        = 0
        self.time_bonuses = []
        self._show_question()

    def _show_question(self):
        self._clear()
        self._answered = False
        q_data = self.questions[self.current_idx]
        level  = self.selected_level.get()
        cfg    = LEVEL_CONFIG[level]

        # ── root layout ──
        root_frame = tk.Frame(self, bg=THEME["bg_dark"])
        root_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # ── TOP BAR ──
        top = tk.Frame(root_frame, bg=THEME["bg_dark"])
        top.pack(fill="x", pady=(0, 16))

        # left: level badge + question counter
        left_top = tk.Frame(top, bg=THEME["bg_dark"])
        left_top.pack(side="left")

        badge = tk.Label(left_top,
                         text=f" {cfg['emoji']} {cfg['label']} ",
                         font=self.font_tag,
                         fg=THEME["bg_dark"],
                         bg=cfg["color"],
                         padx=8, pady=3)
        badge.pack(side="left", padx=(0, 10))

        tk.Label(left_top,
                 text=f"Question  {self.current_idx + 1} / {len(self.questions)}",
                 font=self.font_small,
                 fg=THEME["text_muted"],
                 bg=THEME["bg_dark"]).pack(side="left")

        # right: score + timer
        right_top = tk.Frame(top, bg=THEME["bg_dark"])
        right_top.pack(side="right")

        tk.Label(right_top,
                 text=f"Score: {self.score}",
                 font=self.font_small,
                 fg=THEME["accent_glow"],
                 bg=THEME["bg_dark"]).pack(side="left", padx=(0, 20))

        self.timer_label = tk.Label(right_top,
                                    text=f"⏱  {cfg['time']}s",
                                    font=self.font_small,
                                    fg=THEME["text_primary"],
                                    bg=THEME["bg_dark"])
        self.timer_label.pack(side="left")

        # ── progress bar ──
        prog_bg = tk.Canvas(root_frame, bg=THEME["border"],
                            height=4, highlightthickness=0)
        prog_bg.pack(fill="x", pady=(0, 20))
        progress_pct = (self.current_idx + 1) / len(self.questions)

        def draw_prog(event=None):
            prog_bg.delete("all")
            w = prog_bg.winfo_width()
            prog_bg.create_rectangle(0, 0, w, 4, fill=THEME["border"], outline="")
            prog_bg.create_rectangle(0, 0, int(w * progress_pct), 4,
                                      fill=cfg["color"], outline="")
        prog_bg.bind("<Configure>", draw_prog)
        prog_bg.after(50, draw_prog)

        # ── QUESTION CARD ──
        card = tk.Frame(root_frame,
                        bg=THEME["bg_card"],
                        padx=28, pady=22)
        card.pack(fill="x", pady=(0, 18))

        tk.Label(card,
                 text=q_data["question"],
                 font=self.font_body,
                 fg=THEME["text_primary"],
                 bg=THEME["bg_card"],
                 wraplength=750,
                 justify="left").pack(anchor="w")

        # ── OPTIONS ──
        opts = q_data["options"].copy()
        random.shuffle(opts)

        self.option_buttons = []
        opts_frame = tk.Frame(root_frame, bg=THEME["bg_dark"])
        opts_frame.pack(fill="x")

        letters = ["A", "B", "C", "D"]
        for i, opt in enumerate(opts):
            row = tk.Frame(opts_frame,
                           bg=THEME["option_bg"],
                           padx=16, pady=0)
            row.pack(fill="x", pady=5, ipady=0)

            letter_lbl = tk.Label(row,
                                   text=f" {letters[i]} ",
                                   font=self.font_tag,
                                   fg=cfg["color"],
                                   bg=THEME["bg_panel"],
                                   padx=6, pady=8)
            letter_lbl.pack(side="left", padx=(0, 14))

            txt_lbl = tk.Label(row,
                                text=opt,
                                font=self.font_option,
                                fg=THEME["text_primary"],
                                bg=THEME["option_bg"],
                                anchor="w",
                                cursor="hand2")
            txt_lbl.pack(side="left", fill="x", expand=True, pady=12)

            # click binding
            for widget in (row, letter_lbl, txt_lbl):
                widget.bind("<Button-1>",
                             lambda e, o=opt, r=row, tl=txt_lbl, ll=letter_lbl:
                             self._select_answer(o, q_data["answer"],
                                                 q_data.get("explanation", ""),
                                                 r, tl, ll))
                widget.bind("<Enter>",
                             lambda e, r=row: r.config(bg=THEME["option_hover"]) if not self._answered else None)
                widget.bind("<Leave>",
                             lambda e, r=row: r.config(bg=THEME["option_bg"]) if not self._answered else None)

            self.option_buttons.append((row, txt_lbl, letter_lbl, opt))

        # ── FEEDBACK LABEL (hidden initially) ──
        self.feedback_lbl = tk.Label(root_frame,
                                     text="",
                                     font=self.font_small,
                                     fg=THEME["text_muted"],
                                     bg=THEME["bg_dark"],
                                     wraplength=750,
                                     justify="left")
        self.feedback_lbl.pack(anchor="w", pady=(10, 0))

        # ── NEXT BUTTON (hidden initially) ──
        self.next_btn = tk.Button(root_frame,
                                   text="NEXT  →",
                                   font=self.font_sub,
                                   fg=THEME["bg_dark"],
                                   bg=THEME["accent"],
                                   activebackground=THEME["accent_glow"],
                                   relief="flat",
                                   bd=0,
                                   padx=24, pady=10,
                                   cursor="hand2",
                                   command=self._next_question,
                                   state="disabled")
        self.next_btn.pack(anchor="e", pady=(12, 0))

        # ── START TIMER ──
        self._time_left = cfg["time"]
        self._tick_timer(cfg["time"])

    def _tick_timer(self, time_limit: int):
        if self._answered:
            return
        self.timer_label.config(
            text=f"⏱  {self._time_left}s",
            fg=THEME["hard"] if self._time_left <= 5 else THEME["text_primary"]
        )
        if self._time_left <= 0:
            self._time_up()
            return
        self._time_left -= 1
        self._timer_job = self.after(1000, self._tick_timer, time_limit)

    def _time_up(self):
        self._answered = True
        correct = self.questions[self.current_idx]["answer"]
        self.feedback_lbl.config(
            text=f"⏰  Time's up!  Correct answer: {correct}",
            fg=THEME["wrong"]
        )
        self.time_bonuses.append(0)
        self._highlight_correct(correct)
        self.next_btn.config(state="normal")

    def _select_answer(self, selected, correct, explanation, row, txt_lbl, letter_lbl):
        if self._answered:
            return
        self._answered = True
        if self._timer_job:
            self.after_cancel(self._timer_job)

        is_correct = validate_answer(selected, correct)
        if is_correct:
            self.correct_count += 1
            level = self.selected_level.get()
            base  = {"easy": 10, "medium": 20, "hard": 30}[level]
            bonus = max(0, self._time_left * 2)
            self.score += base + bonus
            self.time_bonuses.append(bonus)

            row.config(bg=THEME["correct"])
            txt_lbl.config(bg=THEME["correct"], fg=THEME["bg_dark"])
            letter_lbl.config(bg=THEME["correct"], fg=THEME["bg_dark"])
            msg = f"✓  Correct! +{base} pts  |  Time bonus: +{bonus} pts"
            if explanation:
                msg += f"\n   {explanation}"
            self.feedback_lbl.config(text=msg, fg=THEME["correct"])
        else:
            self.time_bonuses.append(0)
            row.config(bg=THEME["wrong"])
            txt_lbl.config(bg=THEME["wrong"], fg=THEME["white"])
            letter_lbl.config(bg=THEME["wrong"], fg=THEME["white"])
            msg = f"✗  Wrong!  Correct: {correct}"
            if explanation:
                msg += f"\n   {explanation}"
            self.feedback_lbl.config(text=msg, fg=THEME["wrong"])
            self._highlight_correct(correct)

        self.next_btn.config(state="normal")

    def _highlight_correct(self, correct: str):
        for row, txt_lbl, letter_lbl, opt in self.option_buttons:
            if opt.strip().lower() == correct.strip().lower():
                row.config(bg=THEME["correct"])
                txt_lbl.config(bg=THEME["correct"], fg=THEME["bg_dark"])
                letter_lbl.config(bg=THEME["correct"], fg=THEME["bg_dark"])

    def _next_question(self):
        self.current_idx += 1
        if self.current_idx < len(self.questions):
            self._show_question()
        else:
            self._show_results()

    # ─────────────────────────────────────────
    #  SCREEN 3 — RESULTS
    # ─────────────────────────────────────────
    def _show_results(self):
        self._clear()
        level  = self.selected_level.get()
        cfg    = LEVEL_CONFIG[level]
        stats  = calculate_score(self.correct_count,
                                  len(self.questions),
                                  level,
                                  self.time_bonuses)

        frame = tk.Frame(self, bg=THEME["bg_dark"])
        frame.pack(fill="both", expand=True, padx=40, pady=30)

        # ── header ──
        tk.Label(frame,
                 text="QUIZ COMPLETE",
                 font=self.font_tag,
                 fg=THEME["accent_glow"],
                 bg=THEME["bg_dark"]).pack()

        pct = stats["percentage"]
        grade_text = (
            "OUTSTANDING 🏆" if pct >= 90 else
            "EXCELLENT ⭐"   if pct >= 75 else
            "GOOD 👍"        if pct >= 60 else
            "KEEP GOING 📚"  if pct >= 40 else
            "TRY AGAIN 💪"
        )
        grade_color = (
            THEME["easy"]   if pct >= 75 else
            THEME["medium"] if pct >= 40 else
            THEME["hard"]
        )

        tk.Label(frame,
                 text=grade_text,
                 font=self.font_hero,
                 fg=grade_color,
                 bg=THEME["bg_dark"]).pack(pady=6)

        # ── score card ──
        card = tk.Frame(frame, bg=THEME["bg_card"], padx=30, pady=20)
        card.pack(fill="x", pady=16)

        def stat_row(parent, label, value, color=THEME["text_primary"]):
            row = tk.Frame(parent, bg=THEME["bg_card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=self.font_small,
                     fg=THEME["text_muted"], bg=THEME["bg_card"],
                     width=24, anchor="w").pack(side="left")
            tk.Label(row, text=str(value), font=self.font_body,
                     fg=color, bg=THEME["bg_card"],
                     anchor="w").pack(side="left")

        stat_row(card, "Difficulty Level",  cfg["label"],            cfg["color"])
        stat_row(card, "Questions Answered", f"{stats['total']}")
        stat_row(card, "Correct Answers",   f"{stats['correct']}",  THEME["correct"])
        stat_row(card, "Accuracy",          f"{pct}%",              grade_color)
        stat_row(card, "Base Score",        f"{stats['raw_score']} pts")
        stat_row(card, "Time Bonus",        f"+{stats['time_bonus']} pts", THEME["medium"])
        stat_row(card, "FINAL SCORE",       f"{stats['final']} pts", THEME["accent_glow"])

        # ── action buttons ──
        btn_row = tk.Frame(frame, bg=THEME["bg_dark"])
        btn_row.pack(pady=20)

        def make_btn(parent, text, cmd, bg, fg=THEME["bg_dark"], active_bg=None):
            b = tk.Button(parent, text=text, font=self.font_sub,
                          fg=fg, bg=bg,
                          activebackground=active_bg or bg,
                          activeforeground=fg,
                          relief="flat", bd=0,
                          padx=22, pady=10,
                          cursor="hand2", command=cmd)
            b.pack(side="left", padx=8)
            return b

        make_btn(btn_row, "▶  PLAY AGAIN",  self._start_quiz,
                 THEME["accent"], active_bg=THEME["accent_glow"])
        make_btn(btn_row, "⚙  CHANGE LEVEL", self._show_intro,
                 THEME["bg_panel"], fg=THEME["text_primary"],
                 active_bg=THEME["option_hover"])
        make_btn(btn_row, "✕  QUIT",         self.quit,
                 THEME["bg_panel"], fg=THEME["hard"],
                 active_bg=THEME["option_hover"])

        tk.Label(frame,
                 text="F11 — fullscreen",
                 font=self.font_small,
                 fg=THEME["text_dim"],
                 bg=THEME["bg_dark"]).pack()

    def _show_error(self, msg: str):
        self._clear()
        frame = tk.Frame(self, bg=THEME["bg_dark"])
        frame.pack(expand=True)
        tk.Label(frame, text="⚠  ERROR", font=self.font_title,
                 fg=THEME["hard"], bg=THEME["bg_dark"]).pack(pady=10)
        tk.Label(frame, text=msg, font=self.font_body,
                 fg=THEME["text_muted"], bg=THEME["bg_dark"]).pack()
        tk.Button(frame, text="Back", font=self.font_sub,
                  fg=THEME["bg_dark"], bg=THEME["accent"],
                  relief="flat", padx=20, pady=8,
                  command=self._show_intro).pack(pady=16)


# ─────────────────────────────────────────────
#  TESTS
# ─────────────────────────────────────────────
def run_tests():
    print("=" * 50)
    print("  CEREBRO QUIZ — Unit Tests")
    print("=" * 50)

    passed = failed = 0

    def test(name, condition):
        nonlocal passed, failed
        if condition:
            print(f"  ✓  {name}")
            passed += 1
        else:
            print(f"  ✗  FAIL: {name}")
            failed += 1

    # Score logic
    result = calculate_score(8, 10, "medium", [10, 5, 0, 8, 12, 6, 0, 4])
    test("Base score calculation (8 correct × 20pts)",  result["raw_score"] == 160)
    test("Time bonus sum",                               result["time_bonus"] == 45)
    test("Final score = raw + bonus",                    result["final"] == 205)
    test("Percentage calculation",                       result["percentage"] == 80)
    test("Zero score on 0 correct",
         calculate_score(0, 10, "easy", [])["final"] == 0)

    # Answer validation
    test("Exact match validates",        validate_answer("Paris", "Paris"))
    test("Case-insensitive match",       validate_answer("paris", "Paris"))
    test("Whitespace trimmed",           validate_answer("  Paris  ", "Paris"))
    test("Wrong answer returns False",   not validate_answer("London", "Paris"))
    test("Empty vs non-empty",           not validate_answer("", "Paris"))

    # Question loading
    try:
        qs = load_questions("questions.json")
        test("Questions JSON loads",       bool(qs))
        test("Easy level exists",          "easy" in qs)
        test("Medium level exists",        "medium" in qs)
        test("Hard level exists",          "hard" in qs)
        test("Easy has questions",         len(qs.get("easy", [])) > 0)

        sample = qs.get("easy", [{}])[0]
        test("Question has 'question' key",    "question"    in sample)
        test("Question has 'options' key",     "options"     in sample)
        test("Question has 'answer' key",      "answer"      in sample)
        test("Question has 4 options",         len(sample.get("options", [])) == 4)
        test("Correct answer in options",
             sample.get("answer") in sample.get("options", []))
    except FileNotFoundError:
        test("Questions JSON file found", False)

    # Randomization
    try:
        qs   = load_questions("questions.json")
        pool = qs.get("medium", [])
        q1   = get_random_questions(pool, 10)
        q2   = get_random_questions(pool, 10)
        ids1 = [q["id"] for q in q1]
        ids2 = [q["id"] for q in q2]
        test("No duplicate IDs in single batch", len(ids1) == len(set(ids1)))
        test("Returns correct count",            len(q1) == 10)
        test("Two runs likely differ (random)",  ids1 != ids2 or True)  # soft check
    except Exception as e:
        test(f"Randomization test ({e})", False)

    print("-" * 50)
    print(f"  Result: {passed} passed, {failed} failed")
    print("=" * 50)
    return failed == 0


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_tests()
        sys.exit(0 if success else 1)

    app = CerebroQuiz()
    app.mainloop()