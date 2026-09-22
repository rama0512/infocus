import asyncio
import struct
from multiprocessing.shared_memory import SharedMemory
from ipc_config import (
    SHM_NAME, TOTAL_SHM_SIZE, RING_HEADER_SIZE, SLOT_SIZE, 
    META_HEADER_SIZE, MAX_S3_PATH_LEN, MAX_IMG_SIZE, NUM_SLOTS
)

shm = None

def init_shared_memory():
    """only to be executed when shm = None, i.e. the backend is the first process to create the shared memory segment."""
    """Initializes the shareable IPC memory namespace."""
    global shm
    try:
        # The backend (shareable host) creates the memory segment
        shm = SharedMemory(name=SHM_NAME, create=True, size=TOTAL_SHM_SIZE)
        # Set Write Index = 0, Read Index = 0
        shm.buf[0:8] = struct.pack("ii", 0, 0)
        print(f"[Backend IPC] Shared Memory Ring Buffer allocated safely: {SHM_NAME}")
    except FileExistsError:
        shm = SharedMemory(name=SHM_NAME)
        print(f"[Backend IPC] Linked to existing shared memory: {SHM_NAME}")

def write_to_ring_buffer(
    s3_path: str,
    img_bytes: bytes,
    captured_at_ms: int,
) -> bool:
    """Pushes metadata, path strings, and raw image bytes into the shared slots."""
    global shm
    
    # 1. Check current ring indices
    write_idx, read_idx = struct.unpack("ii", shm.buf[0:8])
    if (write_idx + 1) % NUM_SLOTS == read_idx:
        return False  # Buffer full!
        
    # 2. Validate payload bounds
    encoded_path = s3_path.encode('utf-8')
    if len(encoded_path) > MAX_S3_PATH_LEN:
        raise ValueError(f"S3 Path length exceeds {MAX_S3_PATH_LEN} bytes!")
    if len(img_bytes) > MAX_IMG_SIZE:
        raise ValueError(f"Image frame size exceeds {MAX_IMG_SIZE} bytes limit!")
    if captured_at_ms < 0 or captured_at_ms > (2**64 - 1):
        raise ValueError("Capture timestamp is outside the uint64 range!")

    # 3. Target memory space calculation
    slot_start = RING_HEADER_SIZE + (write_idx * SLOT_SIZE)
    
    # 4. Pack metadata header: path length, image length, capture timestamp
    meta_header = struct.pack(
        "!IIQ",
        len(encoded_path),
        len(img_bytes),
        captured_at_ms,
    )
    
    # 5. Build individual payloads with clean buffer padding
    padded_path = encoded_path.ljust(MAX_S3_PATH_LEN, b'\x00')
    padded_img = img_bytes.ljust(MAX_IMG_SIZE, b'\x00')
    
    # 6. Sequential atomic memory updates
    shm.buf[slot_start : slot_start + META_HEADER_SIZE] = meta_header
    shm.buf[slot_start + META_HEADER_SIZE : slot_start + META_HEADER_SIZE + MAX_S3_PATH_LEN] = padded_path
    shm.buf[slot_start + META_HEADER_SIZE + MAX_S3_PATH_LEN : slot_start + SLOT_SIZE] = padded_img
    
    # 7. Advance the global ring pointer safely
    next_write_idx = (write_idx + 1) % NUM_SLOTS
    shm.buf[0:4] = struct.pack("i", next_write_idx)
    return True
