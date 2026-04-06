import sqlite3
import os
import shutil

def reset_system():
    db_path = "database/attendance.db"
    dataset_path = "dataset"
    encodings_path = "encodings"
    
    print("\n--- ATTENDANCE SYSTEM CLEANUP ---")
    
    # 1. Clear Database Tables
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Wipe attendance records
            cursor.execute("DELETE FROM attendance")
            # Wipe student enrollments
            cursor.execute("DELETE FROM enrollments")
            # Wipe students from the main users table
            cursor.execute("DELETE FROM users WHERE role = 'student'")
            # Wipe the legacy students table
            cursor.execute("DELETE FROM students")
            
            conn.commit()
            conn.close()
            print("[✓] Database: All student records and attendance logs cleared.")
        except Exception as e:
            print(f"[!] Database Error: {e}")
    
    # 2. Clear Dataset Folder
    if os.path.exists(dataset_path):
        try:
            for item in os.listdir(dataset_path):
                item_path = os.path.join(dataset_path, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            print("[✓] Storage: Dataset images deleted.")
        except Exception as e:
            print(f"[!] Dataset Cleanup Error: {e}")

    # 3. Clear Encodings Folder
    if os.path.exists(encodings_path):
        try:
            for item in os.listdir(encodings_path):
                os.remove(os.path.join(encodings_path, item))
            print("[✓] Storage: Facial encodings cache cleared.")
        except Exception as e:
            print(f"[!] Encodings Cleanup Error: {e}")

    print("\n[SUCCESS] System reset complete. Ready for new student registration.\n")

if __name__ == "__main__":
    reset_system()
