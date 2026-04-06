import sqlite3

def get_connection():
    return sqlite3.connect("ev_app.db", check_same_thread=False)

def register_user(email, password):
    conn = get_connection()
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS users (email TEXT, password TEXT)")
    
    # Check user exists
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    if c.fetchone():
        return False

    c.execute("INSERT INTO users VALUES (?, ?)", (email, password))
    conn.commit()
    conn.close()
    return True


def login_user(email, password):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()

    return user  # returns None or data