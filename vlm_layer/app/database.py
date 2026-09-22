
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent # this will give you the directory of the current file
#print(f"BASE_DIR: {BASE_DIR}")
# 1. Get the current environment (default to 'development' if not set)
env = os.getenv("APP_ENV", "development")
# 2. Load the specific file (e.g., .env.development or .env.production)
load_dotenv(BASE_DIR/f".env.{env}")

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')  # PostgreSQL default port is 5432
DB_NAME = os.getenv('DB_NAME')

# 3. Access your variables as usual
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"ssl": "require"}
)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
