"""vllm engine configuration"""
from vllm import AsyncLLMEngine, AsyncEngineArgs
from app.config import (
    MODEL_NAME,
    GPU_MEMORY_UTILIZATION,
    MAX_MODEL_LEN,
    MAX_IMAGES_PER_PROMPT,
)
ENGINE_ARGS = AsyncEngineArgs(
    model=MODEL_NAME,
    gpu_memory_utilization=GPU_MEMORY_UTILIZATION,
    max_model_len=MAX_MODEL_LEN,
    limit_mm_per_prompt={"image": MAX_IMAGES_PER_PROMPT},
    trust_remote_code=True,
    enforce_eager=True
)

vllm_engine = AsyncLLMEngine.from_engine_args(ENGINE_ARGS)