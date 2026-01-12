# GCP Deployment Guide

This backend is designed to run on Google Cloud Platform while using Azure services for AI capabilities.

## Architecture

- **Compute**: Cloud Run or GKE
- **Storage**: Cloud Storage (optional) or local files
- **Database**: Firestore (optional) or JSON files
- **Secrets**: Secret Manager
- **AI Services**: Azure OpenAI + Azure AI Search (external)

## Deployment Options

### Option 1: Cloud Run (Recommended for Serverless)

#### 1. Build Container

```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/plaza-ai-backend
```

#### 2. Deploy to Cloud Run

```bash
gcloud run deploy plaza-ai-backend \
  --image gcr.io/PROJECT_ID/plaza-ai-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com" \
  --set-secrets="AZURE_OPENAI_API_KEY=azure-openai-key:latest" \
  --set-secrets="AZURE_SEARCH_API_KEY=azure-search-key:latest"
```

#### 3. Store Secrets in Secret Manager

```bash
# Create secrets
echo -n "your-azure-openai-key" | gcloud secrets create azure-openai-key --data-file=-
echo -n "your-azure-search-key" | gcloud secrets create azure-search-key --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding azure-openai-key \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Option 2: GKE (Kubernetes)

#### 1. Create Kubernetes Secrets

```bash
kubectl create secret generic azure-credentials \
  --from-literal=azure-openai-endpoint=https://your-resource.openai.azure.com \
  --from-literal=azure-openai-key=your-key \
  --from-literal=azure-search-endpoint=https://your-search.search.windows.net \
  --from-literal=azure-search-key=your-key
```

#### 2. Deploy with Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: plaza-ai-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: plaza-ai-backend
  template:
    metadata:
      labels:
        app: plaza-ai-backend
    spec:
      containers:
      - name: backend
        image: gcr.io/PROJECT_ID/plaza-ai-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: AZURE_OPENAI_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: azure-credentials
              key: azure-openai-endpoint
        - name: AZURE_OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: azure-credentials
              key: azure-openai-key
        - name: AZURE_SEARCH_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: azure-credentials
              key: azure-search-endpoint
        - name: AZURE_SEARCH_API_KEY
          valueFrom:
            secretKeyRef:
              name: azure-credentials
              key: azure-search-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: plaza-ai-backend
spec:
  selector:
    app: plaza-ai-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Option 3: Cloud Functions (Not Recommended - Cold Start Issues)

For Cloud Functions, you'd need to adapt the FastAPI app to use Cloud Functions framework.

## Environment Variables for GCP

Set these in Cloud Run, GKE, or via Secret Manager:

```bash
# Azure Services
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=<from-secret-manager>
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=<from-secret-manager>
AZURE_SEARCH_INDEX_NAME=legal-documents-index

# GCP Project (auto-detected)
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional: Use GCP Storage
USE_GCP_STORAGE=true
GCP_STORAGE_BUCKET=plaza-ai-documents

# Optional: Use Firestore
USE_FIRESTORE=true
```

## Storage Options

### Local Storage (Default)
- Matters stored in JSON file: `./data/docs/matters.json`
- Documents stored locally
- Works on Cloud Run with ephemeral storage

### GCP Cloud Storage (Optional)
- Upload documents to Cloud Storage bucket
- Matters can reference GCS paths
- Persistent across container restarts

### Firestore (Optional)
- Replace JSON file storage with Firestore
- Better for production scale
- Automatic scaling

## Monitoring & Logging

### Cloud Logging
Logs automatically go to Cloud Logging:
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

### Cloud Monitoring
Set up alerts for:
- Request latency
- Error rates
- Azure API quota usage

## Scaling

### Cloud Run
- Auto-scales from 0 to N instances
- Configure min/max instances
- Set concurrency per instance

### GKE
- Use Horizontal Pod Autoscaler
- Configure based on CPU/memory or custom metrics

## Cost Optimization

1. **Use Cloud Run** for serverless (pay per request)
2. **Set min instances to 0** when not in use
3. **Use regional persistent disks** for local storage if needed
4. **Cache embeddings** to reduce Azure OpenAI calls
5. **Batch document processing** to reduce API calls

## Security

1. **Use Secret Manager** for all API keys
2. **Enable IAM** authentication for Cloud Run
3. **Use VPC** for GKE if accessing private resources
4. **Enable Cloud Armor** for DDoS protection
5. **Use Workload Identity** for service-to-service auth

## CI/CD Pipeline

### Cloud Build

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/plaza-ai-backend:$SHORT_SHA', '.']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/plaza-ai-backend:$SHORT_SHA']
  
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'plaza-ai-backend'
      - '--image=gcr.io/$PROJECT_ID/plaza-ai-backend:$SHORT_SHA'
      - '--region=us-central1'
```

## Testing Locally with GCP Emulators

```bash
# Install emulators
gcloud components install cloud-firestore-emulator
gcloud components install pubsub-emulator

# Run emulators
gcloud beta emulators firestore start --host-port=localhost:8080
```

## Troubleshooting

### Cold Starts (Cloud Run)
- Set min instances > 0
- Optimize container startup time
- Use Cloud Run Jobs for batch processing

### Azure API Limits
- Implement exponential backoff
- Use batch processing
- Cache embeddings

### Storage Issues
- Check Cloud Storage bucket permissions
- Verify Firestore indexes
- Monitor disk usage on Cloud Run

