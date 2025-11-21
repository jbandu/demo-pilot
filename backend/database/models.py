"""
Database models for Demo Copilot
Tracks demo sessions, interactions, and analytics
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, JSON, Float, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel

Base = declarative_base()


class DemoStatus(str, Enum):
    """Status of a demo session"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InteractionType(str, Enum):
    """Type of interaction during demo"""
    QUESTION = "question"
    NAVIGATION = "navigation"
    PAUSE = "pause"
    RESUME = "resume"
    SKIP = "skip"
    FEEDBACK = "feedback"


# SQLAlchemy Models

class DemoSession(Base):
    """Main demo session tracking"""
    __tablename__ = "demo_sessions"

    id = Column(String, primary_key=True)
    product_name = Column(String, nullable=False)  # e.g., "InSign", "Crew Intelligence"
    demo_script = Column(String, nullable=False)  # Script identifier
    status = Column(String, default=DemoStatus.PENDING)

    # Customer info
    customer_email = Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    customer_company = Column(String, nullable=True)

    # Session metadata
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Configuration
    voice_id = Column(String, default="Rachel")  # ElevenLabs voice
    speed = Column(Float, default=1.0)  # Playback speed
    config = Column(JSON, default=dict)  # Additional configuration

    # Tracking
    current_step = Column(String, nullable=True)
    steps_completed = Column(JSON, default=list)  # List of completed step IDs

    # Analytics
    questions_asked = Column(Integer, default=0)
    pauses_count = Column(Integer, default=0)
    engagement_score = Column(Float, nullable=True)  # 0-100

    # Error tracking
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interactions = relationship("DemoInteraction", back_populates="session", cascade="all, delete-orphan")
    recordings = relationship("DemoRecording", back_populates="session", cascade="all, delete-orphan")


class DemoInteraction(Base):
    """Tracks customer interactions during demo"""
    __tablename__ = "demo_interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("demo_sessions.id"), nullable=False)

    interaction_type = Column(String, nullable=False)  # InteractionType enum
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Content
    question_text = Column(Text, nullable=True)  # Customer question
    answer_text = Column(Text, nullable=True)  # Agent answer
    context = Column(JSON, nullable=True)  # Current demo context

    # Response metrics
    response_time_ms = Column(Integer, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0-1

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("DemoSession", back_populates="interactions")


class DemoRecording(Base):
    """Stores recording metadata for demo sessions"""
    __tablename__ = "demo_recordings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("demo_sessions.id"), nullable=False)

    # Recording details
    recording_url = Column(String, nullable=True)  # S3/storage URL
    duration_seconds = Column(Integer, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    format = Column(String, default="webm")  # Video format

    # Audio
    has_audio = Column(Boolean, default=True)
    audio_url = Column(String, nullable=True)  # Separate audio track

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("DemoSession", back_populates="recordings")


class DemoAnalytics(Base):
    """Aggregated analytics for demos"""
    __tablename__ = "demo_analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    product_name = Column(String, nullable=False)

    # Metrics
    total_demos = Column(Integer, default=0)
    completed_demos = Column(Integer, default=0)
    failed_demos = Column(Integer, default=0)
    avg_duration_seconds = Column(Float, nullable=True)
    avg_questions_per_demo = Column(Float, nullable=True)
    avg_engagement_score = Column(Float, nullable=True)

    # Additional metrics
    metrics = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic Schemas for API

class DemoSessionCreate(BaseModel):
    """Schema for creating a new demo session"""
    product_name: str
    demo_script: str
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    customer_company: Optional[str] = None
    voice_id: str = "Rachel"
    speed: float = 1.0
    config: Dict[str, Any] = {}


class DemoSessionResponse(BaseModel):
    """Schema for demo session response"""
    id: str
    product_name: str
    demo_script: str
    status: str
    current_step: Optional[str]
    steps_completed: list
    started_at: Optional[datetime]
    duration_seconds: Optional[int]
    questions_asked: int

    class Config:
        from_attributes = True


class DemoInteractionCreate(BaseModel):
    """Schema for creating an interaction"""
    interaction_type: str
    question_text: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class DemoInteractionResponse(BaseModel):
    """Schema for interaction response"""
    id: int
    session_id: str
    interaction_type: str
    question_text: Optional[str]
    answer_text: Optional[str]
    timestamp: datetime
    response_time_ms: Optional[int]

    class Config:
        from_attributes = True


class DemoMetrics(BaseModel):
    """Real-time demo metrics"""
    session_id: str
    current_step: str
    progress_percentage: float
    elapsed_seconds: int
    questions_asked: int
    engagement_score: Optional[float]
