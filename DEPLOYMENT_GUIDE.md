# LEGID Deployment Guide

Complete guide for deploying LEGID (backend + frontend) to Google Cloud Run.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Backend Deployment](#backend-deployment)
6. [Frontend Deployment](#frontend-deployment)
7. [OAuth Configuration](#oauth-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts & Tools

- **Google Cloud Platform account** with billing enabled
- **gcloud CLI** installed ([Install here](https://cloud.google.com/sdk/docs/install))
- **Docker** installed (for local testing)
- **Node.js** 18+ and **npm**
- **Python** 3.10+
- **Git**

### GCP Project Setup

```bash
# Install gcloud CLI (if not installed)
# See: https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create legid-production --name="LEGID Production"

# Set the project as default
gcloud config set project legid-production

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable sql.googleapis.com
```

---

## Local Development Setup

### 1. Clone and Setup Repository

```bash
# Clone your repository
git clone https://github.com/your-org/legid.git
cd legid

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 2. Initialize Database

```bash
cd backend
python init_database.py init
```

### 3. Start Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access: `http://localhost:4200`

---

## Environment Configuration

### Backend Environment Variables

Create `backend/.env`:

```bash
# Copy from template
cp backend/.env.example backend/.env

# Edit with your values
nano backend/.env
```

**Required Variables:**

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# JWT Security
JWT_SECRET_KEY=generate-a-random-32-char-string-here

# Database (production)
DATABASE_URL=postgresql://user:password@/cloudsql/project:region:instance/dbname

# OAuth
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
GOOGLE_REDIRECT_URI=https://your-domain.com/auth/callback/google

MS_CLIENT_ID=your-microsoft-client-id
MS_CLIENT_SECRET=your-microsoft-secret
MS_REDIRECT_URI=https://your-domain.com/auth/callback/microsoft

# App URLs
FRONTEND_BASE_URL=https://your-frontend-domain.com
CORS_ORIGINS=https://your-frontend-domain.com
```

### Frontend Environment Variables

Create `frontend/.env.production`:

```bash
VITE_API_URL=https://your-backend-url.run.app
VITE_ENV=production
```

---

## Database Setup

### Option 1: Cloud SQL (Recommended for Production)

```bash
# Create Cloud SQL instance
gcloud sql instances create legid-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create legid_production \
  --instance=legid-db

# Create user
gcloud sql users create legid_user \
  --instance=legid-db \
  --password=YOUR_SECURE_PASSWORD

# Get connection name
gcloud sql instances describe legid-db --format="value(connectionName)"
# Output: project-id:region:instance-name
```

**Database URL format:**
```
postgresql://legid_user:password@/legid_production?host=/cloudsql/project-id:region:legid-db
```

### Option 2: SQLite (Development/Testing Only)

```bash
DATABASE_URL=sqlite:///./data/legal_bot.db
```

---

## Backend Deployment

### Step 1: Create Dockerfile (if not exists)

`backend/Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directories
RUN mkdir -p /app/data/faiss /app/data/docs

# Expose port
EXPOSE 8080

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Step 2: Store Secrets in Secret Manager

```bash
# OpenAI API Key
echo -n "sk-your-key" | gcloud secrets create openai-api-key --data-file=-

# JWT Secret
openssl rand -base64 32 | gcloud secrets create jwt-secret --data-file=-

# Google OAuth
echo -n "your-google-client-id" | gcloud secrets create google-client-id --data-file=-
echo -n "your-google-secret" | gcloud secrets create google-client-secret --data-file=-

# Microsoft OAuth
echo -n "your-ms-client-id" | gcloud secrets create ms-client-id --data-file=-
echo -n "your-ms-secret" | gcloud secrets create ms-client-secret --data-file=-

# Database URL
echo -n "postgresql://..." | gcloud secrets create database-url --data-file=-
```

### Step 3: Deploy Backend to Cloud Run

```bash
cd backend

# Build and deploy
gcloud run deploy legid-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="PORT=8080,DEBUG=False,LLM_PROVIDER=openai" \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest,JWT_SECRET_KEY=jwt-secret:latest,GOOGLE_CLIENT_ID=google-client-id:latest,GOOGLE_CLIENT_SECRET=google-client-secret:latest,MS_CLIENT_ID=ms-client-id:latest,MS_CLIENT_SECRET=ms-client-secret:latest,DATABASE_URL=database-url:latest" \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0

# Get the service URL
gcloud run services describe legid-backend --platform managed --region us-central1 --format="value(status.url)"
```

### Step 4: Connect to Cloud SQL (if using)

```bash
gcloud run deploy legid-backend \
  --add-cloudsql-instances project-id:region:legid-db \
  [... other flags from Step 3 ...]
```

### Alternative: If Org Policy Blocks Public Access

```bash
# Deploy as private service
gcloud run deploy legid-backend \
  --no-allow-unauthenticated \
  [... other flags ...]

# Grant access to specific users
gcloud run services add-iam-policy-binding legid-backend \
  --member="user:your-email@company.com" \
  --role="roles/run.invoker" \
  --region us-central1

# Or grant access to a service account
gcloud run services add-iam-policy-binding legid-backend \
  --member="serviceAccount:frontend-sa@project.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region us-central1
```

---

## Frontend Deployment

### Option 1: Deploy Frontend to Cloud Run

#### Step 1: Create Frontend Dockerfile

`frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Production image
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
```

#### Step 2: Create nginx.conf

`frontend/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 8080;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;

        # Gzip
        gzip on;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

        # SPA routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }
}
```

#### Step 3: Deploy Frontend

```bash
cd frontend

# Build and deploy
gcloud run deploy legid-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="VITE_API_URL=https://your-backend-url.run.app" \
  --memory 512Mi \
  --cpu 1

# Get URL
gcloud run services describe legid-frontend --platform managed --region us-central1 --format="value(status.url)"
```

### Option 2: Deploy to Firebase Hosting (Simpler for Static Sites)

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize Firebase in frontend directory
cd frontend
firebase init hosting

# Build
npm run build

# Deploy
firebase deploy --only hosting
```

---

## OAuth Configuration

### Update OAuth Redirect URIs

After deployment, update your OAuth redirect URIs:

#### Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Edit your OAuth Client
4. Add authorized redirect URIs:
   ```
   https://your-backend-url.run.app/api/auth/google/callback
   https://your-frontend-url.run.app/auth/callback/google
   ```

#### Azure Portal

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Select your app → **Authentication**
4. Add redirect URIs:
   ```
   https://your-backend-url.run.app/api/auth/microsoft/callback
   https://your-frontend-url.run.app/auth/callback/microsoft
   ```

### Update Environment Variables

```bash
# Update backend secrets
echo -n "https://your-frontend-url.run.app/auth/callback/google" | gcloud secrets versions add google-redirect-uri --data-file=-
echo -n "https://your-frontend-url.run.app/auth/callback/microsoft" | gcloud secrets versions add ms-redirect-uri --data-file=-

# Redeploy backend with new secrets
gcloud run deploy legid-backend \
  --set-secrets="GOOGLE_REDIRECT_URI=google-redirect-uri:latest,MS_REDIRECT_URI=ms-redirect-uri:latest" \
  [... existing flags ...]
```

---

## Custom Domain Setup (Optional)

### Map Custom Domain to Cloud Run

```bash
# Map domain to backend
gcloud run domain-mappings create \
  --service legid-backend \
  --domain api.yourdomain.com \
  --region us-central1

# Map domain to frontend
gcloud run domain-mappings create \
  --service legid-frontend \
  --domain app.yourdomain.com \
  --region us-central1

# Follow DNS instructions to verify domain
```

---

## Troubleshooting

### 403 Forbidden Error (Org Policy)

**Problem**: Org policy blocks `allUsers` as invoker.

**Solution 1 - Private Service**:
```bash
# Deploy without public access
gcloud run deploy legid-backend --no-allow-unauthenticated

# Grant specific users access
gcloud run services add-iam-policy-binding legid-backend \
  --member="user:your-email@company.com" \
  --role="roles/run.invoker"
```

**Solution 2 - Use Cloud IAP** (Identity-Aware Proxy):
Enable IAP for your Cloud Run service to require authentication.

### CORS Errors

**Problem**: Frontend can't call backend APIs.

**Solution**:
1. Ensure `CORS_ORIGINS` includes your frontend URL
2. Update backend environment:
   ```bash
   gcloud run services update legid-backend \
     --set-env-vars="CORS_ORIGINS=https://your-frontend-url.run.app"
   ```

### OAuth redirect_uri_mismatch

**Problem**: OAuth providers reject redirect URI.

**Solution**:
1. Ensure redirect URIs in OAuth console **exactly match** your deployed URLs
2. Include `https://` (not `http://`)
3. No trailing slashes unless your code includes them
4. Redeploy after updating redirect URIs in environment variables

### Database Connection Issues

**Problem**: Can't connect to Cloud SQL.

**Solution**:
```bash
# Verify Cloud SQL connection is added
gcloud run services describe legid-backend \
  --format="value(spec.template.spec.containers[0].volumeMounts)"

# Should show Cloud SQL connection
# If not, redeploy with --add-cloudsql-instances flag
```

### Out of Memory Errors

**Problem**: Service crashes with OOM.

**Solution**:
```bash
# Increase memory allocation
gcloud run services update legid-backend --memory 2Gi
```

### Cold Start Performance

**Problem**: First request after idle is slow.

**Solution**:
```bash
# Keep at least 1 instance running (costs more)
gcloud run services update legid-backend --min-instances 1
```

---

## Monitoring & Logs

### View Logs

```bash
# Backend logs
gcloud run services logs read legid-backend --limit 50

# Follow logs in real-time
gcloud run services logs tail legid-backend

# Frontend logs
gcloud run services logs read legid-frontend --limit 50
```

### View Metrics

```bash
# Open Cloud Console
gcloud run services describe legid-backend --format="value(status.url)"

# Then navigate to Monitoring section in Cloud Console
```

---

## Cost Optimization

### Reduce Costs

1. **Use minimum resources**:
   ```bash
   --memory 512Mi --cpu 0.5 --min-instances 0
   ```

2. **Use SQLite for dev/test** (not production)

3. **Set request timeout**:
   ```bash
   --timeout 60  # Default is 300
   ```

4. **Use cheaper LLM models**:
   ```
   OPENAI_CHAT_MODEL=gpt-4o-mini  # Much cheaper than gpt-4
   ```

5. **Monitor usage**:
   ```bash
   gcloud billing accounts list
   ```

---

## Security Checklist

- [ ] Use strong JWT secret (32+ random characters)
- [ ] Enable HTTPS only (Cloud Run does this by default)
- [ ] Set secure CORS origins (no wildcards in production)
- [ ] Use Secret Manager for sensitive data
- [ ] Enable Cloud Armor (DDoS protection) if needed
- [ ] Regular security audits
- [ ] Monitor for suspicious auth patterns
- [ ] Rotate OAuth secrets periodically
- [ ] Use Cloud SQL with private IP if possible
- [ ] Enable audit logging

---

## Next Steps

1. ✅ Deploy backend and frontend
2. ✅ Configure OAuth
3. ✅ Test authentication flow
4. ⬜ Set up monitoring alerts
5. ⬜ Configure backup strategy
6. ⬜ Set up CI/CD pipeline
7. ⬜ Load testing
8. ⬜ Security audit

---

## Support

- **GCP Issues**: [Google Cloud Support](https://cloud.google.com/support)
- **OAuth Issues**: See `SETUP_OAUTH.md`
- **Application Issues**: Check application logs

---

## Quick Commands Reference

```bash
# Deploy backend
gcloud run deploy legid-backend --source backend/

# Deploy frontend
gcloud run deploy legid-frontend --source frontend/

# View logs
gcloud run services logs tail legid-backend

# Update environment variable
gcloud run services update legid-backend --set-env-vars="KEY=value"

# Update secret
echo -n "new-value" | gcloud secrets versions add secret-name --data-file=-

# Delete service
gcloud run services delete legid-backend
```
