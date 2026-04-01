# Technical Algorithm: Face Recognition Attendance System (v2.0)

This document provides a detailed technical breakdown of the system architecture, from hardware initialization to data persistence and web-based role-based management.

---

## 1. System Initialization & Relational Design
1.1. **Core Directory Verification:** Automatically ensure the existence of `/dataset` (raw images), `/database` (SQLite), `/encodings` (binary facial data), and `/attendance` (CSV exports).
1.2. **Relational Database Migration:** 
   * Initialize `attendance.db` via `DatabaseManager`.
   * **Schema Maintenance:** Detect and add missing columns (`user_id`, `course_id`) to legacy tables to support high-granularity tracking.
1.3. **Encoding Synchronization (Face Matching Pool):**
   * Pre-load the 128-D Euclidean vectors (embeddings) from `encodings.pkl` for instantaneous runtime comparisons.
   * If the cache is empty, trigger the **Deep-Sync Process**:
     * Scan every subdirectory in `/dataset`.
     * Extract coordinates using the HOG (Histogram of Oriented Gradients) model.
     * Re-calculate and serialize vectors to the pickle-binary store.

## 2. Advanced Student Registration (Phase 1)
2.1. **Hardware Collision Avoidance:** Before opening the camera, query the `FaceDetector` for its `is_active` status. If busy, warn the user to stop the attendance session first.
2.2. **Camera Robustness Layer:** 
   * **Re-open Retry Loop:** Attempt to grab the V4L2 device. If closed recently, wait 1.5s/attempt for 3 cycles to allow OS resource release.
   * **Warmup Buffering:** Grab 15 discarded frames to stabilize the camera's auto-exposure and white-balance before detection begins.
2.3. **Interactive Capture Sequence:**
   * **Pre-capture HUD:** Overlay a 3-second live countdown on the screen.
   * **Localization:** Use Haar Cascades with `minNeighbors=4` for ultra-fast, high-sensitivity facial bounding box identification.
   * **Snapshot Logic:** Capture 5 images only after a face is verified in the frame, ensuring 100% data quality for the `/dataset`.
2.4. **Recursive Redirect Pattern:** Upon successful completion, stay on the `register_student` page (`register_student.html`) to allow for rapid, sequential registration of multiple students.

## 3. High-Performance Attendance Tracking (Phase 2)
3.1. **Non-Blocking Operation:** Launch the recognition loop in a **Background Daemon Thread** using the `threading` library, ensuring the Flask web UI and Flask-SocketIO (if applicable) remain responsive.
3.2. **Live Feed Pre-processing:**
   * **Resolution Scaling:** Downscale the live frame to 25% (0.25x) to maximize frames-per-second (FPS) on standard CPUs.
   * **Color Normalization:** Convert BGR (OpenCV standard) to RGB (face_recognition standard) on every odd-numbered frame only.
3.3. **AI Recognition Logic:**
   * **Face Localization:** Identify all facial bounding boxes in the frame.
   * **128-D Euclidean distance:** Compare live embeddings against the pre-loaded pool using the Python `numpy` library.
   * **Threshold Calibration:** Use a 0.6 distance tolerance (approx. 99.38% accuracy).
   * **Pseudo-Confidence Scoring:** $Confidence = \max(0, \text{round}((1.0 - distance) \times 100, 2))$.
3.4. **Persistent Windowing:** If no faces are detected, display **"STATUS: Waiting for people..."** to inform the operator that the system is active but idle.

## 4. Intelligent Marking & Feedback (Phase 3)
4.1. **Duplicate Prevention Algorithm:** 
   * Query the `attendance` table for `(name, course_id, current_date)`.
   * Only insert new record if count == 0.
4.2. **Real-time UX Feedback:** 
   * **Success HUD:** Overlay a large green banner: **"ATTENDANCE MARKED: {Name}"** on the camera stream for 3 seconds.
   * **Bounding Box Labeling:** Highlight known students in Green (✅) and unknown entities in Red (❌).

## 5. Session Termination & Resource Release
5.1. **Interrupt-Driven Stop:** Clicking **"🛑 Stop Attendance"** in the Web UI triggers an immediate `stop_signal` in the `FaceDetector`, breaking the loop at the next frame cycle.
5.2. **Clean-Up Queue:**
   * Release camera hardware immediately.
   * Force-kill all OpenCV windows via `destroyAllWindows()`.
   * Execute 15 cycles of `cv2.waitKey(1)` to "pump" the OS event loop, ensuring prompt window closure on Linux GNOME/KDE environments.
5.3. **Persistence Reset:** Reset the `is_active` flag within a `finally` block to guarantee the web dashboard reflects the true hardware status.

## 6. Functional Features Summary
* **📊 Role-Based Analytics:** Dynamic dashboards for Admin (Courses), Faculty (Tracking), and Students (History).
* **📄 CSV Report Hub:** Automatic generation of timestamped reports for offline administrative use.
* **✅ Live Sync Verification:** Real-time UI indicator of whether a student has valid face samples in the filesystem.
* **🌐 Offline Architecture:** 100% internet-independent execution using local AI models and SQLite storage.

---
*Algorithm designed for high-stability production or classroom deployment.*
