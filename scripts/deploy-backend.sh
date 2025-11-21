#!/bin/bash

set -e

echo "🚀 Deploying Demo Copilot Backend..."

# Configuration
PROJECT_ID="your-gcp-project-id"
SERVICE_NAME="demo-copilot-backend"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Build Docker image
echo "📦 Building Docker image..."
cd backend
docker build -t ${IMAGE_NAME}:latest .

# Push to Google Container Registry
echo "⬆️  Pushing image to GCR..."
docker push ${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 3600 \
  --concurrency 10 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} \
  --set-env-vars ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY} \
  --set-env-vars OPENAI_API_KEY=${OPENAI_API_KEY} \
  --set-env-vars DATABASE_URL=${DATABASE_URL} \
  --set-env-vars REDIS_URL=${REDIS_URL}

echo "✅ Backend deployed successfully!"
echo "🔗 Service URL: $(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')"
