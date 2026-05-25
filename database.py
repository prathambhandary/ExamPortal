import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "nextgen.db"


def create_tables():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Enable foreign key constraint support in SQLite
    c.execute("PRAGMA foreign_keys = ON;")

    # 1. BATCHES TABLE
    c.execute('''CREATE TABLE IF NOT EXISTS batches (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              batch_name TEXT NOT NULL UNIQUE,
              course TEXT NOT NULL,
              year INTEGER NOT NULL
        )''')

    # 2. CORE USERS TABLE (Authentication)
    c.execute('''CREATE TABLE IF NOT EXISTS login (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              password TEXT NOT NULL,
              role TEXT NOT NULL DEFAULT 'student'
        )''')

    # 3. STUDENT PROFILES TABLE (Extended Meta Data)
    c.execute('''CREATE TABLE IF NOT EXISTS student_profiles (
              user_id INTEGER PRIMARY KEY,
              first_name TEXT NOT NULL,
              last_name TEXT,
              roll_number TEXT NOT NULL UNIQUE,
              batch_id INTEGER,
              email TEXT UNIQUE,
              student_phone TEXT,
              parent_phone TEXT,
              stream TEXT NOT NULL,
              target_year INTEGER,
              access INTEGER DEFAULT 1,
              FOREIGN KEY (user_id) REFERENCES login(id) ON DELETE CASCADE,
              FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE SET NULL
        )''')

    # 4. EXAMS TABLE (Test Configuration)
    c.execute('''CREATE TABLE IF NOT EXISTS exams (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              test_name TEXT NOT NULL UNIQUE,
              category TEXT NOT NULL,
              duration_minutes INTEGER NOT NULL,
              total_marks INTEGER NOT NULL,
              start_time TIMESTAMP NOT NULL,
              end_time TIMESTAMP NOT NULL,
              is_active INTEGER DEFAULT 0,
              shuffle_questions INTEGER DEFAULT 0
        )''')

    # 5. QUESTIONS TABLE (Master Question Bank)
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              subject TEXT NOT NULL,
              chapter TEXT NOT NULL,
              question_type TEXT NOT NULL, 
              difficulty TEXT DEFAULT 'Medium',
              question_text TEXT NOT NULL, 
              option_a TEXT,
              option_b TEXT,
              option_c TEXT,
              option_d TEXT,
              correct_answer TEXT NOT NULL,
              positive_marks INTEGER DEFAULT 4,
              negative_marks INTEGER DEFAULT 1,
              explanation TEXT
        )''')

    # 6. EXAM BATCHES BRIDGE TABLE (Targeting Control)
    c.execute('''CREATE TABLE IF NOT EXISTS exam_batches (
              exam_id INTEGER,
              batch_id INTEGER,
              PRIMARY KEY (exam_id, batch_id),
              FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
              FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
        )''')

    # 7. EXAM QUESTIONS BRIDGE TABLE (The Playlist Compiler)
    c.execute('''CREATE TABLE IF NOT EXISTS exam_questions (
              exam_id INTEGER,
              question_id INTEGER,
              section_name TEXT NOT NULL,
              sequence_number INTEGER NOT NULL,
              PRIMARY KEY (exam_id, question_id),
              FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
              FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        )''')

    # 8. STUDENT RESPONSES TABLE (Real-Time Live State Tracking)
    c.execute('''CREATE TABLE IF NOT EXISTS student_responses (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              exam_id INTEGER NOT NULL,
              question_id INTEGER NOT NULL,
              selected_answer TEXT,
              status TEXT DEFAULT 'Not Visited',
              timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              UNIQUE(user_id, exam_id, question_id),
              FOREIGN KEY (user_id) REFERENCES login(id) ON DELETE CASCADE,
              FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
              FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        )''')

    # 9. EXAM ATTEMPTS TABLE (Master Ledger & Ledger Processing)
    c.execute('''CREATE TABLE IF NOT EXISTS exam_attempts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              exam_id INTEGER NOT NULL,
              start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              submit_time TIMESTAMP,
              total_score INTEGER DEFAULT 0,
              correct_count INTEGER DEFAULT 0,
              incorrect_count INTEGER DEFAULT 0,
              status TEXT DEFAULT 'Ongoing',
              UNIQUE(user_id, exam_id),
              FOREIGN KEY (user_id) REFERENCES login(id) ON DELETE CASCADE,
              FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
        )''')

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

def delete_user(username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM login WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def add_batch(batch_name, course, year):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    try:
        c.execute("INSERT INTO batches (batch_name, course, year) VALUES (?, ?, ?)", (batch_name, course, year))
        conn.commit()
        return [True, "Batch added successfully"]
    except sqlite3.IntegrityError:
        return [False, "Batch name already exists"]
    except sqlite3.Error as e:
        return [False, str(e)]
    finally:
        conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully.")