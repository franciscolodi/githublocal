import sqlite3

def check_login(username,password):

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
    )

    result = c.fetchone()
    conn.close()

    return result
