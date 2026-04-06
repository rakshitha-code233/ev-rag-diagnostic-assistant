import sqlite3

# ---------------- CONNECT ----------------
def connect_db():
    return sqlite3.connect("database.db")


# ---------------- CREATE TABLES ----------------
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    # Chat history
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- USER FUNCTIONS ----------------
def register_user(username, password):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()
        return True
    except:
        return False


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


# ---------------- CHAT FUNCTIONS ----------------
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


# ---------------- CUSTOM KNOWLEDGE ----------------
def save_knowledge(question, answer):
    save_chat(question, answer)


def search_knowledge(query):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT answer FROM chats WHERE question LIKE ?",
        ('%' + query + '%',)
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


# ---------------- INIT ----------------
create_tables()