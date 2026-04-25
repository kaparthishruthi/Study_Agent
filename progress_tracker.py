import json
from database import get_conn
from datetime import datetime

def _now():
    return datetime.now().isoformat()

def _parse_date(s):
    if not s:
        return datetime.now()
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return datetime.now()

# ── Progress / activity ──

def save_progress(username: str, topic: str):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO progress (username, topic, date) VALUES (?, ?, ?)",
            (username, topic, _now())
        )
        conn.commit()
    finally:
        conn.close()

def get_progress(username: str):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT username, topic, date FROM progress WHERE username = ? ORDER BY date DESC",
            (username,)
        ).fetchall()
        return [{"username": r["username"], "topic": r["topic"], "date": _parse_date(r["date"])} for r in rows]
    finally:
        conn.close()

# ── Quiz scores ──

def save_quiz_score(username: str, topic: str, score: int, total: int, difficulty: str):
    pct = round((score / total) * 100, 1) if total else 0
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO scores (username, topic, score, total, percentage, difficulty, date) VALUES (?,?,?,?,?,?,?)",
            (username, topic, score, total, pct, difficulty, _now())
        )
        conn.commit()
    finally:
        conn.close()

def get_quiz_scores(username: str):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM scores WHERE username = ? ORDER BY date DESC",
            (username,)
        ).fetchall()
        return [
            {
                "username": r["username"],
                "topic": r["topic"],
                "score": r["score"],
                "total": r["total"],
                "percentage": r["percentage"],
                "difficulty": r["difficulty"],
                "date": _parse_date(r["date"]),
            }
            for r in rows
        ]
    finally:
        conn.close()

def get_all_scores(username: str):
    scores = get_quiz_scores(username)
    if not scores:
        return {"total_quizzes": 0, "avg_score": 0, "best_score": 0, "topics_studied": [], "recent_scores": []}
    total_quizzes  = len(scores)
    avg_score      = round(sum(s["percentage"] for s in scores) / total_quizzes, 1)
    best_score     = max(s["percentage"] for s in scores)
    topics_studied = list(set(s["topic"] for s in scores))
    return {
        "total_quizzes": total_quizzes,
        "avg_score": avg_score,
        "best_score": best_score,
        "topics_studied": topics_studied,
        "recent_scores": scores[:5],
    }

# ── Saved quizzes ──

def save_quiz(username: str, topic: str, difficulty: str, questions: list, score: int, total: int, time_taken: int):
    pct = round((score / total) * 100, 1) if total else 0
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO saved_quizzes (username, topic, difficulty, questions, score, total, percentage, time_taken, date) VALUES (?,?,?,?,?,?,?,?,?)",
            (username, topic, difficulty, json.dumps(questions), score, total, pct, time_taken, _now())
        )
        conn.commit()
    finally:
        conn.close()

def get_saved_quizzes(username: str):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM saved_quizzes WHERE username = ? ORDER BY date DESC",
            (username,)
        ).fetchall()
        result = []
        for r in rows:
            try:
                questions = json.loads(r["questions"]) if r["questions"] else []
            except Exception:
                questions = []
            result.append({
                "username":   r["username"],
                "topic":      r["topic"],
                "difficulty": r["difficulty"],
                "questions":  questions,
                "score":      r["score"],
                "total":      r["total"],
                "percentage": r["percentage"],
                "time_taken": r["time_taken"],
                "date":       _parse_date(r["date"]),
            })
        return result
    finally:
        conn.close()

# ── Saved plans ──

def save_plan(username: str, subjects: str, exam_date: str, hours: int, plan_text: str):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO saved_plans (username, subjects, exam_date, hours, plan, date) VALUES (?,?,?,?,?,?)",
            (username, subjects, exam_date, hours, plan_text, _now())
        )
        conn.commit()
    finally:
        conn.close()

def get_saved_plans(username: str):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM saved_plans WHERE username = ? ORDER BY date DESC",
            (username,)
        ).fetchall()
        return [
            {
                "username":  r["username"],
                "subjects":  r["subjects"],
                "exam_date": r["exam_date"],
                "hours":     r["hours"],
                "plan":      r["plan"],
                "date":      _parse_date(r["date"]),
            }
            for r in rows
        ]
    finally:
        conn.close()
