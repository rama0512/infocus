
import io
import numpy as np
from PIL import Image
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = str(BASE_DIR / "face_landmarker.task")
print(MODEL_PATH)

base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1)

def get_iris_coordinates(data) -> dict:
    with vision.FaceLandmarker.create_from_options(options) as landmarker:
        # Load the raw bytes directly into PIL
        image = Image.open(io.BytesIO(data))
        
        # Force it to RGB format directly (Replaces cv2.cvtColor)
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        w, h = image.size
        
        # Convert directly to a NumPy array for MediaPipe
        rgb_image = np.array(image)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        
        results = landmarker.detect(mp_image)
        
        if results.face_landmarks:
            face_landmarks = results.face_landmarks[0]             
            coordinates = {}
            for idx in [468, 473]:
                lm = face_landmarks[idx]
                px, py = int(lm.x * w), int(lm.y * h)
                coordinates[idx] = (px, py)
            print(coordinates)
            return {"status":coordinates}
            
        print("No face detected")
        return {"status":"face out of frame"}
