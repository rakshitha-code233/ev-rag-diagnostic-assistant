import sqlite3

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


# ---------------- REGISTER USER ----------------
def register_user(username, email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    create_table()  # ✅ Ensure table exists

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        conn.commit()
        conn.close()
        return "success"
    except sqlite3.IntegrityError:
        conn.close()
        return "exists"


# ---------------- LOGIN USER ----------------
def login_user(email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    create_table()  # ✅ Ensure table exists

    cursor.execute(
        "SELECT id, username, email FROM users WHERE email=? AND password=?",
        (email, password)
    )

    user = cursor.fetchone()
    conn.close()

    return user