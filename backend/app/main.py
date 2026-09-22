import os
from anyio import to_thread
from time import time
from fastapi import FastAPI, Depends , Query , HTTPException , status, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.database import SessionLocal, engine,get_db
import app.models as models 

import schemas
import boto3
import aioboto3
from botocore.config import Config
import base64
from datetime import datetime, timedelta, timezone
import os
import io
import struct

import jwt
from hashing import hash_password, verify_password
from dotenv import load_dotenv
from auth import create_access_token
from pathlib import Path
#from redis_queue import upload_webcam_image_manual_queue
import asyncio
from eye_corodinate import get_iris_coordinates
from multiprocessing.shared_memory import SharedMemory
from ipc_config import (
    SHM_NAME, TOTAL_SHM_SIZE, RING_HEADER_SIZE, SLOT_SIZE, 
    META_HEADER_SIZE, MAX_S3_PATH_LEN, MAX_IMG_SIZE, NUM_SLOTS
)
from shared_memory_ring import init_shared_memory, write_to_ring_buffer,shm

BASE_DIR = Path(__file__).resolve().parent
#SETTING ENVIRONMENT FOR PROD OR DEV DEPENDING ON WHERE WE ARE DEPLOYING
env = os.getenv("APP_ENV", "development")
load_dotenv(BASE_DIR/f".env.{env}")
# setting up imp variables from the .env file
BUCKET = os.getenv("BUCKET")
BUCKETSC=os.getenv("BUCKETSC")
USER = os.getenv("APP_USER")
FRONTEND_URL = os.getenv("FRONTEND_URL")
# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM") 
#limit of concurrent webcam uploads
upload_webcam_ml_workers=5
upload_webcam_workers=10
upload_sc_workers=10
upload_webcam_vlm_workers=5
#setup queue for webcam uploads to avoid memory issues and control concurrency
webcam_ml_queue = asyncio.Queue(maxsize=100)  # Adjust maxsize as needed
webcam_queue = asyncio.Queue(maxsize=100)  # Adjust maxsize as needed
sc_queue = asyncio.Queue(maxsize=100)  # Adjust maxsize as needed
sc_vlm_upload_queue = asyncio.Queue(maxsize=100)  # Adjust maxsize as needed

async def s3_image_upload(worker_id:int,s3_client):
    while True:
        job = await webcam_queue.get()
        try:
            data = job["data"]
            s3_path = job["s3_path"]
            print(f"[worker-{worker_id}] uploading {s3_path}")
            #await s3_client.upload_fileobj(io.BytesIO(data),BUCKET,s3_path,ExtraArgs={'ContentType': 'image/jpeg'})
            await s3_client.put_object(
                Body=data,
                Bucket=BUCKET,
                Key=s3_path,
                ContentType='image/jpeg',
                Metadata={"captured-at-ms": str(job["captured_at_ms"])}
            )
            print(f"[worker-{worker_id}] uploaded {s3_path} successfully")
        except Exception as e:
            print(f"[worker-{worker_id}] upload failed: {e}")
        finally:
            webcam_queue.task_done()

async def s3_sc_upload(worker_id:int,s3_client):
    while True:
        job = await sc_queue.get()
        try:
            data = job["data"]
            s3_path = job["s3_path"]
            print(f"[sc-worker-{worker_id}] uploading {s3_path}")
            await s3_client.put_object(
                Body=data,
                Bucket=BUCKETSC,
                Key=s3_path,
                ContentType='image/jpeg',
                Metadata={"captured-at-ms": str(job["captured_at_ms"])}
            )
            print(f"[sc-worker-{worker_id}] uploaded {s3_path} successfully")
        except Exception as e:
            print(f"[sc-worker-{worker_id}] upload failed: {e}")
        finally:
            sc_queue.task_done()

async def webcam_result_db_upload(result:schemas.webcam_result_create):
    async with SessionLocal() as db:
        try:
            db_result = models.webcam_result(
                s3_path=result.s3_path,
                captured_at_ms=result.captured_at_ms,
                coordinates=result.coordinates
            )
            db.add(db_result)
            await db.commit()
            await db.refresh(db_result)
            print(f"Webcam result saved to DB: {db_result}")
        except Exception as e:
            print(f"Failed to save webcam result to DB: {e}")
        finally:
            await db.close()

async def s3_ml_layer_webcam_image_upload(worker_id:int,s3_client):
    while True:
        job = await webcam_ml_queue.get()
        try:
            data = job["data"]
            s3_path = job["s3_path"]
            captured_at_ms = job["captured_at_ms"]
            #await get_iris_coordinates(data)
            coordinates = await to_thread.run_sync(get_iris_coordinates, data)
            print(
                f"[ml-worker-{worker_id}] Processed {s3_path} "
                f"captured_at_ms={captured_at_ms}: {coordinates}"
            )
            await webcam_result_db_upload(schemas.webcam_result_create(s3_path=s3_path, captured_at_ms=captured_at_ms, coordinates=coordinates))
        except Exception as e:
            print(f"[ml-worker-{worker_id}] upload failed: {e}")
        finally:
            webcam_ml_queue.task_done()

