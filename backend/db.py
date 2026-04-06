import sqlite3

# Connect DB
def connect_db():
    return sqlite3.connect("chat.db", check_same_thread=False)


# ---------------- USERS TABLE ----------------
def create_users_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


def register_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()
    return user


# ---------------- CHAT TABLE ----------------
def create_chat_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_chat(question, answer):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO chats (question, answer) VALUES (?, ?)",
        (question, answer)
    )

    conn.commit()
    conn.close()


def get_chats():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT question, answer FROM chats")
    data = cursor.fetchall()

    conn.close()
    return data


# Initialize tables
create_users_table()
create_chat_table()