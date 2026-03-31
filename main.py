import sys
import os

from src.database import DatabaseManager
from src.encoder import FaceEncoder
from src.attendance_manager import AttendanceManager
from src.capture import FaceCapturer

def display_menu():
    print("\n" + "="*45)
    print(" 🌟 FACE RECOGNITION ATTENDANCE SYSTEM MVP 🌟")
    print("="*45)
    print(" 1. Register Student (Capture & Map)")
    print(" 2. Start Attendance (Real-time Live Feed)")
    print(" 3. View Attendance (Generate Reports)")
    print(" 4. Exit")
    print("="*45)

def main():
    # Initialize Core Components
    db_manager = DatabaseManager(db_path="database/attendance.db")
    encoder = FaceEncoder(db_manager=db_manager, dataset_path="dataset", encodings_path="encodings/encodings.pkl")
    attendance_manager = AttendanceManager(db_manager=db_manager, output_dir="attendance")
    capturer = FaceCapturer(dataset_path="dataset")

    while True:
        display_menu()
        choice = input("[?]: Select an option (1-4): ").strip()

        if choice == '1':
            name = input("\n[?] Enter student's full name: ").strip()
            if not name:
                print("[ERROR] Name cannot be empty.")
                continue
                
            # Register in Database initially
            if db_manager.register_student(name):
                print(f"[SUCCESS] Student '{name}' registered in database.")
                
                # Capture Images
                print("\n[INFO] Get ready to capture face dataset. We will take 5 photos.")
                success = capturer.capture_faces(name, num_images=5)
                
                if success:
                    # Immediately generate encodings so the flow is seamless
                    print("[INFO] Processing and encoding faces...")
                    if encoder.generate_encodings_for_user(name):
                        print(f"\n[SUCCESS] '{name}' has been perfectly mapped! They are ready for attendance.")
                    else:
                        print(f"\n[ERROR] Could not extract face encodings for '{name}'. Please try registering again.")
            else:
                print(f"[ERROR] Student '{name}' is already registered in the system.")

        elif choice == '2':
            # Start Live Detection
            from src.detector import FaceDetector
            detector = FaceDetector(encoder=encoder, attendance_manager=attendance_manager)
            detector.start_recognition()

        elif choice == '3':
            # Export CSVs
            print("\n[INFO] Generating Attendance Reports...")
            attendance_manager.export_daily_report()
            attendance_manager.export_monthly_report()
            print(f"[INFO] You can view reports in: {os.path.abspath('attendance')}")

        elif choice == '4':
            print("\n[INFO] Exiting program cleanly. Goodbye!")
            sys.exit(0)
            
        else:
            print("[ERROR] Invalid choice. Please press a number between 1 and 4.")

if __name__ == "__main__":
    # Ensure mandatory folders exist
    os.makedirs("database", exist_ok=True)
    os.makedirs("dataset", exist_ok=True)
    os.makedirs("attendance", exist_ok=True)
    os.makedirs("encodings", exist_ok=True)
    
    main()
