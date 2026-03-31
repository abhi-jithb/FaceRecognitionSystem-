# Face Recognition-Based Attendance System

---

## 📚 TABLE OF CONTENTS

1. [Introduction](#1-introduction)
2. [Problem Statement](#2-problem-statement)
3. [Objectives of the Project](#3-objectives-of-the-project)
4. [Literature Review](#4-literature-review)
5. [Proposed Methodology](#5-proposed-methodology)
6. [System Architecture](#6-system-architecture)
7. [Data Flow Diagram](#7-data-flow-diagram)
8. [Modules Used](#8-modules-used)
9. [Features and Their Purpose](#9-features-and-their-purpose)
10. [Algorithms Used](#10-algorithms-used)
11. [Feature-wise Working with Code Mapping](#11-feature-wise-working-with-code-mapping)
12. [Project Workflow](#12-project-workflow-step-by-step-execution)
13. [Input and Output Specification](#13-input-and-output-specification)
14. [Test Cases](#14-test-cases)
15. [Software Requirements](#15-software-requirements)
16. [Hardware Requirements](#16-hardware-requirements)
17. [Advantages of the System](#17-advantages-of-the-system)
18. [Limitations](#18-limitations)
19. [Future Enhancements](#19-future-enhancements)
20. [Conclusion](#20-conclusion)

---

## 1. Introduction
The **Face Recognition-Based Attendance System** is an automated solution designed to manage attendance records using biometric identification. By utilizing computer vision and machine learning, the system identifies individuals through a live webcam feed and logs their presence in a database. This eliminates the need for manual record-keeping, reduces time consumption, and ensures high accuracy in attendance tracking.

## 2. Problem Statement
Traditional attendance systems, such as paper-based registers or card-swiping methods, suffer from several drawbacks:
* **Time Consumption:** Manually calling out names or swiping cards takes significant time, especially in large groups.
* **Proxy Attendance:** Students or employees can mark attendance for absent peers (buddy punching).
* **Data Loss:** Physical registers are prone to damage or loss.
* **Manual Effort:** Compiling monthly reports from manual logs is tedious and error-prone.

## 3. Objectives of the Project
* To build a completely automated, touch-less attendance system.
* To ensure secure and accurate identification using facial biometrics.
* To prevent duplicate attendance entries for the same person on the same day.
* To provide a user-friendly interface for registration and report generation.
* To generate automated CSV reports for administrative analysis.

## 4. Literature Review
Facial recognition has evolved from simple geometric models to deep learning-based approaches. Modern libraries like `face_recognition` utilize **dlib's state-of-the-art face recognition** built with deep learning. 
* **Detection:** Histogram of Oriented Gradients (HOG) is widely used for its balance between speed and accuracy on standard CPUs.
* **Recognition:** Deep ResNet architectures can map a face into a 128-dimensional vector (embedding) where distance between vectors corresponds to facial similarity.

## 5. Proposed Methodology
The system follows a modular approach:
1. **Enrollment:** Capturing 5 images per user to create a robust facial profile.
2. **Preprocessing:** Resizing and converting BGR frames to RGB for the recognition engine.
3. **Face Analysis:** Detecting facial landmarks and computing unique 128-d encodings.
4. **Database Comparison:** Calculating Euclidean distance between live encodings and stored encodings.
5. **Logging:** Using SQLite's relational model to store timestamps only if a match exceeds the confidence threshold and no prior record exists for the day.

## 6. System Architecture
The architecture is designed to be modular and scalable:
* **UI Layer:** Python CLI (main.py) and OpenCV Windows.
* **Processing Layer:** Logic modules for Capture, Encoding, and Detection.
* **Data Layer:** SQLite Database and File System for image datasets.

```text
[ User ] <--> [ OpenCV UI ]
                  |
        [ Recognition Engine ] <--> [ SQLite DB ]
                  |
        [ Dataset/Encodings ] <--> [ Local Storage ]
```

## 7. Data Flow Diagram
The flow of information through the system:

1.  **User Input:** Student enters name; Camera triggers capture.
2.  **Detection:** OpenCV identifies bounding boxes for faces in the frame.
3.  **Encoding:** The system extracts unique facial features into a 128D numeric vector.
4.  **Comparison:** The live vector is matched against vectors in the Database.
5.  **Validation:** If match found & confidence > 55%, the Attendance Manager is triggered.
6.  **Persistence:** SQLite checks for duplicates and stores the `(Name, Date, Time)` record.
7.  **Report:** Pandas fetches SQL data and exports it as a CSV file.

## 8. Modules Used
* **`capture.py`**: Handles webcam interfacing for registration.
* **`encoder.py`**: Processes raw images into mathematical embeddings.
* **`detector.py`**: The real-time engine that detects and recognizes faces.
* **`database.py`**: Manages the SQLite connection and table operations.
* **`attendance_manager.py`**: Exports reports and validates attendance logic.

## 9. Features and Their Purpose

### Feature: Face Registration
* **Purpose:** To enroll new users into the system.
* **File:** `src/capture.py`
* **Working:** Captures 5 sequential frames of the user with text feedback, saving them to `dataset/Name/`.

### Feature: Real-Time Face Detection
* **Purpose:** To locate faces within the live video stream.
* **File:** `src/detector.py`
* **Working:** Uses the HOG (Histogram of Oriented Gradients) model to identify facial bounding boxes in a downscaled 1/4th frame for speed.

### Feature: Attendance Auto-Logging
* **Purpose:** To record participation without manual intervention.
* **File:** `src/attendance_manager.py`
* **Working:** Once a face is recognized above the threshold, it sends a transaction to the DB.

### Feature: Proxy/Duplicate Prevention
* **Purpose:** To ensure a person is marked present only once per day.
* **File:** `src/database.py`
* **Working:** Uses a `UNIQUE(name, date)` constraint in the SQLite schema to reject redundant entries.

## 10. Algorithms Used

### Face Detection (HOG + Linear SVM)
The system uses the **HOG** method from dlib. 
1. The image is simplified into gradient orientations.
2. A sliding window checks for "face-like" gradient patterns.
3. It is highly efficient for CPU-based real-time processing.

### Face Recognition (Deep Residual Network)
1. **Encoding:** A pre-trained ResNet model takes a face image and outputs **128 facial measurements** (encodings).
2. **Euclidean Distance:** The system calculates the distance between the live vector and stored vectors.
3. **Thresholding:** If `distance < 0.5`, it is considered a match. Confidence is calculated as `(1 - distance) * 100`.

### Attendance Logic Algorithm
1. Receive recognized name.
2. Query `attendance` table for the current `name` and current `date`.
3. If search returns empty → Insert new record.
4. Else → Do nothing (already marked).

### CSV Export Algorithm
1. Use SQL `SELECT` to fetch records filtered by today's date or current month.
2. Load the result into a `Pandas DataFrame`.
3. Call `df.to_csv()` to save the file in the `/attendance` directory.

## 11. Feature-wise Working with Code Mapping

| Feature | Core Function | File Path | Responsibility |
| :--- | :--- | :--- | :--- |
| **Registration** | `capture_faces()` | `src/capture.py` | OpenCV Webcam capture UI |
| **Encoding** | `generate_encodings_for_user()` | `src/encoder.py` | Feature extraction (128D) |
| **Detection** | `face_locations()` | `src/detector.py` | Bounding box identification |
| **Recognition** | `compare_faces()` | `src/detector.py` | Similarity calculation |
| **Persistence** | `mark_attendance()` | `src/database.py` | SQLite Insert/Unique check |
| **Reporting** | `export_daily_report()` | `src/attendance_manager.py` | Pandas CSV Generation |

## 12. Project Workflow (Step-by-step execution)
1.  **Initialize:** Run `main.py`; Database auto-creates folders if missing.
2.  **Register:** Admin selects Option 1, enters a name, and photos are taken.
3.  **Process:** System immediately computes the average encoding for that user.
4.  **Track:** Admin selects Option 2. The live camera overlay shows "Tracking..."
5.  **Identify:** As soon as the user looks at the camera, their name/confidence appears in green.
6.  **Log:** The terminal prints `[SUCCESS]` when the DB entry is committed.
7.  **Report:** Admin selects Option 3 to generate CSV sheets for records.

## 13. Input and Output Specification
* **Input:**
    * Student Name (String via keyboard)
    * Live Video Stream (640x480 pixel frames via Webcam)
    * Existing Dataset (JPG/PNG images in `dataset/` folder)
* **Output:**
    * Real-time GUI feed with bounding boxes and labels.
    * `attendance.db` (Binary SQLite database)
    * `attendance/daily_report_YYYY-MM-DD.csv` (Spreadsheet file)

## 14. Test Cases

| Test Case ID | Description | Input | Expected Output | Status |
| :--- | :--- | :--- | :--- | :--- |
| TC-01 | New User Registration | Valid Name + Face | 5 Images saved + Encoding saved to DB | PASS |
| TC-02 | Recognition of Known Face | Enrolled Student in frame | Name displayed + Green Box | PASS |
| TC-03 | Unknown Face Detection | Stranger in frame | "Unknown" displayed + Red Box | PASS |
| TC-04 | Duplicate Prevention | Same face later in the day | Recognized but NO new DB record | PASS |
| TC-05 | Missing Camera | Run system without Webcam | Clean error message printed | PASS |

## 15. Software Requirements
* **Operating System:** Windows 10+, macOS, or Linux (Ubuntu recommended).
* **Language:** Python 3.8 or higher.
* **Libraries:** 
    * `opencv-python` (UI and Video)
    * `face_recognition` (ML Core)
    * `pandas` (Report Engine)
    * `numpy` (Math)
    * `sqlite3` (Embedded DB)

## 16. Hardware Requirements
* **Processor:** Intel i3 or better (i5 recommended for higher FPS).
* **RAM:** 4GB minimum (8GB recommended).
* **Camera:** Standard 720p/1080p Integrated or External USB Webcam.
* **Storage:** 500MB free space for dataset and library weights.

## 17. Advantages of the System
* **Accuracy:** Uses deep learning embeddings which are highly resistant to variations in lighting or expression.
* **Speed:** Processes every alternate frame and resizes input to maintain 20+ FPS.
* **Scalability:** SQLite and modular logic allow for hundreds of students without significant lag.
* **Safety:** Touch-free identification is ideal for hygienic environments.

## 18. Limitations
* **Lighting Dependency:** Extreme low light may reduce detection accuracy.
* **Camera Angle:** Requires a relatively clear frontal or near-frontal view.
* **Resource Usage:** Training/Encoding large datasets can be CPU intensive.

## 19. Future Enhancements
* **Multi-Face Marking:** Optimizing the loop to mark 10+ students simultaneously in a classroom.
* **Anti-Spoofing:** Adding liveness detection (blink detection) to prevent photo-based fraud.
* **Cloud Integration:** Syncing the local SQLite DB with a remote Firebase/AWS database.
* **Web UI:** Developing a React/Flask dashboard for administrative remote management.

## 20. Conclusion
The **Face Recognition-Based Attendance System** successfully implements a robust, automated biometric solution. By combining dlib's recognition accuracy with SQLite's data integrity, it provides a professional-grade MVP suitable for schools, offices, and small-to-medium organizations looking to modernize their operational efficiency.

---
**Project Lead:** AI Backend Developer
**Status:** MVP Version 1.0 Complete
