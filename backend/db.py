import sqlite3

# ---------- CONNECTION ----------
def get_connection():
    return sqlite3.connect("ev_app.db", check_same_thread=False)

# ---------- CREATE TABLE ----------
def create_table():
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
    create_table()   # 🔥 IMPORTANT

    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# ---------- LOGIN ----------
def login_user(email, password):
    create_table()   # 🔥 IMPORTANT

    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()

    conn.close()

    return user