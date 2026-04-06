import pandas as pd
import sqlite3
import os
from datetime import datetime
from .database import DatabaseManager

class AttendanceManager:
    def __init__(self, db_manager: DatabaseManager, output_dir="attendance"):
        self.db_manager = db_manager
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def mark_attendance(self, name, course_id=None):
        """Marks attendance in the database."""
        success = self.db_manager.mark_attendance(name, course_id=course_id)
        if success:
            print(f"[SUCCESS] Attendance marked for {name} in course {course_id} today!")
        # We don't print anything if already marked to avoid spamming the console
        # since detection happens many times per second.
        return success

    def export_daily_report(self):
        """Exports today's attendance to a CSV file."""
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        csv_filename = os.path.join(self.output_dir, f"daily_report_{current_date}.csv")

        # Fetch attendance from DB
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                query = """
                    SELECT a.id, a.name, c.course_name, a.date, a.time 
                    FROM attendance a 
                    LEFT JOIN courses c ON a.course_id = c.id 
                    WHERE a.date = ?
                """
                df = pd.read_sql_query(query, conn, params=(current_date,))

            if df.empty:
                print(f"[INFO] No attendance records found for {current_date}.")
                
                # Auto-create empty CSV if not exists as requested
                df = pd.DataFrame(columns=["id", "name", "course_name", "date", "time"])
                df.to_csv(csv_filename, index=False)
                return False

            df.to_csv(csv_filename, index=False)
            print(f"[SUCCESS] Daily attendance exported to {csv_filename}")
            return csv_filename
        except Exception as e:
            print(f"[ERROR] Failed to export daily CSV: {e}")
            return None
            
    def export_monthly_report(self):
        """Exports the current month's attendance to a single CSV file."""
        now = datetime.now()
        current_month = now.strftime("%Y-%m")
        csv_filename = os.path.join(self.output_dir, f"monthly_summary_{current_month}.csv")

        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                query = """
                    SELECT a.id, a.name, c.course_name, a.date, a.time 
                    FROM attendance a 
                    LEFT JOIN courses c ON a.course_id = c.id 
                    WHERE a.date LIKE ?
                """
                df = pd.read_sql_query(query, conn, params=(f"{current_month}-%",))

            if df.empty:
                print(f"[INFO] No attendance records found for {current_month}.")
                return False

            df.to_csv(csv_filename, index=False)
            print(f"[SUCCESS] Monthly summary exported to {csv_filename}")
            return csv_filename
        except Exception as e:
            print(f"[ERROR] Failed to export monthly CSV: {e}")
            return None
