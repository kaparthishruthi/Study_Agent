import hashlib
from database import get_conn
from datetime import datetime

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username: str, password: str, email: str) -> dict:
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        if c.fetchone():
            return {"success": False, "message": "Username already exists."}
        c.execute("SELECT id FROM users WHERE email = ?", (email,))
        if c.fetchone():
            return {"success": False, "message": "Email already registered."}
        c.execute(
            "INSERT INTO users (username, password, email, created_at) VALUES (?, ?, ?, ?)",
            (username, hash_password(password), email, datetime.now().isoformat())
        )
        conn.commit()
        return {"success": True, "message": "Account created successfully!"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

def login_user(username: str, password: str) -> dict:
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if not user:
            return {"success": False, "message": "Username not found."}
        if user["password"] != hash_password(password):
            return {"success": False, "message": "Incorrect password."}
        return {"success": True, "message": "Login successful!", "username": username}
    finally:
        conn.close()
