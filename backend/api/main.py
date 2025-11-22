from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import asyncio
import logging
import os
from datetime import datetime
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Get the backend directory path and load .env from there
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
    logger_temp = logging.getLogger(__name__)
    logger_temp.info(f"Loaded environment variables from {env_path}")
else:
    # Try to load from current directory as fallback
    load_dotenv()

# Try both import styles to work from any directory
try:
    from backend.agents.demo_copilot import DemoCopilot
    from backend.database.models import Base
except ImportError:
    import sys
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from backend.agents.demo_copilot import DemoCopilot
    from backend.database.models import Base

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Demo Copilot API",
    description="Autonomous product demo agent system",
    version="1.0.0"
)

# CORS - Allow frontend to connect
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",  # Next.js dev server
    frontend_url,  # Production frontend from env
]
# Add Railway frontend if available
if os.getenv("RAILWAY_ENVIRONMENT"):
    railway_frontend = os.getenv("RAILWAY_STATIC_URL", "")
    if railway_frontend:
        allowed_origins.append(railway_frontend)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
def fix_database_url(url: str) -> str:
    """
    Convert Railway/standard postgres:// URL to asyncpg format.
    Railway provides postgresql:// but we need postgresql+asyncpg:// for async support.
    """
    if url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url

raw_database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/demo_copilot")
DATABASE_URL = fix_database_url(raw_database_url)
SKIP_DATABASE = os.getenv("SKIP_DATABASE", "false").lower() in ("true", "1", "yes")

logger.info(f"Database URL protocol: {DATABASE_URL.split('://')[0] if '://' in DATABASE_URL else 'unknown'}")

# Only create engine if not skipping database
engine = None
AsyncSessionLocal = None

if not SKIP_DATABASE:
    try:
        engine = create_async_engine(DATABASE_URL, echo=True)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    except Exception as e:
        logger.warning(f"Could not create database engine: {e}")
        logger.warning("Database will be disabled. Set SKIP_DATABASE=true to suppress this warning.")

# Global state
active_demos: Dict[str, DemoCopilot] = {}
websocket_connections: Dict[str, WebSocket] = {}


# Pydantic models
class StartDemoRequest(BaseModel):
    demo_type: str = Field(..., description="Type of demo: 'insign', 'crew_intelligence'")
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_company: Optional[str] = None
    customer_industry: Optional[str] = None
    demo_duration: str = Field(default='standard', description="'quick', 'standard', or 'deep_dive'")
    custom_features: Optional[List[str]] = Field(default=None, description="Custom features to focus on")


class StartDemoResponse(BaseModel):
    session_id: str
    status: str
    demo_type: str
    websocket_url: str
    estimated_duration_minutes: int


class AskQuestionRequest(BaseModel):
    session_id: str
    question: str


class DemoControlRequest(BaseModel):
    session_id: str
    action: str  # 'pause', 'resume', 'stop'


class DemoStatusResponse(BaseModel):
    session_id: str
    status: str
    current_step: int
    total_steps: int
    progress_percentage: float
    messages: List[Dict[str, Any]]


# Database dependency
async def get_db():
    """Get database session (returns None if database unavailable)"""
    if AsyncSessionLocal is None:
        yield None
        return

    session = None
    try:
        session = AsyncSessionLocal()
        yield session
    except Exception as e:
        logger.warning(f"Database error: {e}")
        if session:
            await session.rollback()
    finally:
        if session:
            await session.close()


# Routes
@app.get("/")
async def root():
    return {
        "service": "Demo Copilot",
        "version": "1.0.0",
        "status": "operational",
        "active_demos": len(active_demos)
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_demos": len(active_demos),
        "websocket_connections": len(websocket_connections)
    }


@app.post("/api/demo/start", response_model=StartDemoResponse)
async def start_demo(request: StartDemoRequest, db: Optional[AsyncSession] = Depends(get_db)):
    """Start a new demo session"""
    try:
        logger.info(f"Starting {request.demo_type} demo for {request.customer_email}")

        # Create demo copilot instance (db may be None if database unavailable)
        copilot = DemoCopilot(database_session=db)

        # Build customer context
        customer_context = {
            'name': request.customer_name,
            'email': request.customer_email,
            'company': request.customer_company,
            'industry': request.customer_industry
        }

        # Get custom script if requested
        custom_script = None
        if request.custom_features:
            # Build custom script focusing on requested features
            script_builder = copilot.scripts[request.demo_type]
            custom_script = script_builder.get_custom_demo(request.custom_features)

        # Start demo
        session_id = await copilot.start_demo(
            demo_type=request.demo_type,
            customer_context=customer_context,
            custom_script=custom_script
        )

        # Store in active demos
        active_demos[session_id] = copilot

        # Estimate duration
        duration_map = {
            'quick': 5,
            'standard': 10,
            'deep_dive': 20
        }
        estimated_duration = duration_map.get(request.demo_duration, 10)

        return StartDemoResponse(
            session_id=session_id,
            status='started',
            demo_type=request.demo_type,
            websocket_url=f"ws://localhost:8000/ws/demo/{session_id}",
            estimated_duration_minutes=estimated_duration
        )

    except Exception as e:
        logger.error(f"Error starting demo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/demo/{session_id}/status", response_model=DemoStatusResponse)
