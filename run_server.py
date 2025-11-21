#!/usr/bin/env python3
"""
Run the Demo Copilot FastAPI server
"""
import uvicorn
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # Set environment variables if not set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY not set in environment")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        print()

    if not os.getenv("ELEVENLABS_API_KEY"):
        print("Warning: ELEVENLABS_API_KEY not set in environment")
        print("Set it with: export ELEVENLABS_API_KEY='your-key-here'")
        print()

    # Default database URL
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./demo_copilot.db"
        print(f"Using default SQLite database: {os.environ['DATABASE_URL']}")
        print()

    print("Starting Demo Copilot API server...")
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print()

    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
