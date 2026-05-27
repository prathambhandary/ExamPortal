import sqlite3
# from fastapi import params
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "nextgen.db"

def create_tables():
    conn = get_connection()
    c = conn.cursor()

    c.execute("PRAGMA foreign_keys = ON;")

    c.execute('''CREATE TABLE IF NOT EXISTS batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_name TEXT NOT NULL UNIQUE,
        course TEXT NOT NULL,
        year INTEGER NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS login (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

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
        gender TEXT,
        FOREIGN KEY (user_id) REFERENCES login(id) ON DELETE CASCADE,
        FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE SET NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS staff_profiles (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        department TEXT,
        designation TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES login(id) ON DELETE CASCADE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT UNIQUE NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        permission_name TEXT UNIQUE NOT NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS role_permissions (
        role_id INTEGER,
        permission_id INTEGER,
        PRIMARY KEY(role_id, permission_id),
        FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE CASCADE,
        FOREIGN KEY(permission_id) REFERENCES permissions(id) ON DELETE CASCADE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_roles (
        user_id INTEGER,
        role_id INTEGER,
        PRIMARY KEY(user_id, role_id),
        FOREIGN KEY(user_id) REFERENCES login(id) ON DELETE CASCADE,
        FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE CASCADE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS access_control (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        can_create_exam INTEGER DEFAULT 1,
        can_edit_exam INTEGER DEFAULT 1,
        can_delete_exam INTEGER DEFAULT 1,
        can_publish_exam INTEGER DEFAULT 1,
        can_manage_students INTEGER DEFAULT 1,
        can_manage_staff INTEGER DEFAULT 1,
        can_view_results INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES login(id) ON DELETE CASCADE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        target TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES login(id) ON DELETE SET NULL
    )''')

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
        explanation TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(created_by) REFERENCES login(id) ON DELETE SET NULL
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS exam_batches (
        exam_id INTEGER,
        batch_id INTEGER,
        PRIMARY KEY (exam_id, batch_id),
        FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
        FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS exam_questions (
        exam_id INTEGER,
        question_id INTEGER,
        section_name TEXT NOT NULL,
        sequence_number INTEGER NOT NULL,
        PRIMARY KEY (exam_id, question_id),
        FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
    )''')

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

    c.execute('''CREATE TABLE IF NOT EXISTS login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        ip_address TEXT,
        user_agent TEXT,
        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        success INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES login(id) ON DELETE CASCADE
    )''')

    conn.commit()
    conn.close()

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_indexes():
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
        CREATE INDEX IF NOT EXISTS idx_login_username
        ON login(username);

        CREATE INDEX IF NOT EXISTS idx_student_first_name
        ON student_profiles(first_name);

        CREATE INDEX IF NOT EXISTS idx_student_last_name
        ON student_profiles(last_name);

        CREATE INDEX IF NOT EXISTS idx_student_roll_number
        ON student_profiles(roll_number);

        CREATE INDEX IF NOT EXISTS idx_student_stream
        ON student_profiles(stream);

        CREATE INDEX IF NOT EXISTS idx_student_target_year
        ON student_profiles(target_year);

        CREATE INDEX IF NOT EXISTS idx_student_access
        ON student_profiles(access);

        CREATE INDEX IF NOT EXISTS idx_batches_name
        ON batches(batch_name);
                    
        CREATE INDEX IF NOT EXISTS idx_student_email
        ON student_profiles(email);

        CREATE INDEX IF NOT EXISTS idx_student_batch_id
        ON student_profiles(batch_id);

        CREATE INDEX IF NOT EXISTS idx_login_role
        ON login(role);

        CREATE INDEX IF NOT EXISTS idx_exam_attempts_user_exam
        ON exam_attempts(user_id, exam_id);

        CREATE INDEX IF NOT EXISTS idx_student_responses_user_exam
        ON student_responses(user_id, exam_id);
    """)

    conn.commit()
    conn.close()

def get_student_profile(username):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT 
            login.username,
            student_profiles.first_name,
            student_profiles.last_name,
            student_profiles.roll_number,
            student_profiles.email,
            student_profiles.student_phone,
            student_profiles.parent_phone,
            student_profiles.stream,
            student_profiles.target_year,
            student_profiles.gender,
            student_profiles.access,
            batches.batch_name
        FROM login
        JOIN student_profiles
        ON login.id = student_profiles.user_id
        LEFT JOIN batches
        ON batches.id = student_profiles.batch_id
        WHERE login.username = ?
    """, (username,))

    row = c.fetchone()
    conn.close()

    data = dict(row) if row else None
    if data:
        data['batch_name'] = get_batch_name(data.pop('batch_id'))

    return data

def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT password, role
        FROM login
        WHERE username = ?
    """, (username,))

    result = c.fetchone()

    if not result:
        conn.close()
        return [False, None]

    stored_password, role = result
    is_valid = check_password_hash(stored_password, password)

    data = None

    if role == "student":
        data = get_student_profile(username)

    conn.close()

    return [is_valid, role, data]

def add_user(username, password, role):
    conn = get_connection()
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
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM login WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def add_batch(batch_name, course, year):
    conn = get_connection()
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

def all_batches():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT batch_name, course, year FROM batches")
    
    rows = c.fetchall()

    batches = []
    
    for row in rows:
        batches.append({
            "batch_name": row["batch_name"],
            "course": row["course"],
            "year": row["year"]
        })

    conn.close()

    return batches

def all_streams():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT DISTINCT stream FROM student_profiles WHERE stream IS NOT NULL")

    rows = c.fetchall()

    streams = []
    
    for row in rows:
        streams.append({
            "stream": row["stream"]
        })

    conn.close()

    return streams

def get_batch_id(batch_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM batches WHERE batch_name = ?", (batch_name,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_batch_name(batch_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT batch_name FROM batches WHERE id = ?", (batch_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def add_student(
    username,
    password,
    first_name,
    last_name,
    roll_number,
    batch_name,
    email,
    student_phone,
    parent_phone,
    stream,
    target_year,
    gender
):
    conn = get_connection()

    try:
        c = conn.cursor()

        # STEP 1: CREATE LOGIN ACCOUNT

        password_hash = generate_password_hash(password)

        c.execute("""
            INSERT INTO login (username, password, role)
            VALUES (?, ?, ?)
        """, (username, password_hash, "student"))

        # GET GENERATED USER ID
        user_id = c.lastrowid

        # STEP 2: CREATE STUDENT PROFILE
        c.execute("""
            INSERT INTO student_profiles (
                user_id,
                first_name,
                last_name,
                roll_number,
                batch_id,
                email,
                student_phone,
                parent_phone,
                stream,
                target_year,
                gender
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            first_name,
            last_name,
            roll_number,
            get_batch_id(batch_name),
            email,
            student_phone,
            parent_phone,
            stream,
            target_year,
            gender
        ))

        conn.commit()

        return True, "Student added successfully"

    except sqlite3.IntegrityError as e:
        conn.rollback()

        return False, f"Integrity Error: {str(e)}"

    except Exception as e:
        conn.rollback()

        return False, f"Error: {str(e)}"

    finally:
        conn.close()

def ensure_gender_column():
    conn = get_connection()
    c = conn.cursor()

    c.execute("PRAGMA table_info(student_profiles)")
    
    if "gender" not in [col[1] for col in c.fetchall()]:
        c.execute("ALTER TABLE student_profiles ADD COLUMN gender TEXT")
        conn.commit()

    conn.close()

def clear_table(table_name):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute(f"DELETE FROM {table_name}")
        conn.commit()
        return True, f"{table_name} cleared successfully"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_login_table():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT id, username, role
        FROM login
    """)

    rows = [dict(row) for row in c.fetchall()]

    conn.close()

    return rows

def revoke_access(username):
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("""
            UPDATE student_profiles
            SET access = 0
            WHERE user_id = (
                SELECT id
                FROM login
                WHERE username = ?
            )
        """, (username,))

        conn.commit()

        if c.rowcount == 0:
            return False, "User not found"

        return True, "Access revoked successfully"

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        conn.close()

def grant_access(username):
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("""
            UPDATE student_profiles
            SET access = 1
            WHERE user_id = (
                SELECT id
                FROM login
                WHERE username = ?
            )
        """, (username,))

        conn.commit()

        if c.rowcount == 0:
            return False, "User not found"

        return True, "Access granted successfully"

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        conn.close()

def all():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT batch_name, course, year
        FROM batches
    """)

    batches = [dict(row) for row in c.fetchall()]

    c.execute("""
        SELECT
            login.username,
            student_profiles.first_name,
            student_profiles.last_name,
            student_profiles.roll_number,
            batches.batch_name,
            student_profiles.email,
            student_profiles.student_phone,
            student_profiles.parent_phone,
            student_profiles.stream,
            student_profiles.target_year,
            student_profiles.access,
            student_profiles.gender
        FROM login
        JOIN student_profiles
        ON login.id = student_profiles.user_id
        LEFT JOIN batches
        ON batches.id = student_profiles.batch_id
    """)

    students = [dict(row) for row in c.fetchall()]

    conn.close()

    return {
        "batches": batches,
        "students": students
    }

def all_students(
    search="",
    batch_name=None,
    batch_list=None,
    stream=None,
    stream_list=None,
    target_year=None,
    min_year=None,
    max_year=None,
    access=None,
    first_name=None,
    last_name=None,
    username=None,
    roll_number=None,
    sort_by="username",
    sort_order="asc",
    limit=10,
    offset=0
):
    conn = get_connection()
    c = conn.cursor()

    query = """
        SELECT 
            login.username,
            student_profiles.first_name,
            student_profiles.last_name,
            student_profiles.roll_number,
            batches.batch_name,
            student_profiles.email,
            student_profiles.student_phone,
            student_profiles.parent_phone,
            student_profiles.stream,
            student_profiles.target_year,
            student_profiles.access,
            student_profiles.gender
        FROM student_profiles
        JOIN login ON login.id = student_profiles.user_id
        LEFT JOIN batches ON batches.id = student_profiles.batch_id
        WHERE 1=1
    """

    params = []

    # -----------------------
    # SEARCH (case-insensitive partial match)
    # -----------------------
    if search:
        like = f"%{search.lower()}%"
        query += """
            AND (
                LOWER(login.username) LIKE ?
                OR LOWER(student_profiles.first_name) LIKE ?
                OR LOWER(student_profiles.last_name) LIKE ?
                OR LOWER(student_profiles.roll_number) LIKE ?
                OR LOWER(student_profiles.email) LIKE ?
                OR LOWER(student_profiles.student_phone) LIKE ?
            )
        """
        params.extend([like] * 6)

    # -----------------------
    # EXACT FILTERS
    # -----------------------
    def like(v):
        return f"%{v.lower()}%"
    
    if username:
        query += " AND LOWER(login.username) LIKE ?"
        params.append(like(username))

    if first_name:
        query += " AND LOWER(student_profiles.first_name) LIKE ?"
        params.append(like(first_name))

    if last_name:
        query += " AND LOWER(student_profiles.last_name) LIKE ?"
        params.append(like(last_name))

    if roll_number:
        query += " AND LOWER(student_profiles.roll_number) LIKE ?"
        params.append(like(roll_number))

    if batch_name:
        query += " AND LOWER(batches.batch_name) LIKE ?"
        params.append(like(batch_name))

    if stream:
        query += " AND LOWER(student_profiles.stream) LIKE ?"
        params.append(like(stream))

    # -----------------------
    # RANGE FILTERS
    # -----------------------
    if min_year is not None:
        query += " AND student_profiles.target_year >= ?"
        params.append(min_year)

    if max_year is not None:
        query += " AND student_profiles.target_year <= ?"
        params.append(max_year)

    # -----------------------
    # LIST FILTERS
    # -----------------------
    if batch_list:
        placeholders = ",".join(["?"] * len(batch_list))
        query += f" AND LOWER(batches.batch_name) IN ({placeholders})"
        params.extend([b.lower() for b in batch_list])

    if stream_list:
        placeholders = ",".join(["?"] * len(stream_list))
        query += f" AND LOWER(student_profiles.stream) IN ({placeholders})"
        params.extend([s.lower() for s in stream_list])
    
    if target_year is not None:
        query += " AND student_profiles.target_year = ?"
        params.append(target_year)

    if access is not None:
        query += " AND student_profiles.access = ?"
        params.append(access)

    # -----------------------
    # SORTING (SAFE)
    # -----------------------
    allowed_sort = {
        "username": "login.username",
        "first_name": "student_profiles.first_name",
        "last_name": "student_profiles.last_name",
        "roll_number": "student_profiles.roll_number",
        "batch_name": "batches.batch_name",
        "stream": "student_profiles.stream",
        "target_year": "student_profiles.target_year",
        "access": "student_profiles.access",
        "email": "student_profiles.email"
    }

    sort_column = allowed_sort.get(sort_by, "login.username")
    sort_direction = "ASC" if sort_order.lower() == "asc" else "DESC"

    query += f"""
        ORDER BY {sort_column} {sort_direction},
        student_profiles.user_id DESC
    """

    # -----------------------
    # PAGINATION
    # -----------------------
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    return rows


if __name__ == "__main__":
    create_tables()
    create_indexes()