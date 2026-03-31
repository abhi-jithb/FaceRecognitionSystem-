# Algorithm: Face Recognition-Based Attendance System

This document outlines the step-by-step logic and mathematical flow of the attendance system, structured for academic documentation and technical presentations.

---

## 1. Initialization
1.1. **Import Core Libraries:** Load `OpenCV` (video processing), `face_recognition` (ML engine), `Pandas` (data handling), `NumPy` (math), and `sqlite3` (database).
1.2. **System Environment Setup:** Verify the existence of the `/dataset`, `/database`, and `/attendance` directories.
1.3. **Database Connection:** Establish a persistent connection to `attendance.db` and initialize the `students` (mapping) and `attendance` (logging) tables.
1.4. **Encoding Pre-loading:** Retrieve all unique facial embeddings (128-D vectors) and associated names from the database into the system's runtime memory for instantaneous matching.
1.5. **Hardware Activation:** Initialize the primary webcam capture object using CV2.

## 2. User Interaction / Registration
2.1. **CLI Display:** Present the administrative dashboard with command-line options.
2.2. **Input Handling:** Wait for a user-specified trigger:
   * **Option 1:** Trigger "Phase 1: Face Registration."
   * **Option 2:** Trigger "Phase 2 & 3: Live Detection and Recognition."
   * **Option 3:** Trigger "Phase 6: Automatic Report Generation."
   * **Option 4:** Terminate system execution.

## 3. Phase 1: Face Registration
3.1. **Identity Input:** Prompt the administrator to enter a unique Student Name.
3.2. **Image Acquisition:** Open the webcam feed and capture 5 sequential frames of the student's face.
3.3. **Face Localization:** Use the HOG (Histogram of Oriented Gradients) model to detect the face within each captured frame.
3.4. **Feature Extraction:** Convert normalized facial images into a structural 128-dimensional numeric vector (encoding).
3.5. **Data Persistence:** Save the raw images to `/dataset/Name/` and store the averaged 128D encoding directly into the SQLite `students` table as a BLOB.

## 4. Phase 2: Face Detection
4.1. **Stream Capture:** Acquire real-time video frames from the webcam at a standard resolution (e.g., 640x480).
4.2. **Preprocessing (Optimization):** Resize the frame to 1/4th its original size to reduce computational overhead on the CPU.
4.3. **Color Space Conversion:** Convert the frame from BGR (OpenCV default) to RGB (Required by dlib/face_recognition).
4.4. **HOG Modeling:** Execute the HOG detection algorithm to identify all facial bounding boxes present in the frame.

## 5. Phase 3: Face Recognition
5.1. **Live Encoding:** Compute the 128D facial encoding for every face detected in the live frame.
5.2. **Distance Calculation:** Use **Euclidean Distance** to measure the variance between the live encoding and the pre-loaded database encodings.
   * *Formula:* $d(p, q) = \sqrt{\sum_{i=1}^{n} (p_i - q_i)^2}$
5.3. **Similarity Comparison:** Apply a strict threshold (0.5). If the minimum distance is below 0.5, a "Match" is confirmed.
5.4. **Confidence Scoring:** Convert the distance into a percentage: $Confidence = \max(0, (1 - distance) \times 100)$.
5.5. **Classification:** 
   * If Match found → Retrieve Name; Set status to "Recognized".
   * If Distance > Threshold → Assign identity as "Unknown".

## 6. Phase 4: Attendance Marking
6.1. **Verification Logic:** Receive the recognized Name from Phase 3.
6.2. **Daily Unique Check:** Query the `attendance` table using the current `Name` and `Current Date`.
6.3. **Attendance Insertion:** 
   * If record count == 0 → Insert row: `(Name, Date, Time)`.
   * If record count > 0 → Reject entry (Duplicate Prevention).
6.4. **Visual Feedback:** Render the name, confidence score, and timestamp on the GUI window in real-time.

## 7. Phase 5: Database Management
7.1. **Schema Integrity:** Ensure the SQLite database maintains a relational link between student metadata and their time-stamped attendance logs.
7.2. **Persistence Guarantee:** Commit every SQL transaction immediately to ensure no data loss during unexpected system shutdowns.
7.3. **Memory Syncing:** Periodically re-sync runtime encodings with the database if new users are registered during a session.

## 8. Phase 6: Report Generation
8.1. **Data Retrieval:** Use SQL `SELECT` queries to extract attendance logs based on the desired frequency (Daily or Monthly).
8.2. **DataFrame Transformation:** Load the SQL result set into a `Pandas DataFrame` for structural manipulation.
8.3. **CSV Compilation:** Export the DataFrame to a `.csv` file format stored in the `/attendance` directory with a timestamped filename (e.g., `daily_report_2026-03-31.csv`).

## 9. End of Algorithm
9.1. **Loop Continuity:** Return to Phase 2 to continue tracking the video stream.
9.2. **Resource Release:** Upon user exit, release the webcam hardware and gracefully close the SQLite database connection.
9.3. **Final Status:** Provide a summary of the session: Total registrations and total marked attendance before termination.
