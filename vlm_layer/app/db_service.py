from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vlm_result import VLMResult


async def upload_vlm_result(
    db: AsyncSession,
    payload: dict,
):
    vlm_result = VLMResult(
        username=payload.get("username"),
        frame_name=payload.get("frame_name"),
        cheating_detected=payload.get("cheating_detected"),
        violation_type=payload.get("violation_type"),
        confidence=payload.get("confidence"),
        probability=payload.get("probability"),
        reason=payload.get("reason"),
        ttft_ms=payload.get("ttft_ms"),
        total_latency_ms=payload.get("total_latency_ms"),
    )

    db.add(vlm_result)
    await db.commit()
    await db.refresh(vlm_result)

    return vlm_result