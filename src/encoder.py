import face_recognition
import cv2
import os
import pickle
import numpy as np

class FaceEncoder:
    def __init__(self, db_manager, dataset_path="dataset", encodings_path="encodings/encodings.pkl"):
        self.db_manager = db_manager
        self.dataset_path = dataset_path
        self.encodings_path = encodings_path
        self.known_face_encodings = []
        self.known_face_names = []
        
        os.makedirs(self.dataset_path, exist_ok=True)
        os.makedirs(os.path.dirname(self.encodings_path), exist_ok=True)

    def generate_encodings_for_user(self, name):
        """
        Reads images for A SPECIFIC user, generates their encoding,
        saves to DB and also to the global pkl file.
        """
        print(f"[INFO] Quantifying faces for {name}...")
        
        person_dir = os.path.join(self.dataset_path, name)
        if not os.path.exists(person_dir):
            print(f"[WARNING] No images found for {name}.")
            return False

        user_encodings = []
        for image_name in os.listdir(person_dir):
            image_path = os.path.join(person_dir, image_name)
            try:
                # Load the input image and convert it from BGR (OpenCV) to dlib ordering (RGB)
                image = cv2.imread(image_path)
                if image is None:
                    continue
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Detect faces
                boxes = face_recognition.face_locations(rgb_image, model="hog")
                encodings = face_recognition.face_encodings(rgb_image, boxes)

                if encodings:
                    user_encodings.append(encodings[0])
            except Exception as e:
                print(f"[ERROR] Could not process {image_path}: {e}")

        if not user_encodings:
            print("[ERROR] No face detected in the images captured.")
            return False

        # Take average of encodings to make a single robust representation
        avg_encoding = np.mean(user_encodings, axis=0)
        
        # Save to database
        self.db_manager.update_encoding(name, avg_encoding)
        
        # Update the global lists & file for fast loading
        self._sync_all_encodings()
        print(f"[INFO] Encodings saved for {name}!")
        return True

    def _sync_all_encodings(self):
        """Reads all encodings from the dataset into the .pkl file."""
        self.known_face_encodings = []
        self.known_face_names = []

        if not os.path.exists(self.dataset_path):
            return

        for person_name in os.listdir(self.dataset_path):
            person_dir = os.path.join(self.dataset_path, person_name)
            if not os.path.isdir(person_dir):
                continue
                
            for image_name in os.listdir(person_dir):
                image_path = os.path.join(person_dir, image_name)
                image = cv2.imread(image_path)
                if image is None: continue
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(rgb_image, model="hog")
                encodings = face_recognition.face_encodings(rgb_image, boxes)
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_names.append(person_name)

        data = {"encodings": self.known_face_encodings, "names": self.known_face_names}
        with open(self.encodings_path, "wb") as f:
            f.write(pickle.dumps(data))

    def load_encodings(self):
        """Loads encodings from the pickle file."""
        if not os.path.exists(self.encodings_path):
            self._sync_all_encodings()
            if not os.path.exists(self.encodings_path):
                print("[WARNING] No encodings file found. Please register users first.")
                return [], []
            
        with open(self.encodings_path, "rb") as f:
            data = pickle.loads(f.read())
            
        return data["encodings"], data["names"]
