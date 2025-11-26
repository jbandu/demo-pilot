#!/bin/sh
# Startup script for Next.js in production
# Handles both Docker (standalone at /app/server.js) and Railway builds

if [ -f "/app/server.js" ]; then
    echo "Starting Next.js server (standalone mode)"
    exec node /app/server.js
elif [ -f ".next/standalone/server.js" ]; then
    echo "Starting Next.js server (standalone in .next)"
    cd .next/standalone
    exec node server.js
else
    echo "Standalone server.js not found, falling back to next start"
    exec npx next start -p ${PORT:-3000}
fi
