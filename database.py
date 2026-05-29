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
 
    c.execute("""
            CREATE TABLE IF NOT EXISTS login_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                success INTEGER DEFAULT 0,
                failure_reason TEXT,
                ip_address TEXT,
                forwarded_for TEXT,
                host TEXT,
                origin TEXT,
                referer TEXT,
                user_agent TEXT,
                accept_language TEXT,
                sec_ch_ua TEXT,
                sec_ch_platform TEXT,
                sec_ch_mobile TEXT,
                method TEXT,
                path TEXT,
                screen_resolution TEXT,
                viewport TEXT,
                timezone TEXT,
                timezone_offset INTEGER,
                language TEXT,
                languages TEXT,
                platform TEXT,
                cpu_cores INTEGER,
                device_memory TEXT,
                touch_points INTEGER,
                cookies_enabled INTEGER,
                online_status INTEGER,
                connection_type TEXT,
                device_pixel_ratio REAL,
                local_storage INTEGER,
                session_storage INTEGER,
                do_not_track TEXT,
                login_id TEXT,
                request_id TEXT,
                session_id TEXT,
                device_id TEXT,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES login(id) ON DELETE CASCADE
            )
            """)
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

def get_batch_name(batch_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT batch_name FROM batches WHERE id = ?", (batch_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

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
    # if data and data['batch_name'] is not None:
        # data['batch_name'] = get_batch_name(data['batch_id'])

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

def clear_table_with_role(table_name, role):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute(f"DELETE FROM login WHERE role = ?", (role,))
        conn.commit()
        return True, f"login cleared successfully"
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

def add_login_log(
    user_id, success,
    ip_address=None, forwarded_for=None, host=None, origin=None, referer=None,
    user_agent=None, accept_language=None, sec_ch_ua=None, sec_ch_platform=None, sec_ch_mobile=None,
    method=None, path=None,
    screen_resolution=None, viewport=None, timezone=None, timezone_offset=None,
    language=None, languages=None, platform=None,
    cpu_cores=None, device_memory=None, touch_points=None,
    cookies_enabled=None, online_status=None,
    connection_type=None, device_pixel_ratio=None,
    local_storage=None, session_storage=None,
    do_not_track=None,
    login_id=None, request_id=None, session_id=None, device_id=None,
    failure_reason=None
):

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    try:
        c.execute("""
            INSERT INTO login_logs(
                user_id, success, failure_reason,
                ip_address, forwarded_for, host, origin, referer,
                user_agent, accept_language, sec_ch_ua, sec_ch_platform, sec_ch_mobile,
                method, path,
                screen_resolution, viewport, timezone, timezone_offset,
                language, languages, platform,
                cpu_cores, device_memory, touch_points,
                cookies_enabled, online_status,
                connection_type, device_pixel_ratio,
                local_storage, session_storage,
                do_not_track,
                login_id, request_id, session_id, device_id
            )
            VALUES(
                ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?,
                ?, ?,
                ?,
                ?, ?, ?, ?
            )
        """, (
            user_id, int(success), failure_reason,
            ip_address, forwarded_for, host, origin, referer,
            user_agent, accept_language, sec_ch_ua, sec_ch_platform, sec_ch_mobile,
            method, path,
            screen_resolution, viewport, timezone, timezone_offset,
            language, languages, platform,
            cpu_cores, device_memory, touch_points,
            int(cookies_enabled) if cookies_enabled is not None else None,
            int(online_status) if online_status is not None else None,
            connection_type, device_pixel_ratio,
            int(local_storage) if local_storage is not None else None,
            int(session_storage) if session_storage is not None else None,
            do_not_track,
            login_id, request_id, session_id, device_id
        ))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print(f"[LOGIN LOG ERROR] {e}")
        return False

    finally:
        conn.close()

def get_user_id(username):
    conn=sqlite3.connect(DATABASE)
    c=conn.cursor()

    c.execute("SELECT id FROM login WHERE username=?",(username,))
    row=c.fetchone()

    conn.close()

    return row[0] if row else None

def get_login_logs(limit=100,offset=0):
    conn=sqlite3.connect(DATABASE)
    conn.row_factory=sqlite3.Row
    c=conn.cursor()

    c.execute("""
        SELECT
            login_logs.id,
            login.username,
            login_logs.ip_address,
            login_logs.user_agent,
            login_logs.login_time,
            login_logs.success
        FROM login_logs
        LEFT JOIN login
        ON login.id=login_logs.user_id
        ORDER BY login_logs.id DESC
        LIMIT ? OFFSET ?
    """,(limit,offset))

    rows=[dict(row) for row in c.fetchall()]

    conn.close()

    return rows

def ensure_login_logs_columns(conn):
    c = conn.cursor()

    # Existing columns
    c.execute("PRAGMA table_info(login_logs)")
    existing_columns = [column[1] for column in c.fetchall()]

    required_columns = {
        "failure_reason": "TEXT",

        "forwarded_for": "TEXT",
        "host": "TEXT",
        "origin": "TEXT",
        "referer": "TEXT",

        "accept_language": "TEXT",
        "sec_ch_ua": "TEXT",
        "sec_ch_platform": "TEXT",
        "sec_ch_mobile": "TEXT",

        "method": "TEXT",
        "path": "TEXT",

        "screen_resolution": "TEXT",
        "viewport": "TEXT",
        "timezone": "TEXT",
        "timezone_offset": "INTEGER",

        "language": "TEXT",
        "languages": "TEXT",

        "platform": "TEXT",

        "cpu_cores": "INTEGER",
        "device_memory": "TEXT",

        "touch_points": "INTEGER",

        "cookies_enabled": "INTEGER",
        "online_status": "INTEGER",

        "connection_type": "TEXT",

        "device_pixel_ratio": "REAL",

        "local_storage": "INTEGER",
        "session_storage": "INTEGER",

        "do_not_track": "TEXT",

        "login_id": "TEXT",
        "request_id": "TEXT",
        "session_id": "TEXT",
        "device_id": "TEXT"
    }

    for column_name, column_type in required_columns.items():

        if column_name not in existing_columns:

            query = f'''
            ALTER TABLE login_logs
            ADD COLUMN {column_name} {column_type}
            '''

            c.execute(query)

            print(f"[+] Added column: {column_name}")

    conn.commit()

def add_staff(username, password, first_name, last_name, email, phone, department, designation):
    conn = get_connection()
    try:
        c = conn.cursor()
        password_hash = generate_password_hash(password)

        c.execute('INSERT INTO login (username, password, role) VALUES (?, ?, ?)', (username, password_hash, 'staff'))
        user_id = c.lastrowid
        try:
            c.execute('''INSERT INTO staff_profiles (user_id, first_name, last_name, email, phone, department, designation) VALUES (?, ?, ?, ?, ?, ?, ?)''', (user_id, first_name, last_name, email, phone, department, designation))
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            c.execute('DELETE FROM login WHERE id = ?', (user_id,))
            conn.commit()
            return False, f"Email shall be unique: {str(e)}"

        return True, "Staff added successfully"
    
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return False, f"Username shall be unique: {str(e)}"
    except Exception as e:
        conn.rollback()
        return False, str(e)

def get_all_staff_profiles():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''SELECT 
              login.username,
              staff_profiles.first_name,
              staff_profiles.last_name,
              staff_profiles.email,
              staff_profiles.phone,
              staff_profiles.department,
              staff_profiles.designation,
              staff_profiles.is_active,
              staff_profiles.created_at
            FROM staff_profiles
            JOIN login ON login.id = staff_profiles.user_id''')

    rows = c.fetchall()
    staff_list = [dict(row) for row in rows]

    conn.close()

    return staff_list

def all_staff(
    search="",
    department=None,
    department_list=None,
    designation=None,
    designation_list=None,
    is_active=None,
    first_name=None,
    last_name=None,
    username=None,
    email=None,
    phone=None,
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
            staff_profiles.first_name,
            staff_profiles.last_name,
            staff_profiles.email,
            staff_profiles.phone,
            staff_profiles.department,
            staff_profiles.designation,
            staff_profiles.is_active
        FROM staff_profiles
        JOIN login ON login.id = staff_profiles.user_id
        WHERE login.role = 'staff'
    """

    params = []

    # -----------------------
    # SEARCH
    # -----------------------
    if search:
        like_search = f"%{search.lower()}%"

        query += """
            AND (
                LOWER(login.username) LIKE ?
                OR LOWER(staff_profiles.first_name) LIKE ?
                OR LOWER(staff_profiles.last_name) LIKE ?
                OR LOWER(staff_profiles.email) LIKE ?
                OR LOWER(staff_profiles.phone) LIKE ?
                OR LOWER(staff_profiles.department) LIKE ?
                OR LOWER(staff_profiles.designation) LIKE ?
            )
        """

        params.extend([like_search] * 7)

    # -----------------------
    # LIKE HELPER
    # -----------------------
    def like(v):
        return f"%{v.lower()}%"

    # -----------------------
    # FILTERS
    # -----------------------
    if username:
        query += " AND LOWER(login.username) LIKE ?"
        params.append(like(username))

    if first_name:
        query += " AND LOWER(staff_profiles.first_name) LIKE ?"
        params.append(like(first_name))

    if last_name:
        query += " AND LOWER(staff_profiles.last_name) LIKE ?"
        params.append(like(last_name))

    if email:
        query += " AND LOWER(staff_profiles.email) LIKE ?"
        params.append(like(email))

    if phone:
        query += " AND LOWER(staff_profiles.phone) LIKE ?"
        params.append(like(phone))

    if department:
        query += " AND LOWER(staff_profiles.department) LIKE ?"
        params.append(like(department))

    if designation:
        query += " AND LOWER(staff_profiles.designation) LIKE ?"
        params.append(like(designation))

    # -----------------------
    # LIST FILTERS
    # -----------------------
    if department_list:
        placeholders = ",".join(["?"] * len(department_list))

        query += f"""
            AND LOWER(staff_profiles.department)
            IN ({placeholders})
        """

        params.extend([d.lower() for d in department_list])

    if designation_list:
        placeholders = ",".join(["?"] * len(designation_list))

        query += f"""
            AND LOWER(staff_profiles.designation)
            IN ({placeholders})
        """

        params.extend([d.lower() for d in designation_list])

    # -----------------------
    # ACTIVE FILTER
    # -----------------------
    if is_active is not None:
        query += " AND staff_profiles.is_active = ?"
        params.append(is_active)

    # -----------------------
    # SAFE SORTING
    # -----------------------
    allowed_sort = {
        "username": "login.username",
        "first_name": "staff_profiles.first_name",
        "last_name": "staff_profiles.last_name",
        "email": "staff_profiles.email",
        "phone": "staff_profiles.phone",
        "department": "staff_profiles.department",
        "designation": "staff_profiles.designation",
        "is_active": "staff_profiles.is_active"
    }

    sort_column = allowed_sort.get(sort_by, "login.username")
    sort_direction = "ASC" if sort_order.lower() == "asc" else "DESC"

    query += f"""
        ORDER BY {sort_column} {sort_direction},
        staff_profiles.user_id DESC
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

def revoke_staff_access(username):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE staff_profiles
        SET is_active = 0
        WHERE user_id = (
            SELECT id
            FROM login
            WHERE username = ?
        )
    """, (username,))

    conn.commit()
    conn.close()

def grant_staff_access(username):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE staff_profiles
        SET is_active = 1
        WHERE user_id = (
            SELECT id
            FROM login
            WHERE username = ?
        )
    """, (username,))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    create_indexes()