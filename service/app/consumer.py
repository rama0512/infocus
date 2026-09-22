import os
import asyncio
import httpx
import redis.exceptions

from app.redis_queue import get_cheating_event


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
)


async def send_to_backend(event: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/cheating-response",
                json=event
            )

            response.raise_for_status()

            print("Event sent to backend")
    except httpx.RequestError as e:
        print(f"Backend connection error: {e}")
    except httpx.HTTPStatusError as e:
        print(f"Backend returned error: {e}")


async def main():
    print("Consumer started. Waiting for events...")

    while True:
        try:
            event = await get_cheating_event()

            if event:
                print("Received from Redis:")
                print(event)

                await send_to_backend(event)
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            print(f"Redis connection error: {e}")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Unexpected consumer error: {e}")
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())