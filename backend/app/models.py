from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, BigInteger, JSON, Boolean, Float
from datetime import datetime
from app.database import Base
class user(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String(250), nullable=False)
class webcam_result(Base):
    __tablename__ = "webcam_result"
    id = Column(Integer, primary_key=True)
    s3_path = Column(String, nullable=False)
    captured_at_ms = Column(BigInteger, nullable=False) 
    coordinates = Column(JSON, nullable=False) 
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