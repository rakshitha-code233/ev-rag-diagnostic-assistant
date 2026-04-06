import sqlite3

# ---------- CONNECTION ----------
def get_connection():
    return sqlite3.connect("ev_app.db", check_same_thread=False)

# ---------- USER TABLE ----------
def create_user_table():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

# ---------- SIGNUP ----------
def register_user(email, password):
    create_user_table()

    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (email, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# ---------- LOGIN ----------
def login_user(email, password):
    create_user_table()

    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()

    conn.close()
    return user

# ---------- KNOWLEDGE ----------
def create_knowledge_table():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            question TEXT PRIMARY KEY,
            answer TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_knowledge(question, answer):
    create_knowledge_table()

    conn = get_connection()
    c = conn.cursor()

    c.execute("INSERT OR REPLACE INTO knowledge VALUES (?, ?)", (question.lower(), answer))
    conn.commit()
    conn.close()

def get_knowledge(question):
    create_knowledge_table()

    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT answer FROM knowledge WHERE question=?", (question.lower(),))
    data = c.fetchone()

    conn.close()
    return data[0] if data else None