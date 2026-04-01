import sqlite3
import os
import pickle
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="database/attendance.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_tables()

    def _create_tables(self):
        """Creates the necessary tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table: users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL -- 'admin', 'faculty', 'student'
                )
            ''')

            # Table: courses
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_name TEXT NOT NULL,
                    faculty_id INTEGER,
                    FOREIGN KEY (faculty_id) REFERENCES users (id)
                )
            ''')

            # Table: enrollments
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS enrollments (
                    student_id INTEGER,
                    course_id INTEGER,
                    PRIMARY KEY (student_id, course_id),
                    FOREIGN KEY (student_id) REFERENCES users (id),
                    FOREIGN KEY (course_id) REFERENCES courses (id)
                )
            ''')
            
            # Table: students (existing, mapping to users if needed, but keeping for compatibility)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    encoding BLOB,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Table: attendance
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    course_id INTEGER,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    FOREIGN KEY (course_id) REFERENCES courses (id),
                    UNIQUE(name, date, course_id) -- Prevent duplicate entries per course per day
                )
            ''')
            
            # Check if 'students' table needs migration (adding user_id column)
            cursor.execute("PRAGMA table_info(students)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'user_id' not in columns:
                try:
                    cursor.execute("ALTER TABLE students ADD COLUMN user_id INTEGER REFERENCES users(id)")
                except sqlite3.OperationalError:
                    pass
            
            # Check if 'attendance' table needs migration (adding course_id column)
            cursor.execute("PRAGMA table_info(attendance)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'course_id' not in columns:
                try:
                    cursor.execute("ALTER TABLE attendance ADD COLUMN course_id INTEGER REFERENCES courses(id)")
                except sqlite3.OperationalError:
                    pass
            
            # Add a default admin if none exists
            cursor.execute("SELECT * FROM users WHERE role = 'admin'")
            if not cursor.fetchone():
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                               ('admin', 'admin123', 'admin')) # Simple password for local demo
            
            conn.commit()

    def register_student(self, name, encoding=None):
        """Registers a new student. Returns True if successful, False if already exists."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                encoding_blob = pickle.dumps(encoding) if encoding is not None else None
                cursor.execute("INSERT INTO students (name, encoding) VALUES (?, ?)", (name, encoding_blob))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
            
    def update_encoding(self, name, encoding):
        """Updates the encoding for an existing student."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            encoding_blob = pickle.dumps(encoding)
            cursor.execute("UPDATE students SET encoding = ? WHERE name = ?", (encoding_blob, name))
            conn.commit()

    def mark_attendance(self, name, course_id=None):
        """Marks attendance for a student. Returns True if marked, False if already marked today for this course."""
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO attendance (name, course_id, date, time) VALUES (?, ?, ?, ?)",
                    (name, course_id, current_date, current_time)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Already marked today due to UNIQUE constraint
            return False

    # --- Role-Based Access Support ---

    def create_user(self, username, password, role):
        """Creates a new user record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, password, role)
                )
                user_id = cursor.lastrowid
                
                # If student, also create entry in students table (legacy compatibility)
                if role == 'student':
                    cursor.execute("INSERT INTO students (name, user_id) VALUES (?, ?)", (username, user_id))
                
                conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None

    def verify_user(self, username, password):
        """Verifies clear-text password for demo purposes (no hashing for stability as requested)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, password))
            return cursor.fetchone()

    def create_course(self, course_name, faculty_id):
        """Creates a new course."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO courses (course_name, faculty_id) VALUES (?, ?)", (course_name, faculty_id))
            conn.commit()
            return cursor.lastrowid

    def enroll_student(self, student_id, course_id):
        """Enrolls a student in a course."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_users_by_role(self, role):
        """Returns all users of a specific role."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username FROM users WHERE role = ?", (role,))
            return cursor.fetchall()

    def get_all_courses(self):
        """Returns all courses with faculty names."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.course_name, u.username as faculty_name 
                FROM courses c 
                JOIN users u ON c.faculty_id = u.id
            """)
            return cursor.fetchall()

    def get_courses_by_faculty(self, faculty_id):
        """Returns courses assigned to a faculty."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, course_name FROM courses WHERE faculty_id = ?", (faculty_id,))
            return cursor.fetchall()

    def get_attendance_report(self, course_id=None, student_name=None, faculty_id=None):
        """Generic report generator."""
        query = """
            SELECT a.name, c.course_name, a.date, a.time 
            FROM attendance a 
            LEFT JOIN courses c ON a.course_id = c.id
            WHERE 1=1
        """
        params = []
        if course_id:
            query += " AND a.course_id = ?"
            params.append(course_id)
        if student_name:
            query += " AND a.name = ?"
            params.append(student_name)
        if faculty_id:
            query += " AND c.faculty_id = ?"
            params.append(faculty_id)
        
        query += " ORDER BY a.date DESC, a.time DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
