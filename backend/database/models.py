"""
Database models for Demo Copilot
Tracks demo sessions, interactions, actions, and analytics
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    JSON,
    Float,
    ForeignKey,
    Text,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel

Base = declarative_base()


class DemoStatus(str, Enum):
    """Status of a demo session"""

    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    FAILED = "failed"


class ActionType(str, Enum):
    """Type of action during demo"""

    CLICK = "click"
    TYPE = "type"
    UPLOAD = "upload"
    NAVIGATE = "navigate"
    NARRATE = "narrate"
    SCROLL = "scroll"
    HOVER = "hover"
    WAIT = "wait"


class QuestionIntent(str, Enum):
    """Intent classification for customer questions"""

    CLARIFICATION = "clarification"
    FEATURE_REQUEST = "feature_request"
    PRICING = "pricing"
    COMPARISON = "comparison"
    TECHNICAL = "technical"
    INTEGRATION = "integration"
    GENERAL = "general"


class Sentiment(str, Enum):
    """Sentiment classification"""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    CONFUSED = "confused"


# SQLAlchemy Models


class DemoSession(Base):
    """Tracks individual demo sessions"""

    __tablename__ = "demo_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Customer info
    customer_email = Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    customer_company = Column(String, nullable=True)
    customer_industry = Column(String, nullable=True)

    # Demo config
    demo_type = Column(String, nullable=False)  # 'insign', 'crew_intelligence', etc.
    demo_duration_preference = Column(
        String, default="standard"
    )  # 'quick', 'standard', 'deep_dive'
    demo_customization = Column(JSON, nullable=True)  # Custom preferences

    # Voice settings
    voice_id = Column(String, default="Rachel")
    voice_speed = Column(Float, default=1.0)

    # Session state
    status = Column(String, default=DemoStatus.INITIALIZED)
    current_step = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Technical
    browser_session_id = Column(String, nullable=True)
    recording_url = Column(String, nullable=True)

    # Analytics
    engagement_score = Column(Float, nullable=True)  # 0-100
    questions_asked = Column(Integer, default=0)
    pauses_count = Column(Integer, default=0)
    features_shown = Column(JSON, default=list)
    customer_interests = Column(JSON, default=list)

    # Error tracking
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    actions = relationship(
        "DemoAction", back_populates="session", cascade="all, delete-orphan"
    )
    questions = relationship(
        "CustomerQuestion", back_populates="session", cascade="all, delete-orphan"
    )


class DemoAction(Base):
    """Tracks every action taken during demo"""

    __tablename__ = "demo_actions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(
        String, ForeignKey("demo_sessions.id", ondelete="CASCADE"), nullable=False
    )

    # Action details
    step_number = Column(Integer, nullable=False)
    action_type = Column(String, nullable=False)  # ActionType enum
    action_description = Column(Text, nullable=False)

    # Technical details
    selector = Column(String, nullable=True)  # CSS selector for browser actions
    value = Column(Text, nullable=True)  # Value typed, file uploaded, etc.

    # Voice
    narration_text = Column(Text, nullable=True)
    narration_audio_url = Column(String, nullable=True)
    narration_duration_ms = Column(Integer, nullable=True)

    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    # Status
    status = Column(
        String, default="pending"
    )  # 'pending', 'running', 'completed', 'failed'
    error_message = Column(Text, nullable=True)

    # Relationships
    session = relationship("DemoSession", back_populates="actions")


class CustomerQuestion(Base):
    """Tracks customer questions during demo"""

    __tablename__ = "customer_questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(
        String, ForeignKey("demo_sessions.id", ondelete="CASCADE"), nullable=False
    )

    # Question
    question_text = Column(Text, nullable=False)
    question_audio_url = Column(String, nullable=True)  # If spoken
    asked_at_step = Column(Integer, nullable=False)

    # Agent response
    response_text = Column(Text, nullable=True)
    response_audio_url = Column(String, nullable=True)
    response_action = Column(
        String, nullable=True
    )  # 'continue', 'jump_to_feature', 'deep_dive'

    # Classification
    intent = Column(String, nullable=True)  # QuestionIntent enum
    sentiment = Column(String, nullable=True)  # Sentiment enum
    priority = Column(String, default="normal")  # 'low', 'normal', 'high', 'critical'

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    response_time_ms = Column(Integer, nullable=True)

    # Relationships
    session = relationship("DemoSession", back_populates="questions")


class DemoScript(Base):
    """Stores demo scripts for different products"""

    __tablename__ = "demo_scripts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Script identity
    product_name = Column(String, nullable=False)  # 'insign', 'crew_intelligence'
    script_version = Column(String, default="1.0")
    script_type = Column(String, default="standard")  # 'quick', 'standard', 'deep_dive'

    # Script content
    steps = Column(JSON, nullable=False)  # List of demo steps
    total_duration_estimate_minutes = Column(Integer, nullable=False)

    # Product context for Q&A
    product_description = Column(Text, nullable=True)
    key_features = Column(JSON, default=list)
    pricing_info = Column(Text, nullable=True)
    target_customers = Column(JSON, default=list)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DemoAnalytics(Base):
    """Aggregate analytics for demo performance"""

    __tablename__ = "demo_analytics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, nullable=False)
    product_name = Column(String, nullable=True)

    # Volume metrics
    total_demos_started = Column(Integer, default=0)
    total_demos_completed = Column(Integer, default=0)
    total_demos_abandoned = Column(Integer, default=0)

    # Engagement metrics
    avg_duration_seconds = Column(Float, nullable=True)
    avg_completion_rate = Column(Float, nullable=True)
    avg_questions_per_demo = Column(Float, nullable=True)
    avg_engagement_score = Column(Float, nullable=True)

    # Feature interest (most requested features)
    top_features_requested = Column(JSON, default=list)
    top_customer_concerns = Column(JSON, default=list)

    # Outcomes
    demos_leading_to_signup = Column(Integer, default=0)
    conversion_rate = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic Schemas for API


class DemoSessionCreate(BaseModel):
    """Schema for creating a new demo session"""

    demo_type: str
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    customer_company: Optional[str] = None
    customer_industry: Optional[str] = None
    demo_duration_preference: str = "standard"
    demo_customization: Optional[Dict[str, Any]] = None
    voice_id: str = "Rachel"
    voice_speed: float = 1.0


class DemoSessionResponse(BaseModel):
    """Schema for demo session response"""

    id: str
    demo_type: str
    status: str
    customer_name: Optional[str]
    current_step: int
    started_at: Optional[datetime]
    duration_seconds: Optional[int]
    questions_asked: int
    engagement_score: Optional[float]

    class Config:
        from_attributes = True


class DemoActionCreate(BaseModel):
    """Schema for creating a demo action"""

    step_number: int
    action_type: str
    action_description: str
    selector: Optional[str] = None
    value: Optional[str] = None
    narration_text: Optional[str] = None


class DemoActionResponse(BaseModel):
    """Schema for demo action response"""

    id: str
    session_id: str
    step_number: int
    action_type: str
    action_description: str
    status: str
    duration_ms: Optional[int]

    class Config:
        from_attributes = True


class CustomerQuestionCreate(BaseModel):
    """Schema for creating a customer question"""

    question_text: str
    asked_at_step: int


class CustomerQuestionResponse(BaseModel):
    """Schema for customer question response"""

    id: str
    session_id: str
    question_text: str
    response_text: Optional[str]
    intent: Optional[str]
    sentiment: Optional[str]
    response_time_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class DemoScriptCreate(BaseModel):
    """Schema for creating a demo script"""

    product_name: str
    script_version: str = "1.0"
    script_type: str = "standard"
    steps: list
    total_duration_estimate_minutes: int
    product_description: Optional[str] = None
    key_features: Optional[list] = None
    pricing_info: Optional[str] = None


class DemoScriptResponse(BaseModel):
    """Schema for demo script response"""

    id: str
    product_name: str
    script_version: str
    script_type: str
    total_duration_estimate_minutes: int
    is_active: bool

    class Config:
        from_attributes = True


class DemoAnalyticsResponse(BaseModel):
    """Schema for analytics response"""

    date: datetime
    product_name: Optional[str]
    total_demos_started: int
    total_demos_completed: int
    avg_completion_rate: Optional[float]
    avg_questions_per_demo: Optional[float]
    avg_engagement_score: Optional[float]
    conversion_rate: Optional[float]

    class Config:
        from_attributes = True


class DemoMetrics(BaseModel):
    """Real-time demo metrics"""

    session_id: str
    current_step: int
    progress_percentage: float
    elapsed_seconds: int
    questions_asked: int
    engagement_score: Optional[float]
