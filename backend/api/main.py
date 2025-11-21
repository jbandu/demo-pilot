"""
Demo Copilot FastAPI Server
Provides REST API and WebSocket endpoints for demo management
"""
import asyncio
import os
from typing import Dict, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

from agents.demo_copilot import DemoCopilot, DemoState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Active demo sessions
active_sessions: Dict[str, DemoCopilot] = {}

# WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    logger.info("Starting Demo Copilot API server...")
    yield
    logger.info("Shutting down Demo Copilot API server...")

    # Cleanup all active sessions
    for session_id, copilot in active_sessions.items():
        logger.info(f"Cleaning up session: {session_id}")
        try:
            await copilot.stop_demo()
        except Exception as e:
            logger.error(f"Error stopping session {session_id}: {e}")


# Initialize FastAPI app
app = FastAPI(
    title="Demo Copilot API",
    description="Autonomous Product Demonstration Agent",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models

class CreateDemoRequest(BaseModel):
    """Request to create a new demo session"""
    product: str = "insign"
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    voice_id: str = "Rachel"
    headless: bool = True


class DemoSessionResponse(BaseModel):
    """Demo session response"""
    session_id: str
    product: str
    state: str
    customer_name: Optional[str]
    created_at: str


class QuestionRequest(BaseModel):
    """Question from customer"""
    question: str


class QuestionResponse(BaseModel):
    """Answer to customer question"""
    question: str
    answer: str
    response_time_ms: int
    timestamp: str


class DemoControlRequest(BaseModel):
    """Control request (pause, resume, skip)"""
    action: str  # "pause", "resume", "skip"
    section: Optional[str] = None  # For skip action


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Demo Copilot API",
        "status": "running",
        "version": "1.0.0",
        "active_sessions": len(active_sessions)
    }


