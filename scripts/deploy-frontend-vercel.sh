#!/bin/bash

set -e

echo "🚀 Deploying Demo Copilot Frontend to Vercel..."

cd frontend

# Install Vercel CLI if not installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm i -g vercel
fi

# Deploy to Vercel
echo "🌐 Deploying to Vercel..."
vercel --prod \
  --env NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL} \
  --env NEXT_PUBLIC_WS_URL=${NEXT_PUBLIC_WS_URL}

echo "✅ Frontend deployed successfully!"
