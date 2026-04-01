# 📷 Face Recognition-Based Attendance Management System

Welcome to the **Face Recognition-Based Attendance Management System**! This application is designed to modernize and automate the attendance-tracking process using advanced facial recognition technology and a user-friendly role-based web interface.

---

## 🧠 1. What is this Product?

This system is a **complete, role-based attendance management tool** that leverages artificial intelligence to identify individuals and log their presence automatically. 

*   **Automation**: It replaces traditional, manual paper-based attendance or card-swiping systems.
*   **Security**: By using face recognition, it ensures that the person marking the attendance is physically present, preventing "buddy punching."
*   **Role-Based Control**: The system is partitioned into three distinct access levels: **Admin**, **Faculty**, and **Student**, each with specific tools and views.

---

## 👥 2. Who Uses This System?

The application is built for educational or corporate environments where structured attendance is critical.

### 🛡️ Admin
The "Superuser" of the system.
*   **User Management**: Creates faculty and student accounts.
*   **Academic Setup**: Creates courses and assigns them to faculty.
*   **Enrollment**: Links students to specific courses.
*   **System Oversight**: Monitors the entire application's data.

### 👨‍🏫 Faculty
The "Operation Lead" for specific classes.
*   **Face Registration**: Captures and trains the system on new student faces using the webcam.
*   **Session Control**: Selects a course and triggers the live face recognition window to start attendance.
*   **Reporting**: Views attendance logs for their assigned courses.

### 🎓 Student
The "End User" whose presence is being tracked.
*   **Automated Tracking**: Simply appears in front of the camera during a faculty-led session to be marked "Present."
*   **Self-Service**: Can log in to their dashboard to view their personal attendance history for all enrolled courses.

---

## 🏗️ 3. System Overview

The application is built on three core pillars that work together seamlessly:

1.  **💻 Web App (Flask)**: The central hub that handles the user interface (UI), login security, role routing, and course management.
2.  **👁️ Face Recognition Engine**: The "brains" of the system. It uses computer vision libraries to detect faces in real-time, compare them against the database, and verify identities.
3.  **🗄️ Database (SQLite)**: A reliable local storage system that tracks user accounts, student face encodings, course details, and every attendance entry.

---

## ⚙️ 4. How to Run the Application

Follow these simple steps to get the system up and running on your local machine:

1.  **Install Dependencies**:
    Open your terminal/command prompt and run:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the Server**:
    Run the main application file:
    ```bash
    python app.py
    ```

3.  **Open the Browser**:
    Launch your web browser and navigate to:
    **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 5. Default Login

To get started immediately, use the pre-configured administrator account:

**Admin Credentials:**
*   **Username**: `admin`
*   **Password**: `admin123`

---

## 🔄 6. Complete Usage Flow

### Step 1: Admin Setup 🛠️
1.  **Login** as the Admin.
2.  Create **Faculty** and **Student** accounts in the dashboard.
3.  Create a **Course** (e.g., "Artificial Intelligence 101") and assign a faculty member.
4.  **Enroll** students into that course.

### Step 2: Faculty Actions 📸
1.  Logout and **Login** as the assigned Faculty.
2.  Navigate to **Register Student Face**. Enter the student's username and follow the camera prompts to capture their face.
3.  Once registered, go back to the dashboard and click **Start Attendance** for a specific course.

### Step 3: Attendance Process 👁️‍🗨️
1.  The live camera window opens.
2.  The system **detects** a face and matches it against the registered encodings.
3.  When a student is recognized, their name and confidence score appear in green, and they are **automatically marked present** in the database.

### Step 4: Student View 📈
1.  Logout and **Login** as a Student.
2.  Immediately view a clean table of every date and time you were marked present for your courses.

---

## 📥 7. Inputs to the System

*   **User Credentials**: Usernames and passwords entered on the login page.
*   **Student Face**: Live video stream from your computer's webcam for registration and recognition.
*   **Course Details**: Names of courses and faculty assignments entered by the admin.

---

## 📤 8. Outputs from the System

*   **Attendance Records**: Securely stored entries in the SQL database.
*   **CSV Reports**: Automated daily and monthly summary files exported to the `attendance/` folder.
*   **Interactive UI**: Immediate visual feedback on dashboards for all users.

---

## 🧪 9. How to Test the System

To verify that everything is working perfectly:
1.  **Register 2 Students**: Create two student accounts and register their faces.
2.  **Start Attendance**: Trigger the recognition window for a course where they are enrolled.
3.  **Verify Recognition**: Ensure the system identifies them correctly with their names on the screen.
4.  **Check Records**: Login as one of those students and verify the record appears in their history.
5.  **Check Files**: Look in the `attendance/` directory to see if the system generated the CSV export.

---

## 🧠 10. Why Each Module Exists

*   **`app.py`**: The "Conductor" — it runs the web server and tells other modules when to act.
*   **`detector.py`**: The "Watcher" — it handles the live camera feed and facial recognition logic.
*   **`capture.py`**: The "Photographer" — it manages the initial capturing of student faces during registration.
*   **`database.py`**: The "Vault" — it defines how all user and attendance data is stored and retrieved.
*   **`attendance_manager.py`**: The "Secretary" — it handles the specific logic of marking attendance and exporting reports.

---

## ⚠️ 11. Important Notes

*   **Camera Access**: Ensure your webcam is connected and not being used by other apps (like Zoom or Teams) while running this system.
*   **Stop Command**: To close any camera window (during capture or recognition), simply press the **'q'** key on your keyboard.
*   **Local Only**: This system is designed for high-performance **local execution** (localhost) to ensure privacy and low latency.

---

## 🚀 12. Summary

This system transforms attendance from a tedious manual chore into a seamless, high-tech experience. By integrating AI-driven face recognition with a modern role-based web interface, it provides a stable, secure, and highly efficient solution for tracking presence in any environment.

---
*Created with ❤️ for precision and efficiency.*
