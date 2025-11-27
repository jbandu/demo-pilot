"""
CRUD operations for Demo Copilot database
Database access layer with common operations
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import uuid

from .models import (
    DemoSession,
    DemoAction,
    CustomerQuestion,
    DemoScript,
    DemoAnalytics,
    DemoSessionCreate,
    DemoActionCreate,
    CustomerQuestionCreate,
)


# Demo Session CRUD


def create_demo_session(db: Session, session_data: DemoSessionCreate) -> DemoSession:
    """Create a new demo session"""
    session = DemoSession(
        id=str(uuid.uuid4()),
        demo_type=session_data.demo_type,
        customer_email=session_data.customer_email,
        customer_name=session_data.customer_name,
        customer_company=session_data.customer_company,
        customer_industry=session_data.customer_industry,
        demo_duration_preference=session_data.demo_duration_preference,
        demo_customization=session_data.demo_customization,
        voice_id=session_data.voice_id,
        voice_speed=session_data.voice_speed,
        status="initialized",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_demo_session(db: Session, session_id: str) -> Optional[DemoSession]:
    """Get demo session by ID"""
    return db.query(DemoSession).filter(DemoSession.id == session_id).first()


def update_demo_session(
    db: Session, session_id: str, **kwargs
) -> Optional[DemoSession]:
    """Update demo session fields"""
    session = get_demo_session(db, session_id)
    if session:
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        db.commit()
        db.refresh(session)
    return session


def start_demo_session(db: Session, session_id: str) -> Optional[DemoSession]:
    """Mark demo session as started"""
    return update_demo_session(
        db, session_id, status="running", started_at=datetime.utcnow()
    )


def complete_demo_session(
    db: Session, session_id: str, duration_seconds: int
) -> Optional[DemoSession]:
    """Mark demo session as completed"""
    return update_demo_session(
        db,
        session_id,
        status="completed",
        completed_at=datetime.utcnow(),
        duration_seconds=duration_seconds,
    )


def abandon_demo_session(db: Session, session_id: str) -> Optional[DemoSession]:
    """Mark demo session as abandoned"""
    return update_demo_session(
        db, session_id, status="abandoned", completed_at=datetime.utcnow()
    )


def get_active_sessions(db: Session, limit: int = 100) -> List[DemoSession]:
    """Get all active (non-completed) sessions"""
    return (
        db.query(DemoSession)
        .filter(DemoSession.status.in_(["initialized", "running", "paused"]))
        .order_by(desc(DemoSession.created_at))
        .limit(limit)
        .all()
    )


def get_sessions_by_customer(db: Session, customer_email: str) -> List[DemoSession]:
    """Get all sessions for a customer"""
    return (
        db.query(DemoSession)
        .filter(DemoSession.customer_email == customer_email)
        .order_by(desc(DemoSession.created_at))
        .all()
    )


# Demo Action CRUD


def create_demo_action(
    db: Session, session_id: str, action_data: DemoActionCreate
) -> DemoAction:
    """Create a new demo action"""
    action = DemoAction(
        id=str(uuid.uuid4()),
        session_id=session_id,
        step_number=action_data.step_number,
        action_type=action_data.action_type,
        action_description=action_data.action_description,
        selector=action_data.selector,
        value=action_data.value,
        narration_text=action_data.narration_text,
        status="pending",
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def start_demo_action(db: Session, action_id: str) -> Optional[DemoAction]:
    """Mark action as started"""
    action = db.query(DemoAction).filter(DemoAction.id == action_id).first()
    if action:
        action.status = "running"
        action.started_at = datetime.utcnow()
        db.commit()
        db.refresh(action)
    return action


def complete_demo_action(
    db: Session,
    action_id: str,
    duration_ms: int,
    narration_audio_url: Optional[str] = None,
) -> Optional[DemoAction]:
    """Mark action as completed"""
    action = db.query(DemoAction).filter(DemoAction.id == action_id).first()
    if action:
        action.status = "completed"
        action.completed_at = datetime.utcnow()
        action.duration_ms = duration_ms
        if narration_audio_url:
            action.narration_audio_url = narration_audio_url
        db.commit()
        db.refresh(action)
    return action


def get_session_actions(db: Session, session_id: str) -> List[DemoAction]:
    """Get all actions for a session"""
    return (
        db.query(DemoAction)
        .filter(DemoAction.session_id == session_id)
        .order_by(DemoAction.step_number)
        .all()
    )


# Customer Question CRUD


def create_customer_question(
    db: Session, session_id: str, question_data: CustomerQuestionCreate
) -> CustomerQuestion:
    """Create a new customer question"""
    question = CustomerQuestion(
        id=str(uuid.uuid4()),
        session_id=session_id,
        question_text=question_data.question_text,
        asked_at_step=question_data.asked_at_step,
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    # Increment questions_asked counter
    session = get_demo_session(db, session_id)
    if session:
        session.questions_asked += 1
        db.commit()

    return question


def answer_customer_question(
    db: Session,
    question_id: str,
    response_text: str,
    response_time_ms: int,
    intent: Optional[str] = None,
    sentiment: Optional[str] = None,
) -> Optional[CustomerQuestion]:
    """Add answer to customer question"""
    question = (
        db.query(CustomerQuestion).filter(CustomerQuestion.id == question_id).first()
    )
    if question:
        question.response_text = response_text
        question.response_time_ms = response_time_ms
        question.intent = intent
        question.sentiment = sentiment
        db.commit()
        db.refresh(question)
    return question


def get_session_questions(db: Session, session_id: str) -> List[CustomerQuestion]:
    """Get all questions for a session"""
    return (
        db.query(CustomerQuestion)
        .filter(CustomerQuestion.session_id == session_id)
        .order_by(CustomerQuestion.created_at)
        .all()
    )


# Demo Script CRUD


def get_demo_script(
    db: Session, product_name: str, script_type: str = "standard"
) -> Optional[DemoScript]:
    """Get active demo script for a product"""
    return (
        db.query(DemoScript)
        .filter(
            DemoScript.product_name == product_name,
            DemoScript.script_type == script_type,
            DemoScript.is_active == True,
        )
        .first()
    )


def get_all_demo_scripts(db: Session, active_only: bool = True) -> List[DemoScript]:
    """Get all demo scripts"""
    query = db.query(DemoScript)
    if active_only:
        query = query.filter(DemoScript.is_active == True)
    return query.all()


# Analytics CRUD


def create_daily_analytics(
    db: Session, date: datetime, product_name: Optional[str] = None
) -> DemoAnalytics:
    """Create or get daily analytics record"""
    # Try to get existing record
    analytics = (
        db.query(DemoAnalytics)
        .filter(
            DemoAnalytics.date == date.date(),
            DemoAnalytics.product_name == product_name,
        )
        .first()
    )

    if not analytics:
        analytics = DemoAnalytics(
            id=str(uuid.uuid4()), date=date.date(), product_name=product_name
        )
        db.add(analytics)
        db.commit()
        db.refresh(analytics)

    return analytics


def update_daily_analytics(
    db: Session, date: datetime, product_name: Optional[str] = None
):
    """
    Recalculate analytics for a specific date
    Aggregates data from demo sessions
    """
    # Get or create analytics record
    analytics = create_daily_analytics(db, date, product_name)

    # Query sessions for this date
    start_date = datetime.combine(date.date(), datetime.min.time())
    end_date = start_date + timedelta(days=1)

    query = db.query(DemoSession).filter(
        DemoSession.created_at >= start_date, DemoSession.created_at < end_date
    )

    if product_name:
        query = query.filter(DemoSession.demo_type == product_name)

    sessions = query.all()

    # Calculate metrics
    total_started = len(sessions)
    completed = [s for s in sessions if s.status == "completed"]
    abandoned = [s for s in sessions if s.status == "abandoned"]

    analytics.total_demos_started = total_started
    analytics.total_demos_completed = len(completed)
    analytics.total_demos_abandoned = len(abandoned)

    if completed:
        analytics.avg_duration_seconds = sum(
            s.duration_seconds or 0 for s in completed
        ) / len(completed)
        analytics.avg_questions_per_demo = sum(
            s.questions_asked for s in completed
        ) / len(completed)
        analytics.avg_engagement_score = sum(
            s.engagement_score or 0 for s in completed if s.engagement_score
        ) / len(completed)

    if total_started > 0:
        analytics.avg_completion_rate = len(completed) / total_started

    # Get top features requested (from questions)
    questions = []
    for session in sessions:
        questions.extend(get_session_questions(db, session.id))

    feature_counts: Dict[str, int] = {}
    for q in questions:
        if q.intent:
            feature_counts[q.intent] = feature_counts.get(q.intent, 0) + 1

    top_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    analytics.top_features_requested = [
        {"feature": f, "count": c} for f, c in top_features
    ]

    db.commit()
    db.refresh(analytics)
    return analytics


def get_analytics_range(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    product_name: Optional[str] = None,
) -> List[DemoAnalytics]:
    """Get analytics for a date range"""
    query = db.query(DemoAnalytics).filter(
        DemoAnalytics.date >= start_date.date(), DemoAnalytics.date <= end_date.date()
    )

    if product_name:
        query = query.filter(DemoAnalytics.product_name == product_name)

    return query.order_by(DemoAnalytics.date).all()


# Dashboard/Reports


def get_dashboard_stats(db: Session, days: int = 7) -> Dict[str, Any]:
    """
    Get dashboard statistics for the last N days

    Returns overview metrics for monitoring
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Total sessions
    total_sessions = (
        db.query(func.count(DemoSession.id))
        .filter(DemoSession.created_at >= cutoff_date)
        .scalar()
    )

    # Completed sessions
    completed_sessions = (
        db.query(func.count(DemoSession.id))
        .filter(
            DemoSession.created_at >= cutoff_date, DemoSession.status == "completed"
        )
        .scalar()
    )

    # Average duration
    avg_duration = (
        db.query(func.avg(DemoSession.duration_seconds))
        .filter(
            DemoSession.created_at >= cutoff_date, DemoSession.status == "completed"
        )
        .scalar()
    )

    # Total questions
    total_questions = (
        db.query(func.count(CustomerQuestion.id))
        .join(DemoSession)
        .filter(DemoSession.created_at >= cutoff_date)
        .scalar()
    )

    # Questions by intent
    questions_by_intent = (
        db.query(CustomerQuestion.intent, func.count(CustomerQuestion.id))
        .join(DemoSession)
        .filter(
            DemoSession.created_at >= cutoff_date, CustomerQuestion.intent.isnot(None)
        )
        .group_by(CustomerQuestion.intent)
        .all()
    )

    return {
        "total_sessions": total_sessions or 0,
        "completed_sessions": completed_sessions or 0,
        "completion_rate": (
            (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        ),
        "avg_duration_seconds": int(avg_duration) if avg_duration else 0,
        "total_questions": total_questions or 0,
        "avg_questions_per_session": (
            (total_questions / total_sessions) if total_sessions > 0 else 0
        ),
        "questions_by_intent": (
            {intent: count for intent, count in questions_by_intent}
            if questions_by_intent
            else {}
        ),
    }


# Cleanup utilities


def delete_old_sessions(db: Session, days: int = 90) -> int:
    """Delete demo sessions older than N days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    count = db.query(DemoSession).filter(DemoSession.created_at < cutoff_date).delete()

    db.commit()
    return count
