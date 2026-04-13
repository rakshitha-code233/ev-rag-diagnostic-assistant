import sqlite3
import bcrypt

# ---------------- CREATE TABLE ----------------
def create_table():
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


# ---------------- REGISTER (HASH PASSWORD) ----------------
def register_user(username, email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    email = email.strip()

    # check if user exists
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        conn.close()
        return "exists"

    # 🔐 HASH PASSWORD
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        (username, email, hashed_pw)
    )

    conn.commit()
    conn.close()

    return "success"


# ---------------- LOGIN (VERIFY HASH) ----------------
def login_user(email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    email = email.strip()

    cursor.execute(
        "SELECT id, username, email, password FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        user_id, username, email, hashed_pw = user

        # 🔐 CHECK HASHED PASSWORD
        if bcrypt.checkpw(password.encode('utf-8'), hashed_pw):
            return user

    return None