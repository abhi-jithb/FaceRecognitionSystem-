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

        if self.face_cascade.empty():
            print("[ERROR] Haar Cascade not loaded. Check OpenCV installation.")
            return False

        print(f"\n[INFO] Camera initializing... Please look directly at the lens.")
        
        # Fedora/Linux Stabilization: Force kill any existing locks on /dev/video0
        if os.name == 'posix':
            try:
                os.system("fuser -k /dev/video0 > /dev/null 2>&1")
                print("[INFO] Cleared hardware locks for registration.")
            except: pass

        # Open webcam with small retry mechanism
        video_capture = None
        for attempt in range(5): # Increase to 5 attempts
            # Use CAP_V4L2 backend on Linux if possible for better resource management
            try:
                video_capture = cv2.VideoCapture(0, cv2.CAP_V4L2) if os.name == 'posix' else cv2.VideoCapture(0)
            except:
                video_capture = cv2.VideoCapture(0)
                
            if video_capture is not None and video_capture.isOpened():
                break
            
            if video_capture: video_capture.release()
            print(f"[RETRY] Camera busy or initializing, retrying in 2.0s... ({attempt+1}/5)")
            time.sleep(2.0)
            
        if not video_capture or not video_capture.isOpened():
            print("[ERROR] Could not open webcam. Ensure it's connected and not used by another app.")
            return False

        # Camera Warmup: grab a few frames first
        if video_capture:
            for _ in range(10):
                video_capture.read()

        try:
            # Pre-capture delay
            start_time = time.time()
            while time.time() - start_time < 3:
                ret, frame = video_capture.read()
                if ret:
                    display_frame = frame.copy()
                    cv2.putText(display_frame, f"Starting in {int(4 - (time.time() - start_time))}...", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    cv2.imshow('Registration Capture Module', display_frame)
                    cv2.waitKey(1)

            count = 0
            last_capture_time = 0
            while count < num_images:
                ret, frame = video_capture.read()
                if not ret:
                    print("[ERROR] Failed to grab frame.")
                    break

                # Process frame for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Broader detection parameters for registration phase
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4) 

                display_frame = frame.copy()
                
                # If face is detected and enough time has passed since last capture
                if len(faces) > 0 and (time.time() - last_capture_time > 0.8):
                    # Draw indicator on display frame
                    for (x, y, w, h) in faces:
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        # Label during progress
                        cv2.putText(display_frame, f"Captured {count+1}", (x, y-10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    # Save the CLEAN frame
                    img_name = os.path.join(user_dir, f"{name}_{count}.jpg")
                    cv2.imwrite(img_name, frame)
                    count += 1
                    last_capture_time = time.time()
                    print(f"[PROGRESS] Captured image {count}/{num_images}")
                elif len(faces) == 0:
                    cv2.putText(display_frame, "Face Not Detected! Center your face and hold still.", (30, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Overlay status
                cv2.putText(display_frame, f"Registering: {name} ({count}/{num_images})", (20, 450), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                cv2.imshow('Registration Capture Module', display_frame)
                
                # Allow quit via 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("[INFO] Capture interrupted by user.")
                    break
        finally:
            if video_capture:
                video_capture.release()
                print("[INFO] Registration webcam hardware released.")
            # OpenCV Window Cleanup - more aggressive for Linux
            cv2.destroyAllWindows()
            for _ in range(30): 
                cv2.waitKey(1)
            print("[INFO] Registration session closed.")
        
        if count < num_images:
            print(f"[WARNING] Only captured {count} images.")
            return count > 0
            
        return True
