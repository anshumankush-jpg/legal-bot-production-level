# 🚀 Deploy to Google Cloud Run from GitHub

This guide will help you deploy your entire legal bot application (frontend + backend) to Cloud Run directly from your GitHub repository.

## 📋 Prerequisites

1. ✅ Google Cloud Project created
2. ✅ Billing enabled on your GCP project
3. ✅ GitHub repository: `https://github.com/anshumankush-jpg/legal-bot-production-level`
4. ✅ Cloud Build API enabled
5. ✅ Cloud Run API enabled

## 🎯 Deployment Options

### Option 1: Deploy via Cloud Console (Easiest - Recommended)

1. **Go to Cloud Run Console**
   - Navigate to: https://console.cloud.google.com/run
   - Click **"Create Service"**

2. **Select Source**
   - Choose: **"Continuously deploy from a repository (source or function)"**
   - Select: **"GitHub"**
   - Connect your GitHub account if not already connected
   - Select repository: `anshumankush-jpg/legal-bot-production-level`
   - Branch: `main`

3. **Configure Build**
   - **Build type:** Dockerfile
   - **Dockerfile location:** `backend/Dockerfile` (for backend) or `frontend/Dockerfile` (for frontend)
   - **Docker context:** `backend/` or `frontend/`

4. **Service Configuration**
   - **Service name:** `legal-bot-backend` (or `legal-bot-frontend`)
   - **Region:** `us-central1` (or your preferred region)
   - **Authentication:** Identity-Aware Proxy (IAP) for private access
   - **Ingress:** All
   - **Billing:** Request-based
   - **Scaling:** Auto-scaling (Min: 0, Max: 10)

5. **Repeat for Frontend**
   - Create a second service for the frontend
   - Use `frontend/Dockerfile`

### Option 2: Deploy via Cloud Build Triggers (Automated CI/CD)

#### Step 1: Create Cloud Build Trigger

```bash
# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# Create trigger for backend
gcloud builds triggers create github \
  --repo-name=legal-bot-production-level \
  --repo-owner=anshumankush-jpg \
  --branch-pattern="^main$" \
  --build-config=backend/cloudbuild.yaml \
  --name=deploy-backend

# Create trigger for frontend
gcloud builds triggers create github \
  --repo-name=legal-bot-production-level \
  --repo-owner=anshumankush-jpg \
  --branch-pattern="^main$" \
  --build-config=frontend/cloudbuild.yaml \
  --name=deploy-frontend
```

#### Step 2: Manual Trigger (Test)

```bash
# Trigger backend build
gcloud builds triggers run deploy-backend --branch=main

# Trigger frontend build
gcloud builds triggers run deploy-frontend --branch=main
```

### Option 3: Deploy Both with Single Root Config

```bash
# Create trigger for both services
gcloud builds triggers create github \
  --repo-name=legal-bot-production-level \
  --repo-owner=anshumankush-jpg \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --name=deploy-full-stack
```

## 🔧 Configuration Steps

### 1. Update Frontend Environment

After backend is deployed, update `frontend/src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://legal-bot-backend-XXXXX.us-central1.run.app', // Your backend URL
  // ... rest of config
};
```

### 2. Set Environment Variables

For **Backend** service:
```bash
gcloud run services update legal-bot-backend \
  --set-env-vars="OPENAI_API_KEY=your-key" \
  --region=us-central1
```

For **Frontend** service:
```bash
gcloud run services update legal-bot-frontend \
  --set-env-vars="BACKEND_URL=https://legal-bot-backend-XXXXX.us-central1.run.app" \
  --region=us-central1
```

### 3. Set Secrets (Recommended)

```bash
# Store secrets in Secret Manager
echo -n "your-openai-key" | gcloud secrets create openai-api-key --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Update service to use secrets
gcloud run services update legal-bot-backend \
  --update-secrets="OPENAI_API_KEY=openai-api-key:latest" \
  --region=us-central1
```

## 🔐 Authentication Setup (IAP)

1. **Enable IAP**
   ```bash
   gcloud run services update legal-bot-frontend \
     --ingress=all \
     --no-allow-unauthenticated \
     --region=us-central1
   ```

2. **Grant Access**
   - Go to Cloud Run → legal-bot-frontend → Permissions
   - Click "Add Principal"
   - Add your Google account email
   - Role: "Cloud Run Invoker"

## 📝 Deployment Checklist

- [ ] Backend deployed and running
- [ ] Frontend deployed and running
- [ ] Frontend environment updated with backend URL
- [ ] Environment variables set
- [ ] Secrets configured (if using)
- [ ] IAP enabled for private access
- [ ] Test both services are accessible
- [ ] Update CORS settings if needed

## 🧪 Testing Deployment

### Test Backend
```bash
curl https://legal-bot-backend-XXXXX.us-central1.run.app/health
```

### Test Frontend
```bash
curl https://legal-bot-frontend-XXXXX.us-central1.run.app/health
```

## 🔄 Continuous Deployment

Once triggers are set up:
- **Every push to `main` branch** → Automatic deployment
- **Build logs** available in Cloud Build console
- **Service logs** available in Cloud Run console

## 🐛 Troubleshooting

### Build Fails
- Check Cloud Build logs
- Verify Dockerfile paths are correct
- Check dependencies in requirements.txt/package.json

### Service Won't Start
- Check service logs in Cloud Run console
- Verify environment variables are set
- Check port configuration (backend: 8000, frontend: 80)

### 502 Bad Gateway
- Check if backend is running
- Verify CORS settings
- Check frontend API URL configuration

## 📚 Useful Commands

```bash
# View service logs
gcloud run services logs read legal-bot-backend --region=us-central1

# Update service
gcloud run services update legal-bot-backend --region=us-central1

# List services
gcloud run services list --region=us-central1

# Get service URL
gcloud run services describe legal-bot-backend --region=us-central1 --format="value(status.url)"
```

## 🎉 Success!

After deployment, you'll have:
- ✅ Backend API: `https://legal-bot-backend-XXXXX.us-central1.run.app`
- ✅ Frontend App: `https://legal-bot-frontend-XXXXX.us-central1.run.app`
- ✅ Automatic deployments on every push
- ✅ Private access via IAP

---

**Need help?** Check Cloud Build and Cloud Run logs for detailed error messages.