@app.get("/health")
async def health_check():
    """Health check with details"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(active_sessions),
        "active_connections": len(active_connections)
    }


@app.post("/demo/create", response_model=DemoSessionResponse)
async def create_demo(request: CreateDemoRequest, background_tasks: BackgroundTasks):
    """
    Create a new demo session

    Args:
        request: Demo creation parameters

    Returns:
        Demo session info
    """
    logger.info(f"Creating demo session for product: {request.product}")

    try:
        # Create demo copilot
        copilot = DemoCopilot(
            headless=request.headless,
            voice_id=request.voice_id
        )

        # Initialize
        await copilot.initialize(
            product=request.product,
            customer_name=request.customer_name
        )

        # Store session
        active_sessions[copilot.session_id] = copilot

        logger.info(f"Demo session created: {copilot.session_id}")

        return DemoSessionResponse(
            session_id=copilot.session_id,
            product=request.product,
            state=copilot.state,
            customer_name=request.customer_name,
            created_at=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Failed to create demo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/demo/{session_id}/start")
async def start_demo(session_id: str, background_tasks: BackgroundTasks):
    """
    Start a demo session

    Args:
        session_id: Demo session ID

    Returns:
        Status
    """
    copilot = active_sessions.get(session_id)

    if not copilot:
        raise HTTPException(status_code=404, detail="Session not found")

    logger.info(f"Starting demo: {session_id}")

    # Run demo in background
    background_tasks.add_task(run_demo_background, copilot)

    return {
        "status": "started",
        "session_id": session_id
    }


async def run_demo_background(copilot: DemoCopilot):
    """Run demo in background task"""
    try:
        result = await copilot.start_demo()
        logger.info(f"Demo completed: {copilot.session_id}")

        # Send completion notification via WebSocket
        if copilot.session_id in active_connections:
            ws = active_connections[copilot.session_id]
            await ws.send_json({
                "type": "demo_completed",
                "data": result
            })

    except Exception as e:
        logger.error(f"Demo failed: {e}")


@app.post("/demo/{session_id}/control")
async def control_demo(session_id: str, request: DemoControlRequest):
    """
    Control demo (pause, resume, skip)

    Args:
        session_id: Demo session ID
        request: Control action

    Returns:
        Status
    """
    copilot = active_sessions.get(session_id)

    if not copilot:
        raise HTTPException(status_code=404, detail="Session not found")

    logger.info(f"Control action: {request.action} for session: {session_id}")

    try:
        if request.action == "pause":
            await copilot.pause_demo()
        elif request.action == "resume":
            await copilot.resume_demo()
        elif request.action == "skip" and request.section:
            await copilot.skip_to_section(request.section)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")

        return {
            "status": "success",
            "action": request.action,
            "session_id": session_id
        }

    except Exception as e:
        logger.error(f"Control action failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/demo/{session_id}/question", response_model=QuestionResponse)
async def ask_question(session_id: str, request: QuestionRequest):
    """
    Ask a question during demo

    Args:
        session_id: Demo session ID
        request: Question

    Returns:
        Answer
    """
    copilot = active_sessions.get(session_id)

    if not copilot:
        raise HTTPException(status_code=404, detail="Session not found")

    logger.info(f"Question for session {session_id}: {request.question}")

    try:
        result = await copilot.ask_question(request.question)

        return QuestionResponse(**result)

    except Exception as e:
        logger.error(f"Question handling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/demo/{session_id}/status")
async def get_demo_status(session_id: str):
    """
    Get demo status

    Args:
        session_id: Demo session ID

    Returns:
        Current status
    """
    copilot = active_sessions.get(session_id)

    if not copilot:
        raise HTTPException(status_code=404, detail="Session not found")

    return copilot.get_status()


@app.delete("/demo/{session_id}")
async def stop_demo(session_id: str):
    """
    Stop and delete demo session

    Args:
        session_id: Demo session ID

    Returns:
        Status
    """
    copilot = active_sessions.get(session_id)

    if not copilot:
        raise HTTPException(status_code=404, detail="Session not found")

    logger.info(f"Stopping demo: {session_id}")

    try:
        await copilot.stop_demo()

        # Remove from active sessions
        del active_sessions[session_id]

        # Close WebSocket if exists
        if session_id in active_connections:
            await active_connections[session_id].close()
            del active_connections[session_id]

        return {
            "status": "stopped",
            "session_id": session_id
        }

    except Exception as e:
        logger.error(f"Stop failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/demo/sessions")
async def list_sessions():
    """
    List all active demo sessions

    Returns:
        List of active sessions
    """
    sessions = []

    for session_id, copilot in active_sessions.items():
        status = copilot.get_status()
        sessions.append(status)

    return {
        "total": len(sessions),
        "sessions": sessions
    }


# WebSocket endpoint for real-time streaming

@app.websocket("/ws/demo/{session_id}")
async def websocket_demo(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time demo streaming

    Streams:
    - Screenshots from browser
    - Audio chunks from voice
    - State changes
    - Progress updates
    """
    await websocket.accept()

    copilot = active_sessions.get(session_id)

    if not copilot:
        await websocket.send_json({
            "type": "error",
            "message": "Session not found"
        })
        await websocket.close()
        return

    # Store connection
    active_connections[session_id] = websocket

    logger.info(f"WebSocket connected for session: {session_id}")

    # Set up callbacks
    async def on_screenshot(screenshot_b64: str):
        try:
            await websocket.send_json({
                "type": "screenshot",
                "data": screenshot_b64,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to send screenshot: {e}")

    async def on_audio(audio_chunk: bytes):
        try:
            await websocket.send_bytes(audio_chunk)
        except Exception as e:
            logger.error(f"Failed to send audio: {e}")

    async def on_state_change(state: DemoState):
        try:
            await websocket.send_json({
                "type": "state_change",
                "state": state,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to send state change: {e}")

    async def on_progress(status: dict):
        try:
            await websocket.send_json({
                "type": "progress_update",
                "data": status,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to send progress: {e}")

    # Register callbacks
    copilot.on_screenshot = on_screenshot
    copilot.on_audio = on_audio
    copilot.on_state_change = on_state_change
    copilot.on_progress_update = on_progress

    try:
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_json()

            # Handle client messages (e.g., questions, control commands)
            message_type = data.get("type")

            if message_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif message_type == "question":
                question = data.get("question")
                result = await copilot.ask_question(question)
                await websocket.send_json({
                    "type": "answer",
                    "data": result
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
        if session_id in active_connections:
            del active_connections[session_id]

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if session_id in active_connections:
            del active_connections[session_id]


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
