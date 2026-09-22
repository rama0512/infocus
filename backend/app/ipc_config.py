import struct
from pathlib import Path

# Shared Configuration
NUM_SLOTS = 5                  # 5-slot ring buffer
MAX_S3_PATH_LEN = 1024         # 1KB max for S3 path string
MAX_IMG_SIZE = 4 * 1024 * 1024 # 3MB max per image payload (Perfect for compressed JPEGs)

# Calculations
META_HEADER_SIZE = 16          # 4 bytes path_len, 4 bytes img_len, 8 bytes captured_at_ms
SLOT_SIZE = META_HEADER_SIZE + MAX_S3_PATH_LEN + MAX_IMG_SIZE

RING_HEADER_SIZE = 8           # 4 bytes write_idx, 4 bytes read_idx
TOTAL_SHM_SIZE = RING_HEADER_SIZE + (NUM_SLOTS * SLOT_SIZE)

SHM_NAME = "vlm_image_ring_buffer"
