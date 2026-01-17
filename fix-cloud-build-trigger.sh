#!/bin/bash
# 🔧 FIX: Cloud Build Trigger - Dockerfile Path Issue
# This fixes the trigger that's looking for Dockerfile in root
# Run this in Cloud Shell

set -e

PROJECT_ID="auth-login-page-481522"
TRIGGER_ID="4038edb0-98dd-4c76-a647-a0035d8889fd"  # From your error logs
REGION="europe-west1"
SERVICE_NAME="legal-bot-production-level"

echo "🔧 Fixing Cloud Build Trigger..."
echo ""

# Option 1: Delete the problematic trigger and create a new one
echo "🗑️  Deleting old trigger..."
gcloud builds triggers delete $TRIGGER_ID \
    --project $PROJECT_ID \
    --quiet 2>/dev/null || echo "Trigger not found or already deleted"

echo ""
echo "✅ Old trigger deleted"
echo ""

# Option 2: Create a proper cloudbuild.yaml in backend that will work
echo "📝 Creating proper backend cloudbuild.yaml..."
cd ~/legal-bot-production-level/legal-bot-production-level/backend 2>/dev/null || cd ~/legal-bot-production-level/backend

cat > cloudbuild.yaml << 'EOF'
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: 
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/legal-bot-backend:$SHORT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/legal-bot-backend:latest'
      - '-f'
      - 'Dockerfile'
      - '.'
  
  # Push the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/legal-bot-backend:$SHORT_SHA']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/legal-bot-backend:latest']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'legal-bot-backend'
      - '--image=gcr.io/$PROJECT_ID/legal-bot-backend:$SHORT_SHA'
      - '--region=europe-west1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--memory=2Gi'
      - '--cpu=2'
      - '--timeout=300'
      - '--max-instances=10'
      - '--port=8000'

options:
  logging: CLOUD_LOGGING_ONLY

timeout: '1200s'
EOF

echo "✅ cloudbuild.yaml created in backend/"
echo ""

# Option 3: Create new trigger that uses backend/cloudbuild.yaml
echo "🔧 Creating new trigger with correct configuration..."
gcloud builds triggers create github \
    --repo-name=legal-bot-production-level \
    --repo-owner=anshumankush-jpg \
    --branch-pattern="^main$" \
    --build-config=backend/cloudbuild.yaml \
    --name=deploy-legal-bot-backend \
    --project $PROJECT_ID \
    --description="Deploy legal bot backend from backend/ directory"

echo ""
echo "✅ New trigger created!"
echo ""
echo "📝 Alternative: Use direct deployment (no trigger)"
echo ""
echo "To deploy directly without triggers, use:"
echo "  cd backend"
echo "  gcloud run deploy legal-bot-backend --source . --region europe-west1 --project $PROJECT_ID --allow-unauthenticated"
echo ""
