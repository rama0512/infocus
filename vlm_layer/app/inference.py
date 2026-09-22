import asyncio
import time
import traceback

from PIL import Image

from app.engine import vllm_engine
from app.prompt import (
    PROCTOR_PROMPT,
    SAMPLING_PARAMS,
)


async def analyze_with_qwen(
    img_object: Image.Image,
    frame_name: str = "uploaded_image"
):
    """
    Runs Qwen-VL inference and returns
    prediction + TTFT + total latency.
    """

    try:
        request_id = (
            f"req_{frame_name.split('.')[0]}_"
            f"{asyncio.get_running_loop().time()}"
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": img_object
                        #"max_pixels": 768 * 768,
                    },
                    {
                        "type": "text",
                        "text": PROCTOR_PROMPT,
                    },
                ],
            }
        ]

        tokenizer = vllm_engine.get_tokenizer()

        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,#True,
            add_generation_prompt=True,
        )

        inputs = {
            "prompt": prompt,
            "multi_modal_data": {
                "image": img_object
            }
        }

        print(f"[vLLM] Running inference: {request_id}")

        start_time = time.perf_counter()

        results_generator = vllm_engine.generate(
            inputs,
            SAMPLING_PARAMS,
            request_id,
        )

        first_token_time = None
        final_output = None

        async for request_output in results_generator:

            if first_token_time is None:
                first_token_time = time.perf_counter()

            final_output = request_output

        end_time = time.perf_counter()

        ttft_ms = (
            (first_token_time - start_time) * 1000
            if first_token_time
            else None
        )

        total_latency_ms = (
            (end_time - start_time) * 1000
        )

        if final_output:

            prediction = final_output.outputs[0].text.strip()

            return {
                "prediction": prediction,
                "ttft_ms": round(ttft_ms, 2),
                "total_latency_ms": round(total_latency_ms, 2),
            }

        return {
            "prediction": None,
            "ttft_ms": round(ttft_ms, 2) if ttft_ms else None,
            "total_latency_ms": round(total_latency_ms, 2),
        }

    except Exception as e:

        print(f"vLLM Inference Failure on {frame_name}: {e}")
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception repr: {repr(e)}")
        traceback.print_exc()

        return {
            "prediction": None,
            "ttft_ms": None,
            "total_latency_ms": None,
            "error": str(e),
        }