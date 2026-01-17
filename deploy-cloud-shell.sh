#!/bin/bash
# 🚀 Deploy Legal Bot to Cloud Run via Cloud Shell
# This script automates the entire deployment process

set -e  # Exit on error

echo "🚀 Starting Legal Bot Deployment to Cloud Run..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
BACKEND_SERVICE="legal-bot-backend"
FRONTEND_SERVICE="legal-bot-frontend"
GITHUB_REPO="anshumankush-jpg/legal-bot-production-level"
GITHUB_BRANCH="main"

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Backend Service: $BACKEND_SERVICE"
echo "  Frontend Service: $FRONTEND_SERVICE"
echo ""

# Step 1: Enable required APIs
echo -e "${YELLOW}Step 1: Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    iap.googleapis.com

echo -e "${GREEN}✅ APIs enabled${NC}"
echo ""

# Step 2: Clone repository
echo -e "${YELLOW}Step 2: Cloning repository...${NC}"
if [ -d "legal-bot-production-level" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd legal-bot-production-level
    git pull origin main
else
    git clone https://github.com/$GITHUB_REPO.git
    cd legal-bot-production-level
fi
echo -e "${GREEN}✅ Repository cloned${NC}"
echo ""

# Step 3: Build and deploy Backend
echo -e "${YELLOW}Step 3: Building and deploying Backend...${NC}"
cd backend

# Build Docker image
echo "Building Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $BACKEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --port 8000 \
    --set-env-vars "PORT=8000"

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
    --platform managed \
    --region $REGION \
    --format 'value(status.url)')

echo -e "${GREEN}✅ Backend deployed: $BACKEND_URL${NC}"
echo ""

# Step 4: Update frontend environment with backend URL
echo -e "${YELLOW}Step 4: Updating frontend configuration...${NC}"
cd ../frontend

# Update environment.prod.ts with backend URL
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

echo -e "${GREEN}✅ Frontend configuration updated${NC}"
echo ""

# Step 5: Build and deploy Frontend
echo -e "${YELLOW}Step 5: Building and deploying Frontend...${NC}"

# Build Docker image
echo "Building Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $FRONTEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --port 80

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE \
    --platform managed \
    --region $REGION \
    --format 'value(status.url)')

echo -e "${GREEN}✅ Frontend deployed: $FRONTEND_URL${NC}"
echo ""

# Step 6: Setup IAP for private access (optional)
echo -e "${YELLOW}Step 6: Setting up Identity-Aware Proxy for private access...${NC}"
read -p "Do you want to enable IAP for private access? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Update frontend to require authentication
    gcloud run services update $FRONTEND_SERVICE \
        --region $REGION \
        --no-allow-unauthenticated
    
    # Grant access to current user
    CURRENT_USER=$(gcloud config get-value account)
    gcloud run services add-iam-policy-binding $FRONTEND_SERVICE \
        --region $REGION \
        --member="user:$CURRENT_USER" \
        --role="roles/run.invoker"
    
    echo -e "${GREEN}✅ IAP enabled. Only authenticated users can access.${NC}"
else
    echo -e "${YELLOW}⚠️  IAP not enabled. Service is publicly accessible.${NC}"
fi
echo ""

# Summary
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo ""
echo -e "${BLUE}📊 Service URLs:${NC}"
echo "  Backend:  $BACKEND_URL"
echo "  Frontend: $FRONTEND_URL"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "  1. Test backend: curl $BACKEND_URL/health"
echo "  2. Test frontend: Open $FRONTEND_URL in browser"
echo "  3. Set environment variables if needed:"
echo "     gcloud run services update $BACKEND_SERVICE --set-env-vars KEY=value --region $REGION"
echo "  4. View logs:"
echo "     gcloud run services logs read $BACKEND_SERVICE --region $REGION"
echo ""
