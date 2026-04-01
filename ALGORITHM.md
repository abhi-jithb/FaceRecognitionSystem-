# Algorithm: Face Recognition-Based Attendance System

This document outlines the step-by-step logic and mathematical flow of the attendance system, structured for academic documentation and technical presentations.

---

## 1. Initialization & Environment Setup
1.1. **Directory Verification:** Check for `/dataset`, `/database`, and `/encodings`. Create them if missing.
1.2. **Database Integrity:** Establish connection to `attendance.db`. Perform **Schema Migration** to support Role-Based Access (Users, Courses, Enrollments).
1.3. **Encoding Synchronization:** 
   * Check if `encodings.pkl` exists.
   * If missing or images were added, trigger `FaceEncoder` to scan `/dataset` and generate 128-D facial embeddings.
1.4. **Web Server Ready:** Initialize Flask with session security to manage Admin (Management), Faculty (Operations), and Student (View) roles.

## 2. Phase 1: Robust Face Registration (Faculty Only)
2.1. **Target Identification:** Faculty selects a student from the "Registered in DB" list.
2.2. **Hardware Initialization:**
   * **Wait & Retry:** Attempt to open VideoCapture(0). If busy (transitioning from attendance), wait 1.5s and retry (up to 3 attempts).
   * **Warmup:** Grab 15 discarded frames to allow auto-exposure/white-balance to stabilize.
2.3. **Pre-Capture Countdown:** Display a 3-second visual countdown on the UI to ensure student readiness.
2.4. **Face Localization & Validation:**
   * Use Haar Cascade with adjusted sensitivity (`minNeighbors=4`) for high-speed detection.
   * Verify face presence before triggering a snapshot.
2.5. **Sequential Acquisition:** Capture 5 high-quality frames with a 0.8s interval to ensure variety in facial angles.
2.6. **Persistence & Flow:**
   * Save images to `/dataset/{Name}/`. 
   * **Stay-on-Page:** Redirect the Faculty back to the registration list to allow immediate next-student registration.

## 3. Phase 2: Asynchronous Attendance Tracking
3.1. **Session Trigger:** Faculty selects a specific `course_id` and starts attendance.
3.2. **Thread Management:** Launch `FaceDetector.start_recognition` in a **Background Daemon Thread** to prevent blocking the Flask main loop and UI.
3.3. **Real-time Recognition Loop:**
   * **Performance Tuning:** Process every other frame. Resize frames to 25% (1/4th) for CPU optimization.
   * **Detection (HOG):** Detect bounding boxes for all faces in the frame.
   * **Status Display:** If `len(faces) == 0`, display **"STATUS: Waiting for people..."** to the operator.
3.4. **Stop Signal Reactivity:** Continuously monitor a `stop_signal` flag. Interrupt the loop immediately if the flag is set via the Web UI "Stop" button.

## 4. Phase 3: 128-D Facial Matching
4.1. **Feature Extraction:** Convert live detected faces into 128-dimensional numeric vectors (embeddings).
4.2. **Euclidean Distance Comparison:**
   * Measure the distance ($d$) between the live vector ($p$) and all known database vectors ($q$):
     $$d(p, q) = \sqrt{\sum_{i=1}^{n} (p_i - q_i)^2}$$
4.3. **Match Verification:**
   * Compare against a tolerance threshold (0.6).
   * **Confidence Score Calibration:** $Confidence = \max(0, \text{round}((1.0 - d) \times 100, 2))$.
   * A match is accepted only if $Confidence > 50\%$.

## 5. Phase 4: Intelligent Attendance Lifecycle
5.1. **Marking Logic:** Upon a successful match, pass Name + Course ID to `AttendanceManager`.
5.2. **Duplicate Suppression:** Verify that the student hasn't already been marked for the **SAME course** on the **SAME day**.
5.3. **Feedback Banner:** If successful, display a green success banner on the camera stream for 3 seconds: **"ATTENDANCE MARKED: {Name}"**.
5.4. **Database Record:** Insert entry: `(Name, course_id, Date, Time)`.

## 6. Phase 5: Resource Cleanup & Reporting
6.1. **Manual Termination:** Click **"🛑 Stop Attendance"** in the Web UI.
6.2. **Graceful Release:** 
   * Set `stop_signal = True`.
   * Wait for thread loop to break.
   * Release camera hardware.
   * **Event Pump:** Call `cv2.waitKey(1)` 15 times to ensure the OS destroys all UI windows completely.
6.3. **Dashboard Sync:** Verification status badges (✅ Captured vs ❌ No Face) are updated dynamically by scanning `/dataset`.
6.4. **CSV Export:** Generate detailed attendance logs as CSV files for faculty review.

---
*Optimized for high-stability local execution without internet dependency.*
