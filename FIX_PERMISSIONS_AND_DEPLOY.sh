#!/bin/bash
# 🔧 FIX PERMISSIONS + DEPLOY - Complete Solution
# This fixes the storage permission error and deploys
# Run this in Cloud Shell

set -e

PROJECT_ID="auth-login-page-481522"
REGION="europe-west1"
BACKEND_SERVICE="legal-bot-backend"
FRONTEND_SERVICE="legal-bot-frontend"
YOUR_EMAIL="anshuman.kush@predictivetechlabs.com"

echo "🔧 Step 1: Fixing Cloud Build Permissions..."
echo ""

# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

if [ -z "$PROJECT_NUMBER" ]; then
    echo "❌ Could not get project number"
    exit 1
fi

echo "Project Number: $PROJECT_NUMBER"
echo ""

# Grant all necessary permissions to Cloud Build service account
echo "Granting permissions to Cloud Build service account..."

# Storage permissions (for uploading source code)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/storage.admin" \
    --quiet

# Cloud Run permissions (for deploying)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin" \
    --quiet

# Service Account User (for Cloud Run deployments)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser" \
    --quiet

# Also grant to compute service account (sometimes needed)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/storage.admin" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/run.admin" \
    --quiet

echo "✅ Permissions granted!"
echo ""

# Wait a moment for permissions to propagate
echo "⏳ Waiting for permissions to propagate..."
sleep 5

# Step 2: Setup repository
echo ""
echo "📥 Step 2: Setting up repository..."
cd ~ && rm -rf legal-bot-production-level && git clone https://github.com/anshumankush-jpg/legal-bot-production-level.git && cd legal-bot-production-level

# Step 3: Deploy Backend
echo ""
echo "🚀 Step 3: Deploying Backend..."
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

# Deploy backend
echo "Building and deploying backend (this may take 5-10 minutes)..."
gcloud run deploy $BACKEND_SERVICE \
    --source . \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --port 8000

BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
    --region $REGION \
    --project $PROJECT_ID \
    --format 'value(status.url)' 2>/dev/null)

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Backend deployment failed!"
    exit 1
fi

echo "✅ Backend deployed: $BACKEND_URL"

# Grant access
gcloud run services add-iam-policy-binding $BACKEND_SERVICE \
    --region $REGION \
    --project $PROJECT_ID \
    --member="user:$YOUR_EMAIL" \
    --role="roles/run.invoker" \
    --quiet 2>/dev/null || echo "Access already granted"

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

# Ensure Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    cat > Dockerfile << 'EOF'
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF
fi

# Ensure nginx.conf exists
if [ ! -f "nginx.conf" ]; then
    cat > nginx.conf << 'EOF'
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
    location /health {
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
fi

# Deploy frontend
echo "Building and deploying frontend (this may take 5-10 minutes)..."
gcloud run deploy $FRONTEND_SERVICE \
    --source . \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --port 80

FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE \
    --region $REGION \
    --project $PROJECT_ID \
    --format 'value(status.url)' 2>/dev/null)

if [ -z "$FRONTEND_URL" ]; then
    echo "❌ Frontend deployment failed!"
    exit 1
fi

echo "✅ Frontend deployed: $FRONTEND_URL"

# Grant access
gcloud run services add-iam-policy-binding $FRONTEND_SERVICE \
    --region $REGION \
    --project $PROJECT_ID \
    --member="user:$YOUR_EMAIL" \
    --role="roles/run.invoker" \
    --quiet 2>/dev/null || echo "Access already granted"

echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "📊 Service URLs:"
echo "  Backend:  $BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"
echo ""
echo "✅ Access granted to: $YOUR_EMAIL"
echo ""
echo "💡 Open $FRONTEND_URL in your browser!"
echo ""
