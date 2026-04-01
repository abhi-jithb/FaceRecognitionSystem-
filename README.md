# 📷 Face Recognition-Based Attendance Management System

Welcome to the **Face Recognition-Based Attendance Management System**! This application is a modern, automated solution for tracking attendance using facial recognition and a secure, role-based web interface built with Flask.

---

## 🧠 1. What is this Product?

This system is a **complete, role-based attendance management tool** that leverages artificial intelligence to identify individuals and log their presence automatically. 

*   **Automation**: No more manual paper logs or card swiping.
*   **Security**: Facial recognition ensures the person marking attendance is physically present.
*   **Role-Based Control**: Three distinct access levels (**Admin**, **Faculty**, and **Student**) ensure sensitive data is only accessible to authorized users.
*   **Zero-Config Migrations**: The system automatically detects and updates your database schema if you're upgrading from an older version.

---

## 👥 2. Who Uses This System?

### 🛡️ Admin (Superuser)
*   **User Management**: Creates faculty and student accounts.
*   **Academic Setup**: Manages courses and faculty assignments.
*   **Enrollment**: Links students to their respective courses.

### 👨‍🏫 Faculty (Operation Lead)
*   **Face Registration**: Captures and trains new student faces via the webcam.
*   **Attendance Sessions**: Starts the live recognition window for specific courses.
*   **Reporting**: Views logs for their assigned courses.

### 🎓 Student (End User)
*   **Personal Tracking**: Log in to view a comprehensive history of their own attendance across all enrolled courses.
*   **Automated Logging**: Just appear in the recognition window to be marked present!

---

## 🏗️ 3. System Overview

The application is built on three core pillars:
1.  **💻 Web App (Flask)**: Handles security, role-based routing, and data management.
2.  **👁️ Face Recognition Engine**: Uses HOG and Euclidean distance matching for highly accurate identity verification.
3.  **🗄️ Database (SQLite)**: Securely stores user profiles, student face encodings (128-D vectors), and timestamped attendance records.

---

## ⚙️ 4. How to Run the Application

### 1. Install Dependencies
Ensure you have Python 3.8+ installed. Then, run:
```bash
pip install -r requirements.txt
```

### 2. Start the Server
Run the main Flask application:
```bash
python app.py
```

### 3. Access the Dashboard
Open your browser and go to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 5. Default Login
For immediate setup, use the pre-configured admin account:
*   **Username**: `admin`
*   **Password**: `admin123`

---

## 🔄 6. Complete Usage Flow

1.  **Admin Setup**: Create Faculty and Student accounts, then create a Course and Enroll students.
2.  **Face Registration**: Login as Faculty, go to "Register Student Face," and capture the student's face (press **'q'** to finish).
3.  **Taking Attendance**: Faculty clicks "Start Attendance" for a course. The live camera window opens, identifies students, and logs them in the database.
4.  **Viewing Reports**: Students can see their own logs, and Faculty/Admins can view global reports on the "Reports" page.

---

## 🧠 7. Module Breakdown

*   **`app.py`**: The main entry point and web server.
*   **`src/database.py`**: The "Vault" — handles storage and automated schema migrations.
*   **`src/detector.py`**: The "Watcher" — manages the live recognition window.
*   **`src/capture.py`**: The "Photographer" — used for initial face registration.
*   **`src/attendance_manager.py`**: The "Secretary" — handles logging logic and CSV exports.
*   **`src/encoder.py`**: The "Translator" — converts images into 128-D math vectors for the AI.

---

## ⚠️ 8. Important Notes

*   **Camera Access**: Ensure no other application (like Zoom) is using your webcam.
*   **Stop Command**: In any camera window (Capture or Recognition), press **'q'** to close it.
*   **Database**: The system uses `database/attendance.db`. If you ever need a fresh start, simply delete this file; the app will recreate it with the correct schema automatically.

---
*Created with ❤️ for precision and efficiency.*
