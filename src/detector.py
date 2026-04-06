import face_recognition
import cv2
import numpy as np
from datetime import datetime
import os
import threading

class FaceDetector:
    def __init__(self, encoder, attendance_manager):
        self.encoder = encoder
        self.attendance_manager = attendance_manager
        self.stop_event = threading.Event() # Flag to stop the loop externally
        self.is_active = False   # Flag to track if the session is actually running
        
        # Load known encodings
        self.known_face_encodings, self.known_face_names = self.encoder.load_encodings()

    def stop_recognition(self):
        """Sets the signal to stop the recognition loop."""
        print("[INFO] Stop signal triggered from UI.")
        self.stop_event.set()

    def start_recognition(self, course_id=None):
        """Starts the webcam and recognizes faces in real-time."""
        self.stop_event.clear() # Reset signal
        self.is_active = True    # Mark as active
        
        # Load latest encodings from file
        self.known_face_encodings, self.known_face_names = self.encoder.load_encodings()
        
        # If we have no encodings, attempt one sync in case images were recently added
        if not self.known_face_encodings:
            print("[INFO] No encodings in cache. Attempting to sync from dataset...")
            self.encoder._sync_all_encodings()
            self.known_face_encodings, self.known_face_names = self.encoder.load_encodings()

        print(f"\n[INFO] Loaded {len(self.known_face_encodings)} face encodings for matching.")
        
        if not self.known_face_encodings:
            print("[ERROR] Still no encodings loaded. Please register users first.")
            return

        print("\n[INFO] Starting video stream for Live Attendance...")
        print("[INFO] Press 'q' or use the Web UI to stop tracking.\n")
        
        try:
            import time
            print("[INFO] Initializing webcam... (may take a moment)")
            # Small delay to give OS time to release previous handles
            time.sleep(1.0) 
            
            # Fedora/Linux Stabilization: Force kill any existing locks on /dev/video0 
            # to ensure the device is available for this new session.
            if os.name == 'posix':
                try: 
                    os.system("fuser -k /dev/video0 > /dev/null 2>&1")
                    print("[INFO] Cleared any existing hardware locks on /dev/video0")
                except: pass

            # Open webcam with retry
            video_capture = None
            for i in range(5): # Increase to 5 attempts
                # Use CAP_V4L2 backend on Linux if possible for better resource management
                try:
                    video_capture = cv2.VideoCapture(0, cv2.CAP_V4L2) if os.name == 'posix' else cv2.VideoCapture(0)
                except:
                    video_capture = cv2.VideoCapture(0)

                if video_capture is not None and video_capture.isOpened():
                    break
                
                if video_capture: video_capture.release()
                print(f"[RETRY] Camera busy, retrying in 2.0s... ({i+1}/5)")
                time.sleep(2.0)

            if not video_capture or not video_capture.isOpened():
                print("[ERROR] Could not open webcam after multiple attempts.")
                return

            print("[INFO] Webcam opened successfully.")

            # Camera Warmup - critical for auto-exposure
            for _ in range(15):
                video_capture.read()

            # Tracking for feedback
            last_success_time = None
            success_message = ""

            # Optimization: process every other frame
            process_this_frame = True

            while not self.stop_event.is_set():
                # Grab a single frame of video
                ret, frame = video_capture.read()
                if not ret:
                    print("[ERROR] Failed to grab frame.")
                    # Retry briefly instead of immediate exit
                    time.sleep(0.5)
                    continue

                # SIGNAL CHECK: Check again after frame grab
                if self.stop_event.is_set(): break

                # Only process every other frame to save time
                face_locations = []
                face_names = []
                confidence_scores = []

                if process_this_frame:
                    # Resize frame to 1/4 size for faster face recognition processing
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    
                    # Find all the faces and face encodings in the current frame of video
                    face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                    
                    # SIGNAL CHECK: Check again after heavy detection
                    if self.stop_event.is_set(): break

                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                    for face_encoding in face_encodings:
                        if self.stop_event.is_set(): break # Don't start marking attendance if stopping
                        
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
                
                # STATUS MESSAGE: If no faces detected, show waiting status
                if len(face_locations) == 0:
                    cv2.putText(frame, "STATUS: Waiting for people...", (200, 450), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

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

                # --- Visual Feedback & Manual Stop Logic ---
                if last_success_time:
                    elapsed = (datetime.now() - last_success_time).total_seconds()
                    if elapsed < 3.0:
                        # Draw a large success banner
                        cv2.rectangle(frame, (0, 0), (frame.shape[1], 100), (0, 255, 0), cv2.FILLED)
                        cv2.putText(frame, success_message, (50, 65), font, 1.2, (255, 255, 255), 3)
                    else:
                        # Clear success message after 3 seconds but keep tracking
                        last_success_time = None
                        success_message = ""

                # Display timestamp at the corner
                cv2.putText(frame, f"Live Tracking System | System Time: {datetime.now().strftime('%H:%M:%S')}", 
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                cv2.imshow('Face Recognition Live Tracking', frame)

                # Hit 'q' to quit manually
                if cv2.waitKey(10) & 0xFF == ord('q'): # Increased waitKey slightly for event handling
                    break

        except Exception as e:
            print(f"[ERROR] Exception in recognition loop: {e}")
        finally:
            print("[INFO] Cleaning up camera resources...")
            self.is_active = False 
            
            # 1. First destroy the named window specifically
            try:
                cv2.destroyWindow('Face Recognition Live Tracking')
                print("[INFO] Recognition window destroyed.")
            except:
                pass
            
            # 2. Release handle to the webcam
            if 'video_capture' in locals() and video_capture:
                video_capture.release()
                print("[INFO] Webcam hardware released.")
            
            # 3. Aggressive event pumping for Linux window managers
            cv2.destroyAllWindows()
            for _ in range(50): # Even more cycles
                cv2.waitKey(20) # Longer wait to let OS process thread messaging
            
            self.stop_event.clear() 
            print("[INFO] Session fully terminated.")
