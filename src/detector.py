import face_recognition
import cv2
import numpy as np
from datetime import datetime

class FaceDetector:
    def __init__(self, encoder, attendance_manager):
        self.encoder = encoder
        self.attendance_manager = attendance_manager
        
        # Load known encodings
        self.known_face_encodings, self.known_face_names = self.encoder.load_encodings()

    def start_recognition(self, course_id=None):
        """Starts the webcam and recognizes faces in real-time."""
        # Load latest encodings from file
        self.known_face_encodings, self.known_face_names = self.encoder.load_encodings()
        
        if not self.known_face_encodings:
            print("[ERROR] No encodings loaded. Please register users first.")
            return

        print("\n[INFO] Starting video stream for Live Attendance...")
        print("[INFO] Press 'q' to stop tracking.\n")
        
        # Open webcam
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            print("[ERROR] Could not open webcam.")
            return

        # Tracking for auto-close feature
        last_success_time = None
        success_message = ""

        # Optimization: process every other frame
        process_this_frame = True

        while True:
            # Grab a single frame of video
            ret, frame = video_capture.read()
            if not ret:
                print("[ERROR] Failed to grab frame.")
                break

            # Only process every other frame to save time
            if process_this_frame:
                # Resize frame to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                confidence_scores = []

                for face_encoding in face_encodings:
                    name = "Unknown"
                    confidence = 0.0

                    if len(self.known_face_encodings) > 0:
                        # Increased tolerance to 0.6 for better detection in varying light
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                        
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]
                            
                            # Calculate a pseudo-confidence score
                            distance = face_distances[best_match_index]
                            confidence = max(0, min(100, round((1.0 - distance) * 100, 2)))

                            # Mark attendance if confidence > threshold
                            if confidence > 50.0:
                                success = self.attendance_manager.mark_attendance(name, course_id=course_id)
                                if success:
                                    last_success_time = datetime.now()
                                    success_message = f"ATTENDANCE MARKED: {name}"
                            else:
                                name = "Unknown"
                                
                    face_names.append(name)
                    confidence_scores.append(confidence)

            process_this_frame = not process_this_frame

            # Display the results
            font = cv2.FONT_HERSHEY_DUPLEX
            for (top, right, bottom, left), name, confidence in zip(face_locations, face_names, confidence_scores):
                # Scale back up face locations
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Choose color based on recognition status
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(frame, (left, bottom - 45), (right, bottom), color, cv2.FILLED)
                
                label_name = f"{name} ({confidence}%)" if name != "Unknown" else "Unknown"
                cv2.putText(frame, label_name, (left + 6, bottom - 20), font, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, datetime.now().strftime("%H:%M:%S"), (left + 6, bottom - 4), font, 0.4, (255, 255, 255), 1)

            # --- Visual Feedback & Auto-Close Logic ---
            if last_success_time:
                elapsed = (datetime.now() - last_success_time).total_seconds()
                if elapsed < 3.0:
                    # Draw a large success banner
                    cv2.rectangle(frame, (0, 0), (frame.shape[1], 100), (0, 255, 0), cv2.FILLED)
                    cv2.putText(frame, success_message, (50, 65), font, 1.2, (255, 255, 255), 3)
                    cv2.putText(frame, f"Closing in {int(4-elapsed)}s...", (frame.shape[1]-200, 150), font, 0.7, (0, 255, 0), 2)
                else:
                    # Automatically close after the success message duration
                    print(f"[INFO] Auto-closing session for {success_message}")
                    break

            # Display timestamp at the corner
            cv2.putText(frame, f"System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow('Face Recognition Live Tracking', frame)

            # Hit 'q' to quit manually
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()
