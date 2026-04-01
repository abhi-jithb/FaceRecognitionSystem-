# Algorithm: Face Recognition-Based Attendance System

This document outlines the step-by-step logic and mathematical flow of the attendance system, structured for academic documentation and technical presentations.

---

## 1. Initialization
1.1. **Environment Setup:** Verify the existence of the `/dataset`, `/database`, and `/attendance` directories.
1.2. **Database Connection & Migration:** Establish a persistent connection to `attendance.db`. Check the current schema and **automatically migrate** the tables (adding `user_id` to `students` and `course_id` to `attendance`) if transitioning from an older version.
1.3. **Flask Web Server:** Initialize the Flask application, setting up secret keys for session management and defining routes for Admin, Faculty, and Student roles.
1.4. **Encoding Pre-loading:** Retrieve all unique facial embeddings (128-D vectors) and associated names from the database into the system's runtime memory for instantaneous matching.
1.5. **Hardware Activation:** Initialize the primary webcam capture object using OpenCV for both registration and detection.

## 2. User Interaction / Role-Based Access
2.1. **Web UI Dashboard:** Present a secure login screen. Upon authentication, route the user to their specific dashboard based on their role:
   * **🛡️ Admin:** Access to user creation, course management, and enrollment.
   * **👨‍🏫 Faculty:** Access to student face registration and starting attendance sessions.
   * **🎓 Student:** Access to personal attendance history.
2.2. **Request Handling:** Wait for user-specified triggers via HTTP POST/GET requests (e.g., clicking "Start Attendance" or "Register Student").

## 3. Phase 1: Face Registration (Faculty Only)
3.1. **Identity Input:** Faculty selects a student account and enters their name via the Web UI registration form.
3.2. **Image Acquisition:** The system triggers `FaceCapturer`, opening the webcam feed and capturing 5 sequential frames of the student's face.
3.3. **Face Localization:** Use the HOG (Histogram of Oriented Gradients) model to detect the face within each captured frame.
3.4. **Feature Extraction:** Convert normalized facial images into a structural 128-dimensional numeric vector (encoding).
3.5. **Data Persistence:** Save the raw images to `/dataset/Name/` and store the averaged 128D encoding directly into the SQLite `students` table, linked to the student's `user_id`.

## 4. Phase 2: Face Detection
4.1. **Stream Capture:** Acquire real-time video frames from the webcam at a standard resolution (640x480).
4.2. **Preprocessing:** Resize the frame to 1/4th its original size to reduce computational overhead on the CPU.
4.3. **Color Space Conversion:** Convert the frame from BGR (OpenCV default) to RGB.
4.4. **HOG Modeling:** Execute the HOG detection algorithm to identify all facial bounding boxes present in the frame.

## 5. Phase 3: Face Recognition
5.1. **Live Encoding:** Compute the 128D facial encoding for every face detected in the live frame.
5.2. **Distance Calculation:** Use **Euclidean Distance** to measure the variance between the live encoding and the pre-loaded database encodings.
   * *Formula:* $d(p, q) = \sqrt{\sum_{i=1}^{n} (p_i - q_i)^2}$
5.3. **Similarity Comparison:** Apply a strict threshold (e.g., 0.5). If the minimum distance is below the threshold, a "Match" is confirmed.
5.4. **Confidence Scoring:** Convert the distance into a percentage: $Confidence = \max(0, (1 - distance) \times 100)$.
5.5. **Classification:** 
   * If Match found → Retrieve Name; Set status to "Recognized".
   * If Distance > Threshold → Assign identity as "Unknown".

## 6. Phase 4: Attendance Marking
6.1. **Verification Logic:** Receive the recognized Name and the active `course_id`.
6.2. **Duplicate Prevention:** Query the `attendance` table using the `Name`, `course_id`, and `Current Date`.
6.3. **Attendance Insertion:** 
   * If record count == 0 → Insert row: `(Name, course_id, Date, Time)`.
   * If record count > 0 → Reject entry (Prevent multiple logs for the same course on the same day).
6.4. **Visual Feedback:** Render the name, confidence score, and timestamp on the GUI window in real-time.

## 7. Phase 5: Database & Report Management
7.1. **Relational Integrity:** Ensure the SQLite database maintains links between Users, Students, Courses, and Attendance records.
7.2. **Persistence Guarantee:** Commit SQL transactions immediately to ensure data durability.
7.3. **CSV Compilation:** The `AttendanceManager` extracts logs and exports them to a `.csv` file in the `/attendance` directory with timestamped filenames for external reporting.

## 8. End of Session
8.1. **Loop Continuity:** The recognition window runs until the user presses **'q'**, returning them to the Web Dashboard.
8.2. **Resource Release:** Release the webcam hardware and gracefully close UI windows after each session.
8.3. **Final Status:** Provide visual feedback on the dashboard summarizing the action taken (e.g., "Successfully registered {student}" or "Attendance session complete").

---
*Algorithm designed for high-performance local execution and secure role-based management.*
