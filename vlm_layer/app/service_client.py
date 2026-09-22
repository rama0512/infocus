import httpx
import os
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent
#SETTING ENVIRONMENT FOR PROD OR DEV DEPENDING ON WHERE WE ARE DEPLOYING
env = os.getenv("APP_ENV", "development")
load_dotenv(BASE_DIR/f".env.{env}")
SERVICE_URL = os.getenv(
    "CHEATING_SERVICE_URL",
    "http://localhost:8001/cheating-event"
)
print(f"[SERVICE CLIENT] SERVICE_URL: {SERVICE_URL}")
async def send_cheating_event(payload: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            SERVICE_URL,
            json=payload,
        )
        print("response",response.status_code)
        response.raise_for_status()