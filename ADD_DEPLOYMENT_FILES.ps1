# Add Cloud Run deployment files to git
# Based on your code block (lines 2-13)

# Add backend Dockerfile
git add backend/Dockerfile

# Add frontend Dockerfile
git add frontend/Dockerfile

# Add nginx configuration
git add frontend/nginx.conf

# Add production environment config
git add frontend/src/environments/environment.prod.ts

# Add Cloud Build configuration
git add cloudbuild.yaml

# Add deployment script
git add deploy-cloud-shell.sh

# Commit
git commit -m "Add Cloud Run deployment files"

# Push
git push origin main
