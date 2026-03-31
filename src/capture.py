import cv2
import os
import time

class FaceCapturer:
    def __init__(self, dataset_path="dataset"):
        self.dataset_path = dataset_path
        os.makedirs(self.dataset_path, exist_ok=True)

    def capture_faces(self, name, num_images=5):
        """
        Captures images of a user using the webcam.
        Saves them in dataset/<name>/ folder.
        """
        user_dir = os.path.join(self.dataset_path, name)
        os.makedirs(user_dir, exist_ok=True)

        print(f"\n[INFO] Camera initializing... Please look directly at the lens.")
        
        # Open webcam
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            print("[ERROR] Could not open webcam. Make sure your camera is connected and not used by another app.")
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

            # Add helpful text to the frame during capture
            display_frame = frame.copy()
            cv2.putText(display_frame, f"Capturing for: {name}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(display_frame, f"Photos taken: {count}/{num_images}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Show the frame
            cv2.imshow('Registration Capture Module', display_frame)
            
            # Save the clean (un-texted) frame
            img_name = os.path.join(user_dir, f"{name}_{count}.jpg")
            cv2.imwrite(img_name, frame)
            
            count += 1
            time.sleep(1) # wait 1 second between captures
            
            # Exit option
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()
        return True
