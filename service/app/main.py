import os
import httpx
import asyncio
from fastapi import FastAPI

from app.redis_queue import push_cheating_event
from app.consumer import main as consumer_main

app = FastAPI()

background_tasks = set()

@app.on_event("startup")
async def startup_event():
    task = asyncio.create_task(consumer_main())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
)


@app.post("/cheating-event")
async def receive_cheating_event(payload: dict):
    await push_cheating_event(payload)

    return {
        "status": "queued",
        "message": "Cheating event added to response queue"
    }




@app.post("/send-to-backend")
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