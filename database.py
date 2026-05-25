import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "nextgen.db"


def create_tables():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def login_user(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password, role FROM login WHERE username = ?",
        (username,)
    )

    result = cursor.fetchone()

    conn.close()

    if not result:
        return [False, None]

    is_valid = check_password_hash(result[0], password)

    return [is_valid, result[1]]


def add_user(username, password, role):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    hashed_password = generate_password_hash(password)

    try:
        cursor.execute(
            "INSERT INTO login (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_password, role)
        )

        conn.commit()

        return [True, "User added successfully"]

    except sqlite3.IntegrityError:
        return [False, "Username already exists"]

    except sqlite3.Error as e:
        return [False, str(e)]

    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")