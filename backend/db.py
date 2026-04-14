import sqlite3
import bcrypt

DB_NAME = "users.db"
def create_table():
    import sqlite3

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()
# ---------------- INIT TABLE ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# ---------------- REGISTER USER ----------------
def register_user(username, email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        conn.close()
        return "exists"

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, hashed_pw)
    )

    conn.commit()
    conn.close()
    return "success"


# ---------------- LOGIN USER ----------------
def login_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, email, password FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        user_id, username, email_db, hashed_pw = user

        if bcrypt.checkpw(password.encode(), hashed_pw):
            return {
                "id": user_id,
                "username": username,
                "email": email_db
            }

    return None