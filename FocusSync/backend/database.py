import sqlite3
import os

DB_PATH = "focus_sync.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            duration INTEGER,
            distractions INTEGER DEFAULT 0,
            task_difficulty INTEGER CHECK(task_difficulty BETWEEN 1 AND 5),
            completed BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()