#!/bin/bash

set -e

echo "🚀 Deploying Complete Demo Copilot System to Railway..."
echo ""
echo "Note: This script assumes you have Railway CLI installed and configured."
echo "Install with: npm i -g @railway/cli && railway login"
echo ""

# Check if railway CLI is available
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "   npm i -g @railway/cli"
    echo "   railway login"
    exit 1
fi

# Deploy backend
echo ""
echo "📦 Step 1/2: Deploying Backend..."
cd backend
railway up --service backend
cd ..

# Deploy frontend
echo ""
echo "📦 Step 2/2: Deploying Frontend..."
cd frontend
railway up --service frontend
cd ..

echo ""
echo "✅ Full deployment complete!"
echo ""
echo "🔗 Check your Railway dashboard for service URLs"
