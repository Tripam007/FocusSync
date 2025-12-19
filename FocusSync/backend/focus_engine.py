import math
from datetime import datetime, timedelta

# Default base durations (minutes)
BASE_FOCUS = 25
BASE_BREAK = 5

def calculate_focus_duration(task_difficulty: int, avg_distractions: float = 0) -> int:
    """
    Adaptive focus duration:
    - Harder tasks → longer focus (up to 50 min)
    - More distractions → shorter focus (encourage recovery)
    """
    # Normalize difficulty (1–5 → 0.8 to 1.6 multiplier)
    difficulty_factor = 0.8 + (task_difficulty / 5) * 0.8
    distraction_penalty = max(0.5, 1.0 - (avg_distractions * 0.1))
    duration = BASE_FOCUS * difficulty_factor * distraction_penalty
    return min(50, max(10, round(duration)))

def calculate_break_duration(focus_duration: int) -> int:
    return min(15, max(2, round(focus_duration / 5)))

def calculate_focus_score(duration: int, distractions: int, completed: bool) -> int:
    base = min(100, duration)
    penalty = distractions * 10
    bonus = 10 if completed else 0
    score = max(0, base - penalty + bonus)
    return int(score)

def get_avg_distractions():
    import sqlite3
    conn = sqlite3.connect("focus_sync.db")
    cur = conn.cursor()
    cur.execute("SELECT AVG(distractions) FROM sessions WHERE completed = 1")
    avg = cur.fetchone()[0]
    conn.close()
    return avg if avg is not None else 0.0