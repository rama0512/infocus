import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import redis
import time
import boto3
from dotenv import load_dotenv
from pathlib import Path
from PIL import Image
import io
import os 
"""REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)"""
s3 = boto3.client('s3')
def get_iris_coordinates(Bucket:str, key: str, model_path: str = 'face_landmarker.task') -> dict:
    """
    Detects the left and right iris pixel coordinates from an image.
    Returns a dict like: {468: (x, y), 473: (x, y)} or None if no face is found.
    """
    # 1. Initialize detector options
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1)
    # getting the image from s3 and saving it to a temp file for processing
    
    # 2. Context manager ensures resources are freed immediately after detection
    with vision.FaceLandmarker.create_from_options(options) as landmarker:
        response = s3.get_object(Bucket, key)
        image_bytes = response['Body'].read()
        image = Image.open(io.BytesIO(image_bytes))
        cv_image = cv2.imread(image)
        if cv_image is None:
            raise FileNotFoundError(f"Could not load image from path: {key}")
        # 3. Convert image formats for MediaPipe processing
        h, w, _ = cv_image.shape
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        # 4. Execute detection
        results = landmarker.detect(mp_image)
        
        # 5. Extract coordinates if a face exists
        if results.face_landmarks:
            # MediaPipe guarantees landmarks for the first face are at index 0
            face_landmarks = results.face_landmarks[0] 
            
            # Map target landmark indices to their computed (x, y) pixel locations
            coordinates = {}
            for idx in [468, 473]:  # 468: Left Iris, 473: Right Iris
                lm = face_landmarks[idx]
                px, py = int(lm.x * w), int(lm.y * h)
                coordinates[idx] = (px, py)
                
            return coordinates
            
        return None  # Explicit return if no face is detected