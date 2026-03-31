import cv2
import os
import time

class FaceCapturer:
    def __init__(self, dataset_path="dataset"):
        self.dataset_path = dataset_path
        os.makedirs(self.dataset_path, exist_ok=True)
        # Load Haar Cascade for quick face detection during capture
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def capture_faces(self, name, num_images=5):
        """
        Captures images of a user using the webcam.
        Only saves images where a face is clearly detected.
        """
        user_dir = os.path.join(self.dataset_path, name)
        os.makedirs(user_dir, exist_ok=True)

        print(f"\n[INFO] Camera initializing... Please look directly at the lens.")
        
        # Open webcam
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            print("[ERROR] Could not open webcam. Ensure it's connected and not used by another app.")
            return False

        # Pre-capture delay
        for i in range(3, 0, -1):
            print(f"[INFO] Taking first picture in {i}...")
            time.sleep(1)

        count = 0
        while count < num_images:
            ret, frame = video_capture.read()
            if not ret:
                print("[ERROR] Failed to grab frame.")
                break

            # Process frame for face detection (Haar Cascade is faster for just detection)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            display_frame = frame.copy()
            
            # If face is detected, save the frame
            if len(faces) > 0:
                # Draw indicator on display frame
                for (x, y, w, h) in faces:
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Save the CLEAN frame
                img_name = os.path.join(user_dir, f"{name}_{count}.jpg")
                cv2.imwrite(img_name, frame)
                count += 1
                print(f"[PROGRESS] Captured image {count}/{num_images}")
                time.sleep(0.5) # Slight delay between valid captures
            else:
                cv2.putText(display_frame, "Face Not Detected! Please center your face.", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Overlay status
            cv2.putText(display_frame, f"Capturing for: {name}", (20, 430), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Registration Capture Module', display_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[INFO] Capture interrupted by user.")
                break

        video_capture.release()
        cv2.destroyAllWindows()
        
        if count < num_images:
            print(f"[WARNING] Only captured {count} images. You may need to re-register.")
            return count > 0
            
        return True
