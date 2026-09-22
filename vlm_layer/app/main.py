import asyncio

from fastapi import FastAPI

from app.listener import shared_memory_listener
from app.database import engine, Base
from app.models.vlm_result import VLMResult


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)"""
    asyncio.create_task(
        shared_memory_listener()
    )


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "vlm_layer",
    }