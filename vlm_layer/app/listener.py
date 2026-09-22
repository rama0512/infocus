"""reads from shared memory """
import asyncio
import struct
from multiprocessing.shared_memory import SharedMemory

from app.ipc_config import (
    SHM_NAME,
    TOTAL_SHM_SIZE,
    RING_HEADER_SIZE,
    SLOT_SIZE,
    META_HEADER_SIZE,
    MAX_S3_PATH_LEN,
    MAX_IMG_SIZE,
    NUM_SLOTS,
)

from app.pipeline import process_image_pipeline


def read_indices(shm):
    """
    Read the current write and read indices
    from the ring-buffer header.
    """

    write_idx, read_idx = struct.unpack(
        "ii",
        shm.buf[0:RING_HEADER_SIZE],
    )

    return write_idx, read_idx


def read_slot(shm, slot_index):
    """
    Read one complete image slot from shared memory.

    Slot layout:

    [path_len:        4 bytes]
    [img_len:         4 bytes]
    [captured_at_ms:  8 bytes]
    [S3 path:  1024 bytes]
    [image:    MAX_IMG_SIZE bytes]
    """

    slot_start = (
        RING_HEADER_SIZE
        + (slot_index * SLOT_SIZE)
    )

    # Read metadata
    path_len, img_len, captured_at_ms = struct.unpack(
        "!IIQ",
        shm.buf[
            slot_start:
            slot_start + META_HEADER_SIZE
        ],
    )

    # Validate metadata
    if path_len < 0 or path_len > MAX_S3_PATH_LEN:
        raise ValueError(
            f"Invalid path length: {path_len}"
        )

    if img_len <= 0 or img_len > MAX_IMG_SIZE:
        raise ValueError(
            f"Invalid image size: {img_len}"
        )

    # Path starts immediately after metadata
    path_start = (
        slot_start
        + META_HEADER_SIZE
    )

    # Image starts after the fixed-size path area
    image_start = (
        path_start
        + MAX_S3_PATH_LEN
    )

    # Read path
    path_bytes = bytes(
        shm.buf[
            path_start:
            path_start + path_len
        ]
    )


    frame_name = path_bytes.decode(
        "utf-8",
        errors="replace",
    )

    # IMPORTANT:
    # Copy the bytes out of shared memory.
    image_bytes = bytes(
        shm.buf[
            image_start:
            image_start + img_len
        ]
    )

    return frame_name, image_bytes, captured_at_ms return s3_path, image_bytes, captured_at_ms


async def shared_memory_listener():
    """
    Reads images from CalmRR's shared-memory
    ring buffer and sends them to the VLM pipeline.
    """

    print(
        f"[VLM LISTENER] Connecting to shared memory: "
        f"{SHM_NAME}"
    )

    shm = None

    # Wait for the backend to create the shared memory.
    while shm is None:
        try:
            shm = SharedMemory(
                name=SHM_NAME,
                create=False,
            )

            print(
                f"[VLM LISTENER] Connected to "
                f"{SHM_NAME}"
            )

        except FileNotFoundError:
            print(
                "[VLM LISTENER] Shared memory not "
                "available yet. Retrying..."
            )

            await asyncio.sleep(0.5)

    if shm.size < TOTAL_SHM_SIZE:
        shm.close()

        raise RuntimeError(
            f"Shared memory size mismatch. "
            f"Expected {TOTAL_SHM_SIZE}, "
            f"got {shm.size}"
        )

    try:
        while True:

            write_idx, read_idx = read_indices(shm)

            # Ring buffer is empty
            if write_idx == read_idx:
                await asyncio.sleep(0.005)
                continue

            slot_index = read_idx

            try:
                frame_name, image_bytes, captured_at_ms = read_slot(
                    shm,
                    slot_index,
                )

                print(
                    f"[VLM LISTENER] New frame: "
                    f"{frame_name} "
                    f"(slot={slot_index}, "
                    f"bytes={len(image_bytes)}, "
                    f"captured_at_ms={captured_at_ms})"
                )

                # Move read index forward BEFORE inference.
                #
                # The image bytes have already been copied
                # out of shared memory, so the slot can now
                # be reused by the backend.
                next_read_idx = (
                    read_idx + 1
                ) % NUM_SLOTS

                shm.buf[
                    4:8
                ] = struct.pack(
                    "i",
                    next_read_idx,
                )

                # Run VLM inference asynchronously.
                asyncio.create_task(
                    process_image_pipeline(
                        image_bytes,
                        frame_name,
                        captured_at_ms,
                    )
                )

            except Exception as e:

                print(
                    f"[VLM LISTENER ERROR] "
                    f"slot={slot_index}: {e}"
                )

                # Do not get permanently stuck on
                # a corrupted/bad slot.
                next_read_idx = (
                    read_idx + 1
                ) % NUM_SLOTS

                shm.buf[
                    4:8
                ] = struct.pack(
                    "i",
                    next_read_idx,
                )

    finally:
        shm.close()
