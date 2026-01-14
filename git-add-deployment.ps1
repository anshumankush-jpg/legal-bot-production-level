# PowerShell script to add Cloud Run deployment files

# Add deployment files
git add backend/Dockerfile
git add frontend/Dockerfile
git add frontend/nginx.conf
git add frontend/src/environments/environment.prod.ts
git add cloudbuild.yaml
git add deploy-cloud-shell.sh

# Commit
git commit -m "Add Cloud Run deployment files

- Backend Dockerfile for containerized deployment
- Frontend Dockerfile with nginx configuration
- Cloud Build configuration (cloudbuild.yaml)
- Deployment script (deploy-cloud-shell.sh)
- Production environment configuration"

# Push
git push origin main
