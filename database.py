import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash 

DATABASE = "nextgen.db"

def create_tables():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS login (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              password TEXT NOT NULL,
              role TEXT NOT NULL,
              last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT password FROM login WHERE username = ?", (username,))

    result = c.fetchone()
    conn.close()
    if result:
        return check_password_hash(result[0], password)
    return False

if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")