async def vlm_image_upload(worker_id: int, s3_client):
    if shm is None:
        init_shared_memory()
        
    print(f"[vlm-worker-{worker_id}] Initialized. Awaiting frame payloads...")
    
    while True:
        job = await sc_vlm_upload_queue.get()
        s3_path = job["s3_path"]
        img_bytes = job["raw_bytes"]  # Incoming image frame raw binary stream
        captured_at_ms = job["captured_at_ms"]
        
        try:
            success = False
            while not success:
                # Thread offloading ensures your main FastAPI loops never freeze
                success = await asyncio.to_thread(
                    write_to_ring_buffer,
                    s3_path,
                    img_bytes,
                    captured_at_ms,
                )
                if not success:
                    # Quick non-blocking yield back to event loop if queue is full
                    await asyncio.sleep(0.005) 
                    
            print(
                f"[vlm-worker-{worker_id}] Synchronized frame data for path: "
                f"{s3_path}, captured_at_ms={captured_at_ms}"
            )
        except Exception as e:
            print(f"[vlm-worker-{worker_id}] RAM pipeline submission failed: {e}")
        finally:
            sc_vlm_upload_queue.task_done()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # -----------------------------------------------------------------
    # STARTUP LOGIC: Runs BEFORE the server starts accepting requests
    # -----------------------------------------------------------------
    if env == "development":
        model_metadata = models.user.metadata
        print("SQLAlchemy checklist (Direct from Model):", model_metadata.tables.keys())  
        async with engine.begin() as conn:
            await conn.run_sync(model_metadata.create_all)
            print("Tables successfully synced with model.py!")

    # Initialize the single shared session and open the client context
    session = aioboto3.Session()
    async with session.client("s3", config=Config(max_pool_connections=50)) as s3_client:
        
        # Spin up background workers, passing the shared s3_client context down
        for i in range(upload_webcam_workers):
            asyncio.create_task(s3_image_upload(i, s3_client))

        for i in range(upload_sc_workers):
            asyncio.create_task(s3_sc_upload(i, s3_client))

        for i in range(upload_webcam_ml_workers):
            asyncio.create_task(s3_ml_layer_webcam_image_upload(i, s3_client))
        
        for i in range(upload_webcam_vlm_workers):
            asyncio.create_task(vlm_image_upload(i, s3_client))

        # The 'yield' statement hands control back to FastAPI.
        # Your app runs happily inside this block while the S3 context remains open!
        yield
        
    # -----------------------------------------------------------------
    # SHUTDOWN LOGIC: Runs AFTER the server stops accepting requests
    # -----------------------------------------------------------------
    print("Application is shutting down. S3 connection pool safely closed.")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # frontend set as * untill we get the deployed frontend url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


FRAME_TIMESTAMP_HEADER_SIZE = 8


def decode_timestamped_jpeg_frame(message: bytes) -> tuple[int, bytes]:
    if len(message) <= FRAME_TIMESTAMP_HEADER_SIZE:
        raise ValueError("Frame must contain an 8-byte timestamp and JPEG data.")

    captured_at_ms = struct.unpack("!Q", message[:FRAME_TIMESTAMP_HEADER_SIZE])[0]
    image_bytes = message[FRAME_TIMESTAMP_HEADER_SIZE:]
    return captured_at_ms, image_bytes


#web socket for webcam feed
@app.websocket("/ws/webcam")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    #this code segment runs ONLY ONCE when the user connects or reconnects.
    last_saved_time = 0.0  
    #p1:check if token is present else close connection
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        USER = payload.get("username")
        if not USER:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception as e:
        print(f"Token decode error: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await websocket.accept()
    print("!!! Socket Accepted !!!") # Debug 1
    
    try:
        # after this part the while block below runs continuously until the user disconnects.the above segment is not executed for every image. above segment executed only for new connection and reconnection. 
        while True:
            message = await websocket.receive_bytes()
            #denial of Service (DoS) via Unbounded Payload Size
            if len(message)>5*1024*1024:
                await websocket.close(code=status.WS_1009_MESSAGE_TOO_BIG)
                return
            try:
                captured_at_ms, data = decode_timestamped_jpeg_frame(message)
            except ValueError:
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                return
            now = datetime.now()   
            current_time = time()
            # Only save if 2 seconds have passed since the last save
            if current_time - last_saved_time >= 10:   
                #asyncio.create_task(upload_webcam_image(USER, data, BUCKET))
                # Instead of directly calling the upload, we put the job in the queue
                s3_path = (f"{USER}_webcam_{now.year}_{now.month:02d}_{now.day:02d}_{now.strftime('%H%M%S')}.jpg")
                try:
                    # Throws an exception instantly if the queue is full
                    webcam_queue.put_nowait({"s3_path": s3_path, "data": data, "captured_at_ms": captured_at_ms})
                except asyncio.QueueFull:
                    # Log it and move on; do not freeze the websocket
                    print("Warning: Queue full, dropping webcam frame!")
                """await webcam_queue.put({
                    "s3_path": s3_path,
                    "data": data,
                })"""
                try:
                    # Throws an exception instantly if the queue is full
                    webcam_ml_queue.put_nowait({"s3_path": s3_path, "data": data, "captured_at_ms": captured_at_ms})
                except asyncio.QueueFull:
                    # Log it and move on; do not freeze the websocket
                    print("Warning: Queue full, dropping webcam frame!")
                """await webcam_ml_queue.put({
                    "s3_path": s3_path,
                    "data": data,
                })"""
                # Optional ACK
                """await websocket.send_text(
                    f"queued:{s3_path}"
                )"""
                last_saved_time = current_time
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"websocket error: {e}")

