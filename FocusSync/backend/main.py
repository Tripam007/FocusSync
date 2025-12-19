from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import sqlite3
from datetime import datetime
from models import SessionCreate, SessionUpdate
from focus_engine import (
    calculate_focus_duration,
    calculate_break_duration,
    calculate_focus_score,
    get_avg_distractions,
)
from database import init_db
import os

app = FastAPI(title="FocusSync API", description="Hackathon MVP for adaptive focus timer")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

@app.post("/api/session/start")
def start_session(data: SessionCreate):
    if not (1 <= data.task_difficulty <= 5):
        raise HTTPException(400, "Task difficulty must be 1–5")
    
    avg_dist = get_avg_distractions()
    focus_min = calculate_focus_duration(data.task_difficulty, avg_dist)
    break_min = calculate_break_duration(focus_min)

    conn = sqlite3.connect("focus_sync.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (start_time, task_difficulty) VALUES (?, ?)",
        (datetime.now().isoformat(), data.task_difficulty)
    )
    session_id = cur.lastrowid
    conn.commit()
    conn.close()

    return {
        "session_id": session_id,
        "focus_minutes": focus_min,
        "break_minutes": break_min
    }

@app.put("/api/session/{session_id}/end")
def end_session(session_id: int, data: SessionUpdate):
    conn = sqlite3.connect("focus_sync.db")
    cur = conn.cursor()
    cur.execute("SELECT start_time FROM sessions WHERE id = ?", (session_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(404, "Session not found")
    
    start_time = datetime.fromisoformat(row[0])
    duration_sec = (datetime.now() - start_time).total_seconds()
    duration_min = round(duration_sec / 60)

    focus_score = calculate_focus_score(duration_min, data.distractions, data.completed)

    cur.execute("""
        UPDATE sessions
        SET end_time = ?, duration = ?, distractions = ?, completed = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), duration_min, data.distractions, data.completed, session_id))
    conn.commit()
    conn.close()

    return {"session_id": session_id, "focus_score": focus_score, "duration_min": duration_min}

@app.get("/api/stats")
def get_stats():
    conn = sqlite3.connect("focus_sync.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            AVG(duration) as avg_duration,
            AVG(distractions) as avg_distractions,
            AVG(CASE WHEN completed THEN 1 ELSE 0 END) * 100 as completion_rate
        FROM sessions WHERE completed = 1
    """)
    row = cur.fetchone()
    conn.close()
    if not row or not row[0]:
        return {"message": "No completed sessions yet"}
    return {
        "total_sessions": row[0],
        "avg_duration_min": round(row[1] or 0, 1),
        "avg_distractions": round(row[2] or 0, 1),
        "completion_rate_percent": round(row[3] or 0, 1)
    }

# Serve frontend
@app.get("/")
def serve_frontend():
    return FileResponse("../frontend/index.html")