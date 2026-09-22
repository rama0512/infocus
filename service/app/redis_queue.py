import os
import json
from pathlib import Path

from dotenv import load_dotenv
import redis.asyncio as aioredis


BASE_DIR = Path(__file__).resolve().parent.parent

env = os.getenv("APP_ENV", "development")

load_dotenv(BASE_DIR / f".env.{env}")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = aioredis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_timeout=None,
    socket_keepalive=True
)


async def push_cheating_event(payload: dict):
    json_message = json.dumps(payload)

    await redis_client.rpush(
        "cheating_response_queue",
        json_message
    )


async def get_cheating_event():
    result = await redis_client.blpop(
        "cheating_response_queue",
        timeout=0
    )

    if result is None:
        return None

    _, message = result

    return json.loads(message)