async def get_demo_status(session_id: str):
    """Get current status of a demo"""
    copilot = active_demos.get(session_id)

    if not copilot:
        raise HTTPException(status_code=404, detail="Demo session not found")

    state = copilot.state
    if not state:
        raise HTTPException(status_code=500, detail="Demo state not initialized")

    total_steps = len(state['demo_script'])
    current_step = state['current_step']
    progress = (current_step / total_steps * 100) if total_steps > 0 else 0

    return DemoStatusResponse(
        session_id=session_id,
        status=state['status'],
        current_step=current_step,
        total_steps=total_steps,
        progress_percentage=round(progress, 2),
        messages=state.get('messages', [])
    )


@app.post("/api/demo/{session_id}/question")
async def ask_question(session_id: str, request: AskQuestionRequest):
    """Ask a question during the demo"""
    copilot = active_demos.get(session_id)

    if not copilot:
        raise HTTPException(status_code=404, detail="Demo session not found")

    try:
        await copilot.ask_question(request.question)
        return {
            "status": "question_received",
            "session_id": session_id,
            "question": request.question
        }
    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/demo/{session_id}/control")
async def control_demo(session_id: str, request: DemoControlRequest):
    """Control demo playback (pause, resume, stop)"""
    copilot = active_demos.get(session_id)

    if not copilot:
        raise HTTPException(status_code=404, detail="Demo session not found")

    try:
        if request.action == 'pause':
            await copilot.pause_demo()
        elif request.action == 'resume':
            await copilot.resume_demo()
        elif request.action == 'stop':
            await copilot.cleanup()
            active_demos.pop(session_id, None)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")

        return {
            "status": "success",
            "action": request.action,
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error controlling demo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/demo/{session_id}")
async def websocket_demo_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time demo streaming.
    Streams:
    - Video frames (browser screenshots)
    - Audio chunks (voice narration)
    - Status updates
    - Step changes
    """
    await websocket.accept()
    websocket_connections[session_id] = websocket

    logger.info(f"WebSocket connected for session: {session_id}")

    try:
        copilot = active_demos.get(session_id)
        if not copilot:
            await websocket.send_json({
                "type": "error",
                "message": "Demo session not found"
            })
            await websocket.close()
            return

        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Stream demo updates
        while True:
            # Check if demo is still active
            if session_id not in active_demos:
                break

            state = copilot.state
            if not state:
                break

            # Get current video frame
            video_frame = await copilot.browser.get_video_frame()
            if video_frame:
                await websocket.send_json({
                    "type": "video_frame",
                    "data": video_frame,
                    "timestamp": datetime.utcnow().isoformat()
                })

            # Send status update
            await websocket.send_json({
                "type": "status_update",
                "current_step": state['current_step'],
                "total_steps": len(state['demo_script']),
                "status": state['status'],
                "timestamp": datetime.utcnow().isoformat()
            })

            # Check for new messages
            if state.get('messages'):
                last_message = state['messages'][-1]
                await websocket.send_json({
                    "type": "message",
                    "message": last_message,
                    "timestamp": datetime.utcnow().isoformat()
                })

            # Wait before next update (30 FPS = ~33ms)
            await asyncio.sleep(0.033)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        websocket_connections.pop(session_id, None)


@app.get("/api/demos")
async def list_demos(db: Optional[AsyncSession] = Depends(get_db)):
    """List all demo sessions (for analytics)"""
    # Query database for demo sessions
    # This is a placeholder - implement based on your database layer
    return {
        "active_demos": len(active_demos),
        "database_available": db is not None,
        "sessions": [
            {
                "session_id": sid,
                "status": copilot.state.get('status') if copilot.state else 'unknown',
                "demo_type": copilot.state.get('demo_type') if copilot.state else 'unknown'
            }
            for sid, copilot in active_demos.items()
        ]
    }


@app.get("/api/analytics/summary")
async def analytics_summary(db: Optional[AsyncSession] = Depends(get_db)):
    """Get analytics summary"""
    # Implement analytics queries
    return {
        "database_available": db is not None,
        "total_demos_today": 0,  # Query from DB
        "completion_rate": 0.0,
        "avg_duration_minutes": 0.0,
        "most_asked_questions": [],
        "top_features_requested": []
    }


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Demo Copilot API starting up...")

    # Skip database initialization if SKIP_DATABASE is set or engine is None
    if SKIP_DATABASE or engine is None:
        logger.info("Database disabled (SKIP_DATABASE=true or no valid DATABASE_URL)")
        logger.info("Backend running in development mode without database")
        return

    # Try to create database tables (gracefully handle if DB not available)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Could not connect to database: {e}")
        logger.warning("Backend will run without database. Some features may not work.")
        logger.warning("To fix: Set DATABASE_URL in .env or set SKIP_DATABASE=true")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Demo Copilot API shutting down...")

    # Close all active demos
    for session_id, copilot in list(active_demos.items()):
        try:
            await copilot.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up demo {session_id}: {e}")

    # Close all websockets
    for session_id, ws in list(websocket_connections.items()):
        try:
            await ws.close()
        except Exception as e:
            logger.error(f"Error closing websocket {session_id}: {e}")

    logger.info("Shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
