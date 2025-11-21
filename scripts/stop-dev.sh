#!/bin/bash

echo "🛑 Stopping Demo Copilot..."
echo ""

# Function to kill process by PID file
kill_by_pidfile() {
    local pidfile=$1
    local service=$2

    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid 2>/dev/null || true
            echo "✓ Stopped $service (PID: $pid)"
        else
            echo "⚠ $service process not found (PID: $pid)"
        fi
        rm -f "$pidfile"
    else
        echo "⚠ No PID file for $service"
    fi
}

# Stop using PID files
if [ -d "logs" ]; then
    kill_by_pidfile "logs/backend.pid" "backend"
    kill_by_pidfile "logs/frontend.pid" "frontend"
fi

# Fallback: kill by process name
echo ""
echo "Checking for remaining processes..."

# Kill backend processes
pkill -f "python.*run_server.py" && echo "✓ Killed remaining backend processes" || true
pkill -f "uvicorn.*backend.api.main" && echo "✓ Killed remaining uvicorn processes" || true

# Kill frontend processes
pkill -f "next dev" && echo "✓ Killed remaining frontend processes" || true
pkill -f "node.*next" && echo "✓ Killed remaining node processes" || true

echo ""
echo "✅ All Demo Copilot processes stopped"
