import os
import json
import time
from dotenv import load_dotenv
from pathlib import Path
from eye_corodinate import get_iris_coordinates
import redis as r
#SETTING ENVIRONMENT FOR PROD OR DEV DEPENDING ON WHERE WE ARE DEPLOYING
env = os.getenv("APP_ENV", "development")
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR/f".env.{env}")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# 2. Initialize the async client
redis_client = r.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
print("ML Worker is live and waiting for images...")

while True:
    # This blocks until an item hits the "image_queue"
    queue_name, raw_message =  redis_client.blpop("image_queue", timeout=0)
    
    try:
        task_data = json.loads(raw_message)
        print(f"\nProcessing frame: {task_data['s3_path']}")
        Bucket=task_data['bucket_name']
        key=task_data['s3_path']
        # --- Simulated ML Task ---
        coords = get_iris_coordinates(Bucket, key)
        if coords:
            print("Left Iris (468):", coords[468])
            print("Right Iris (473):", coords[473])
        else:
            print("No face detected in the image.") 
        """# --- Save to Result Queue ---
        db_payload = {
            "s3_path": task_data['s3_path'],
            "coords": detected_coords,
            "processed_at": time.time()
        }
        r.rpush("nosql_queue", json.dumps(db_payload))
        print(f"Finished. Sent coordinates to NoSQL Queue: {detected_coords}")"""
        
    except Exception as e:
        print(f"Worker Error: {e}")
