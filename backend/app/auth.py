from datetime import datetime, timedelta, timezone
import jwt
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
env = os.getenv("APP_ENV", "development")
load_dotenv(BASE_DIR/f".env.{env}")
# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = SECRET_KEY 
ALGORITHM = ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 300
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)