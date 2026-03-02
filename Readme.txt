╔══════════════════════════════════════════════════════════════╗
║              CEREBRO — Aesthetic Tkinter Quiz App            ║
╚══════════════════════════════════════════════════════════════╝

QUICK START
───────────
1. Make sure both files are in the SAME folder:
      cerebro_quiz.py
      questions.json

2. Run the app:
      python cerebro_quiz.py

3. Run unit tests:
      python cerebro_quiz.py --test


REQUIREMENTS
────────────
  Python 3.8+   (tkinter is included in standard Python installs)
  No pip packages needed.

  On Linux, if tkinter is missing:
      sudo apt install python3-tk


FEATURES
────────
  ✓ Aesthetic dark UI with Courier New monospace font
  ✓ Animated decorative background (grid lines + glow orbs)
  ✓ 3 difficulty levels: Easy 🌱 | Medium ⚡ | Hard 🔥
  ✓ 15 questions per level (10 randomly chosen each game)
  ✓ No repeated questions within a single game session
  ✓ Options are shuffled randomly each question
  ✓ Countdown timer per question (Easy=30s, Medium=20s, Hard=15s)
  ✓ Time bonus scoring: faster answers = more points
  ✓ Answer explanation shown after each question
  ✓ Fullscreen mode: press F11 to toggle, ESC to exit
  ✓ Detailed results screen with grade, accuracy, score breakdown
  ✓ Play again / Change level / Quit buttons

SCORING SYSTEM
──────────────
  Easy   →  10 pts per correct + time_remaining × 2 bonus pts
  Medium →  20 pts per correct + time_remaining × 2 bonus pts
  Hard   →  30 pts per correct + time_remaining × 2 bonus pts

  Grades:
    90–100% → OUTSTANDING 🏆
    75–89%  → EXCELLENT ⭐
    60–74%  → GOOD 👍
    40–59%  → KEEP GOING 📚
    0–39%   → TRY AGAIN 💪

KEYBOARD SHORTCUTS
──────────────────
  F11    Toggle fullscreen
  ESC    Exit fullscreen

TESTS COVERED
─────────────
  ✓ Score logic (base + time bonus + final)
  ✓ Percentage calculation
  ✓ Answer validation (case-insensitive, whitespace trimmed)
  ✓ Question JSON loading and structure
  ✓ Randomization (no repeats, correct count)

FILE STRUCTURE
──────────────
  cerebro_quiz.py    Main application + all logic + unit tests
  questions.json     Question bank (15 per level × 3 levels = 45 total)
  README.txt         This file