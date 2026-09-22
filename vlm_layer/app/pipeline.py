import io

from PIL import Image, UnidentifiedImageError
import base64
from app.database import SessionLocal
from app.db_service import upload_vlm_result
from app.parser import parse_prediction
from app.inference import analyze_with_qwen
from app.service_client import send_cheating_event

def image_to_base64(image):
    buffer = io.BytesIO()

    image.save(buffer, format="JPEG", quality=85)

    image_bytes = buffer.getvalue()

    return base64.b64encode(image_bytes).decode("utf-8")

def extract_username(frame_name: str) -> str | None:
    """
    Recover the username from a screen frame name.

    The backend builds the frame name as
    ``{username}_sc_{YYYY}_{MM}_{DD}_{HHMMSS}.jpg``, so the
    username is everything before the first ``_sc_`` marker.
    """

    if not frame_name:
        return None

    marker = "_sc_"
    index = frame_name.find(marker)

    if index <= 0:
        return None

    return frame_name[:index]


async def process_image_pipeline(
    image_bytes: bytes,
    frame_name: str,
    captured_at_ms: int,
):
    """
    Converts shared-memory image bytes into a PIL image
    and runs VLM inference.
    """

    try:
        with io.BytesIO(image_bytes) as buffer:
            image = Image.open(buffer)
            image.load()
            image = image.copy()
        
        #get the base64 representation of the image for sending to the service
        image_base64 = image_to_base64(image)

        # The buffer is now explicitly closed.
        prediction = await analyze_with_qwen(
            image,
            frame_name,
        )
        
        parsed_prediction = parse_prediction(
            prediction.get("prediction")
        )

        if (parsed_prediction and parsed_prediction.get("CHEATING_DETECTED") == "YES"):
            print(f"[PIPELINE] CHEATING DETECTED: "
                f"{frame_name}")

            payload = {
                "username": extract_username(frame_name),
                "frame_name": frame_name,
                "cheating_detected": True,
                "image_base64": image_base64,
                "violation_type": parsed_prediction.get(
                    "VIOLATION"
                ),
                "confidence": parsed_prediction.get(
                    "CONFIDENCE"
                ),
                "probability": parsed_prediction.get(
                    "PROBABILITY"
                ),
                "reason": parsed_prediction.get(
                    "REASON"
                ),
                "ttft_ms": prediction.get(
                    "ttft_ms"
                ),
                "total_latency_ms": prediction.get(
                    "total_latency_ms"
                ),
            }

            async with SessionLocal() as db:
                await upload_vlm_result(db, payload)

            await send_cheating_event(payload)

            print(
                f"[PIPELINE] CHEATING EVENT SENT: "
                f"{frame_name}"
            )

        if (parsed_prediction and parsed_prediction.get("CHEATING_DETECTED") == "NO"):
            payload = {
                "username": extract_username(frame_name),
                "frame_name": frame_name,
                "cheating_detected": False,
                "violation_type": parsed_prediction.get("VIOLATION"),
                "confidence": parsed_prediction.get("CONFIDENCE"),
                "probability": parsed_prediction.get("PROBABILITY"),
                "reason": parsed_prediction.get("REASON"),
                "ttft_ms": prediction.get("ttft_ms"),
                "total_latency_ms": prediction.get("total_latency_ms"),
            }
            #print(payload)
            #await db_upload_event(payload)
            async with SessionLocal() as db:
                await upload_vlm_result(db, payload)
        print(
            f"[PIPELINE] Completed: {frame_name}, "
            f"captured_at_ms={captured_at_ms}"
        )

        return prediction

    except UnidentifiedImageError:
        print(
            f"[PIPELINE ERROR] Invalid image: "
            f"{frame_name}"
        )
        return None

    except Exception as e:
        print(
            f"[PIPELINE ERROR] "
            f"{frame_name}: {e}"
        )
        return None
