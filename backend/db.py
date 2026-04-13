import sqlite3
import hashlib

# ---------- HASH PASSWORD ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------- CREATE TABLE ----------
def create_table():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

# ---------- REGISTER ----------
def register_user(username, email, password):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # check if email exists
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        conn.close()
        return "exists"

    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, password)
    )

    conn.commit()
    conn.close()

    return "success"

# ---------- LOGIN ----------
def login_user(email, password):   # ✅ correct

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, email, password FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cursor.fetchone()
    conn.close()

    return user