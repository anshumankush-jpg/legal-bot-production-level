# LEGID - QUICK START & DEPLOYMENT GUIDE

## 🚀 LOCAL DEVELOPMENT (5 Minutes)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Cloud SDK
- GCP Project with billing enabled

### Step 1: Database Setup (2 min)

```bash
# Set your GCP project
export GCP_PROJECT_ID="your-project-id"

# Create BigQuery tables
cd database/bigquery
python create_tables.py --project=$GCP_PROJECT_ID --dataset=legid_dev

# Create GCS buckets
python setup_gcs_buckets.py --project=$GCP_PROJECT_ID --prefix=legid-dev
```

### Step 2: Backend Setup (2 min)

```bash
cd backend

# Install dependencies
pip install fastapi uvicorn google-cloud-bigquery google-cloud-storage \
    PyJWT bcrypt python-dotenv openai python-multipart

# Create .env
cat > .env << 'EOF'
DEBUG=True
HOST=0.0.0.0
PORT=8000

JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256

GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-secret

GCP_PROJECT_ID=your-project-id
BIGQUERY_DATASET=legid_dev
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

GCS_UPLOADS_BUCKET=legid-dev-uploads-prod
GCS_LAWYER_VERIFICATION_BUCKET=legid-dev-lawyer-verification

OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
EOF

# Run backend
uvicorn app.main:app --reload
```

### Step 3: Frontend Setup (1 min)

```bash
cd frontend

# Install
npm install

# Create .env
echo "VITE_API_URL=http://localhost:8000" > .env
echo "VITE_GOOGLE_CLIENT_ID=your-google-client-id" >> .env

# Run
npm run dev
```

**✅ Open http://localhost:5173**

---

## 🌐 PRODUCTION DEPLOYMENT (GCP Cloud Run)

### Option A: Single Service (Recommended)

```bash
# Build combined service (frontend + backend)
cd deployment

# Build Docker image
docker build -t gcr.io/$GCP_PROJECT_ID/legid:latest -f Dockerfile.combined ..

# Push to GCR
docker push gcr.io/$GCP_PROJECT_ID/legid:latest

# Deploy to Cloud Run
gcloud run deploy legid \
  --image gcr.io/$GCP_PROJECT_ID/legid:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated=false \
  --set-env-vars="GCP_PROJECT_ID=$GCP_PROJECT_ID,BIGQUERY_DATASET=legid_production" \
  --set-secrets="JWT_SECRET_KEY=legid-jwt-secret:latest,OPENAI_API_KEY=openai-api-key:latest"

# Grant access to specific user
gcloud run services add-iam-policy-binding legid \
  --region=us-central1 \
  --member="user:anshuman.kush@predictivetechlabs.com" \
  --role="roles/run.invoker"

# Get service URL
gcloud run services describe legid --region us-central1 --format="value(status.url)"
```

### Option B: Separate Frontend/Backend

```bash
# Deploy backend
gcloud run deploy legid-backend \
  --image gcr.io/$GCP_PROJECT_ID/legid-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated=false

# Deploy frontend
gcloud run deploy legid-frontend \
  --image gcr.io/$GCP_PROJECT_ID/legid-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated=false \
  --set-env-vars="VITE_API_URL=https://legid-backend-xxx.run.app"
```

### Set Up IAP (Identity-Aware Proxy)

```bash
# Enable IAP
gcloud iap web enable \
  --resource-type=compute \
  --oauth2-client-id=your-oauth-client-id \
  --oauth2-client-secret=your-oauth-secret

# Grant IAP access
gcloud iap web add-iam-policy-binding \
  --member="user:anshuman.kush@predictivetechlabs.com" \
  --role="roles/iap.httpsResourceAccessor"
```

---

## 🧪 SMOKE TEST CHECKLIST

### Backend Tests

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "display_name": "Test User",
    "role": "Client"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Create conversation (use token from login)
curl -X POST http://localhost:8000/api/conversations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Chat",
    "law_type": "Criminal Law",
    "jurisdiction": "Ontario, Canada"
  }'

# Send message
curl -X POST http://localhost:8000/api/messages/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "YOUR_CONV_ID",
    "message": "What are the penalties for speeding in Ontario?"
  }'
