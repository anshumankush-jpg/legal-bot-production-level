#!/bin/bash
# 🔧 COMPLETE FIX: Cloud Build Trigger Dockerfile Error
# Run this in Cloud Shell

set -e

PROJECT_ID="auth-login-page-481522"
TRIGGER_ID="4038edb0-98dd-4c76-a647-a0035d8889fd"
REGION="europe-west1"
YOUR_EMAIL="anshuman.kush@predictivetechlabs.com"

echo "🔧 Fixing Cloud Build Trigger Issue..."
echo ""

# Step 1: Delete the problematic trigger
echo "🗑️  Step 1: Deleting problematic trigger..."
gcloud builds triggers delete $TRIGGER_ID \
    --project $PROJECT_ID \
    --quiet 2>/dev/null || echo "Trigger already deleted or not found"

echo "✅ Trigger deleted"
echo ""

# Step 2: Setup repository
echo "📥 Step 2: Setting up repository..."
cd ~ && rm -rf legal-bot-production-level && git clone https://github.com/anshumankush-jpg/legal-bot-production-level.git && cd legal-bot-production-level

# Step 3: Deploy Backend directly (no trigger needed)
echo ""
echo "🚀 Step 3: Deploying Backend directly..."
cd backend

# Ensure Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    cat > Dockerfile << 'EOF'
FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
RUN mkdir -p ./data/docs ./data/faiss ./data/uploads
ENV PYTHONUNBUFFERED=1 PORT=8000
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
fi

# Deploy from backend directory
gcloud run deploy legal-bot-backend \
    --source . \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --port 8000

BACKEND_URL=$(gcloud run services describe legal-bot-backend --region $REGION --project $PROJECT_ID --format 'value(status.url)')
echo "✅ Backend: $BACKEND_URL"

# Grant access
gcloud run services add-iam-policy-binding legal-bot-backend \
    --region $REGION \
    --project $PROJECT_ID \
    --member="user:$YOUR_EMAIL" \
    --role="roles/run.invoker" \
    --quiet 2>/dev/null

# Step 4: Deploy Frontend
echo ""
echo "🎨 Step 4: Deploying Frontend..."
cd ../frontend

# Update frontend config
mkdir -p src/environments
cat > src/environments/environment.prod.ts << EOF
export const environment = {
  production: true,
  apiUrl: '$BACKEND_URL',
  showEvaluation: false,
  googleClientId: '',
  microsoftClientId: '',
  enableMultiAccount: false,
  enableLawyerVerification: true
};
EOF

# Deploy frontend
gcloud run deploy legal-bot-frontend \
    --source . \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --port 80

FRONTEND_URL=$(gcloud run services describe legal-bot-frontend --region $REGION --project $PROJECT_ID --format 'value(status.url)')
echo "✅ Frontend: $FRONTEND_URL"

# Grant access
gcloud run services add-iam-policy-binding legal-bot-frontend \
    --region $REGION \
    --project $PROJECT_ID \
    --member="user:$YOUR_EMAIL" \
    --role="roles/run.invoker" \
    --quiet 2>/dev/null

echo ""
echo "🎉 Deployment Complete!"
echo "Backend:  $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo ""
echo "✅ The trigger has been deleted. Future deployments can be done manually or"
echo "   you can create a new trigger using backend/cloudbuild.yaml"
echo ""