#web socket for screen feed
screen_connections = {}

@app.websocket("/ws/screen")
async def websocket_sc_endpoint(
    websocket: WebSocket,
    token: str = Query(None)):
    last_saved_time1 = 0.0

    # Check token
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        USER = payload.get("username")

        if not USER:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION
            )
            return

    except Exception as e:
        print(f"Token decode error: {e}")

        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION
        )
        return

    await websocket.accept()

    # Register this user's WebSocket
    screen_connections[USER] = websocket

    print(f"Screen WebSocket connected: {USER}")

    try:
        while True:

            message = await websocket.receive_bytes()

            try:
                captured_at_ms, data = decode_timestamped_jpeg_frame(
                    message
                )

            except ValueError:
                await websocket.close(
                    code=status.WS_1003_UNSUPPORTED_DATA
                )
                return

            now = datetime.now()
            current_time = time()

            # Save/process every 10 seconds
            if current_time - last_saved_time1 >= 10:

                s3_path = (
                    f"{USER}_sc_"
                    f"{now.year}_"
                    f"{now.month:02d}_"
                    f"{now.day:02d}_"
                    f"{now.strftime('%H%M%S')}.jpg"
                )

                try:
                    sc_vlm_upload_queue.put_nowait({
                        "s3_path": s3_path,
                        "data": data,
                        "raw_bytes": data,
                        "captured_at_ms": captured_at_ms
                    })

                except asyncio.QueueFull:
                    print(
                        "Warning: Queue full, dropping screen frame!"
                    )

                try:
                    sc_queue.put_nowait({
                        "s3_path": s3_path,
                        "data": data,
                        "captured_at_ms": captured_at_ms
                    })

                except asyncio.QueueFull:
                    print(
                        "Warning: Queue full, dropping screen frame!"
                    )

                last_saved_time1 = current_time

    except WebSocketDisconnect:
        print(f"Screen WebSocket disconnected: {USER}")

    finally:
        # Remove connection when user disconnects
        if screen_connections.get(USER) is websocket:
            del screen_connections[USER]
# cheating-response listener
@app.post("/cheating-response")
async def receive_cheating_response(payload: dict):

    print("Received cheating event:")
    print(payload)

    username = payload.get("username")

    if not username:
        return {
            "status": "error",
            "message": "username is missing"
        }

    websocket = screen_connections.get(username)

    if websocket is None:
        return {
            "status": "received",
            "message": "User WebSocket is not connected"
        }

    try:
        await websocket.send_json(payload)

        print(
            f"Cheating event sent to WebSocket: {username}"
        )

        return {
            "status": "sent_to_websocket"
        }

    except Exception as e:
        print(f"Failed to send to WebSocket: {e}")

        return {
            "status": "error",
            "message": "Failed to send to WebSocket"
        }
# POST: create user
@app.post("/signup_user", response_model=schemas.userresponse)
async def create_user(user: schemas.usercreate, db: AsyncSession = Depends(get_db)):
    hashed_password = hash_password(user.password)
    db_user = models.user(
        username=user.username,
        email=user.email,
        password=hashed_password  
    )
    db.add(db_user) #MEMO: db.add() only updates Python's memory (RAM). No network call happens yet
    await db.commit()#MEMO: This triggers the actual network I/O block transaction to PostgreSQL. Must await
    await db.refresh(db_user)
    return db_user

@app.post("/login")
async def login(user_credentials: schemas.userlogin, db: AsyncSession = Depends(get_db)):
    print("Hereeee")
    # 1. Look for the user by email
    #user = await db.query(models.user).filter(models.user.email == user_credentials.email).first()
    statement=select(models.user).where(models.user.email == user_credentials.email)
    result=await db.execute(statement)
    user=result.scalars().first() 
    #If user doesn't exist, throw a 403 error
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )
    if verify_password(user_credentials.password,user.password)==False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )
    access_token = create_access_token(
        data={
            "id": str(user.id),
            "username": user.username,
            "email": user.email
        }
    )
    # 4. Return the token in the standard OAuth2 format
    return {"access_token": access_token, "token_type": "bearer"}   
    #return user

@app.get("/user/get_username", response_model=schemas.userresponse)
async def get_user_by_username(username: str = Query(..., min_length=1),db: AsyncSession = Depends(get_db)):
    statement=select(models.user).where(models.user.username==username)
    result=db.execute(statement)
    user=result.scalars().first()
    #user = await db.query(models.user).filter(models.user.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
