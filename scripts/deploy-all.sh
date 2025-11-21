#!/bin/bash

set -e

echo "🚀 Deploying Complete Demo Copilot System..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Deploy backend
echo ""
echo "📦 Step 1/2: Deploying Backend..."
./scripts/deploy-backend.sh

# Get backend URL
BACKEND_URL=$(gcloud run services describe demo-copilot-backend --region us-central1 --format 'value(status.url)')
export NEXT_PUBLIC_API_URL=$BACKEND_URL
export NEXT_PUBLIC_WS_URL="${BACKEND_URL/https/wss}"

# Deploy frontend
echo ""
echo "📦 Step 2/2: Deploying Frontend..."
./scripts/deploy-frontend-vercel.sh

echo ""
echo "✅ Full deployment complete!"
echo ""
echo "🔗 Backend API: $BACKEND_URL"
echo "🔗 Frontend: Check Vercel output above"
