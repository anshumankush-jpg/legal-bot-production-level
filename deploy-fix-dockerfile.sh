#!/bin/bash
# 🔧 FIX: Dockerfile Path Issue - Complete Solution
# This fixes the "unable to evaluate symlinks in Dockerfile path" error
# Run this in Google Cloud Shell

set -e

PROJECT_ID="auth-login-page-481522"
REGION="europe-west1"
BACKEND_SERVICE="legal-bot-backend"
FRONTEND_SERVICE="legal-bot-frontend"
YOUR_EMAIL="anshuman.kush@predictivetechlabs.com"
GITHUB_REPO="anshumankush-jpg/legal-bot-production-level"

echo "🔧 Fixing Dockerfile Path Issue..."
echo ""

# Step 1: Setup repository
echo "📥 Setting up repository..."
REPO_DIR="$HOME/legal-bot-production-level"
if [ -d "$REPO_DIR" ]; then
    cd $REPO_DIR
    git pull origin main 2>/dev/null || echo "Git pull skipped"
else
    cd $HOME
    git clone https://github.com/$GITHUB_REPO.git
    cd $REPO_DIR
fi

# Step 2: Fix Backend - Deploy from backend directory
echo ""
echo "🔧 Fixing Backend Deployment..."
cd backend

# Ensure Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "Creating Dockerfile..."
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

# Deploy from backend directory (Dockerfile is in current dir)
echo "🚀 Deploying backend from backend/ directory..."
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
    --format 'value(status.url)')

echo "✅ Backend deployed: $BACKEND_URL"

# Grant access
gcloud run services add-iam-policy-binding $BACKEND_SERVICE \
    --region $REGION \
    --project $PROJECT_ID \
    --member="user:$YOUR_EMAIL" \
    --role="roles/run.invoker" \
    --quiet 2>/dev/null

# Step 3: Fix Frontend
echo ""
echo "🔧 Fixing Frontend Deployment..."
cd ../frontend

# Ensure Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "Creating frontend Dockerfile..."
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
    echo "Creating nginx.conf..."
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

# Deploy from frontend directory (Dockerfile is in current dir)
echo "🚀 Deploying frontend from frontend/ directory..."
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
    --format 'value(status.url)')

echo "✅ Frontend deployed: $FRONTEND_URL"

# Grant access
gcloud run services add-iam-policy-binding $FRONTEND_SERVICE \
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
echo "✅ The key fix: Deploy from the directory containing the Dockerfile!"
