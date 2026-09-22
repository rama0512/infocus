from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime
from datetime import datetime

from app.database import Base


class VLMResult(Base):
    __tablename__ = "vlm_results"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    frame_name = Column(String, nullable=False)
    cheating_detected = Column(Boolean, nullable=False)
    violation_type = Column(String, nullable=True)
    confidence = Column(String, nullable=True)
    probability = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    ttft_ms = Column(Float, nullable=True)
    total_latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
