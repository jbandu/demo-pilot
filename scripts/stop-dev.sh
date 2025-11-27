#!/bin/bash
echo "🛑 Stopping Demo Copilot..."
pkill -f "uvicorn api.main:app"
pkill -f "next dev"
echo "✅ Stopped"
