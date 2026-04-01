# Algorithm Summary: Face Recognition Attendance System

This document provides a concise overview of the core logic and technical workflows governing the Face Recognition-Based Attendance Tracking System.

---

## 1. System Initialization
1.1. **Cold-Start Sequence:** Automatically verify the existence of the `/dataset`, `/database`, `/encodings`, and `/attendance` directories.
1.2. **Database Integrity:** Establish connection to `attendance.db` and perform schema migrations to support role-based data.
1.3. **Encoding Lake:** Pre-load 128-D facial feature vectors from a serialized `.pkl` binary store. Trigger the **Deep-Sync Process** to rebuild the lake if images were recently added.

## 2. Integrated Face Registration
2.1. **Hardware Acquisition:** Attempt to open the webcam with a 3-cycle retry loop (1.5s/attempt) to allow previous handles to release. Discard the initial 15 frames for sensor warmup.
2.2. **Biometric Capture:** Use **Haar Cascade** with an interactive 3-second HUD countdown. Capture 5 frames at 0.8s intervals once a face is verified in the frame.
2.3. **Persistence:** Save raw images to `/dataset/{Name}/`, and redirect the user back to the registration list immediately for rapid, multi-student input.

## 3. High-Performance Attendance Tracking
3.1. **Async Monitoring:** Launch the recognition loop in a **Background Daemon Thread** to prevent web server UI hanging.
3.2. **Frame Optimization:** Resize the live frame to 25% (0.25x scaling) and process every other frame for high FPS on standard CPUs.
3.3. **Idle Persistence:** If no faces are detected, display **"STATUS: Waiting for people..."** to the operator.

## 4. Facial Recognition Calculus
4.1. **128-D Vector Extraction:** Compute the structural facial geometry from the live frame using a deep learning model.
4.2. **Multidimensional Comparison:** Calculate the variance between live vectors ($p$) and reference vectors ($q$) using the **Euclidean Distance Formula**:
   $$d(p, q) = \sqrt{\sum_{i=1}^{n} (p_i - q_i)^2}$$
4.3. **Precision Matching:** Reject matches if $d > 0.6$. Convert matching distances into a linear confidence score ($Confidence = (1 - d) \times 100$).

## 5. Intelligent Marking & Feedback
5.1. **Database Atomicity:** Pass (Name + Course_ID) to the `AttendanceManager`. Only insert a record if the student hasn't already been marked for the **same course** on the **same day**.
5.2. **Visual Success HUD:** Highlight recognized students in Green (✅) and Unknowns in Red (❌). If successful, display an onscreen banner for 3 seconds.

## 6. Resource Cleanup
6.1. **Interrupt Signal:** Click **"🛑 Stop Attendance"** to send an immediate `stop_signal` which breaks the and terminates the thread.
6.2. **Guaranteed Release:** Release hardware hardware and force-close all GUI windows. Execute a 15-cycle OpenCV event pump to ensure prompt window destruction in Linux environments.

---
*Optimized Algorithm: Technical summary designed for high-precision, low-latency attendance automation.*