```

### Frontend Tests

**Manual Testing Checklist:**

1. **Authentication**
   - [ ] Register with email/password
   - [ ] Login with email/password
   - [ ] Login with Google OAuth
   - [ ] Logout clears session
   - [ ] Protected routes redirect to login

2. **Chat Functionality**
   - [ ] New Chat creates new conversation
   - [ ] Send message shows typing dots
   - [ ] Response appears with text animation
   - [ ] Messages persist on reload
   - [ ] Search finds conversations
   - [ ] Click old chat loads messages

3. **Profile & Settings**
   - [ ] Profile dropdown shows user info
   - [ ] Edit profile updates name/avatar
   - [ ] Theme toggle (dark/light) works
   - [ ] Font size changes apply
   - [ ] Response style affects replies
   - [ ] Language selection works
   - [ ] Auto-read toggle works

4. **Resources**
   - [ ] Sidebar tiles are clickable
   - [ ] Recent Updates loads data
   - [ ] Case Lookup searches work
   - [ ] Documents page loads
   - [ ] Images page shows uploads
   - [ ] Settings page saves

5. **Typing Animation**
   - [ ] Typing dots appear (3 dots blink)
   - [ ] Text reveals character-by-character
   - [ ] Animation completes smoothly

6. **Role-Based Features**
   - [ ] Client sees basic features
   - [ ] Lawyer sees verification flow
   - [ ] Lawyer can upload license
   - [ ] Lawyer verification status shows

---

## 🎨 THEMING & ANIMATIONS

### Dark Theme

```css
/* Applied automatically - see frontend/src/styles/theme.css */
--bg-primary: #1a1a1a;
--bg-secondary: #2a2a2a;
--text-primary: #e0e0e0;
--accent-blue: #4a9eff;
```

### Typing Dots Animation

```jsx
// Automatically shown while bot is "thinking"
<div className="typing-indicator">
  <span></span>
  <span></span>
  <span></span>
</div>
```

### Text Reveal Animation

```jsx
// Use hook in components
const { displayedText, isComplete } = useTypingAnimation(message.content, 30);
```

---

## 📊 MONITORING & LOGS

```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=legid" \
  --limit=50 \
  --format=json

# Monitor BigQuery usage
gcloud alpha bq datasets describe legid_production

# Check GCS bucket size
gsutil du -sh gs://legid-uploads-prod
```

---

## 🔒 SECURITY CHECKLIST

- [ ] JWT secret is strong and stored in Secret Manager
- [ ] OpenAI API key is in Secret Manager
- [ ] BigQuery dataset has IAM restrictions
- [ ] GCS buckets have proper IAM policies
- [ ] Cloud Run services require authentication
- [ ] CORS is restricted to production domain
- [ ] Passwords are hashed with bcrypt
- [ ] SQL injection protected (parameterized queries)
- [ ] XSS protection (React auto-escapes)
- [ ] CSRF tokens for state-changing requests
- [ ] Rate limiting enabled on auth endpoints
- [ ] Audit log tracks all actions
- [ ] Cookie consent banner implemented
- [ ] GDPR data export/delete available
- [ ] Lawyer verification requires admin approval

---

## 🐛 TROUBLESHOOTING

### "Conversation not found"
- Check conversation_id is correct
- Verify user owns the conversation
- Check BigQuery for conversation existence

### "Typing animation not working"
- Verify `useTypingAnimation` hook is imported
- Check CSS animations.css is loaded
- Inspect network tab for message delays

### "Google OAuth fails"
- Verify GOOGLE_CLIENT_ID matches OAuth consent screen
- Check redirect URI is whitelisted
- Ensure backend can verify id_token

### "BigQuery permission denied"
- Service account needs BigQuery Data Editor role
- Check GOOGLE_APPLICATION_CREDENTIALS path
- Verify dataset exists and project ID matches

### "Profile dropdown doesn't show"
- Check user is logged in (token exists)
- Verify /api/auth/me returns user data
- Inspect browser console for errors

---

## 📝 TODO: Future Enhancements

- [ ] WebSocket for real-time streaming responses
- [ ] Voice chat (STT + TTS integration)
- [ ] Document generation (contracts, letters, etc.)
- [ ] Case lookup API integration
- [ ] Multi-language UI (not just responses)
- [ ] Mobile app (React Native)
- [ ] Admin dashboard for lawyer verification
- [ ] Analytics dashboard
- [ ] Export chat history as PDF
- [ ] Share conversation via link
- [ ] Collaborative chats (multiple users)

---

## 🤝 SUPPORT

For issues:
1. Check logs: `gcloud logging read`
2. Verify environment variables
3. Test with smoke tests above
4. Check BigQuery tables exist
5. Verify service account permissions

For questions: anshuman.kush@predictivetechlabs.com

---

**✅ LEGID is now production-ready with:**
- ChatGPT-style dark UI
- Full authentication (Google + Email/Password)
- Conversation persistence (BigQuery)
- Typing animations (dots + text reveal)
- Profile management
- Personalization
- Role-based access
- Lawyer verification
- Cloud Run deployment
- Private IAM access
