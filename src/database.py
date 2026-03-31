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
            
            # Table: students
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    encoding BLOB
                )
            ''')
            
            # Table: attendance
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    UNIQUE(name, date) -- Prevent duplicate entries per day
                )
            ''')
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

    def mark_attendance(self, name):
        """Marks attendance for a student. Returns True if marked, False if already marked today."""
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
                    (name, current_date, current_time)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Already marked today due to UNIQUE constraint
            return False
