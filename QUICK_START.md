# LEGID OAuth + Chat System - Quick Start Guide

Get up and running with LEGID's OAuth authentication and chat system in under 10 minutes.

---

## ⚡ Quick Setup (Local Development)

### 1. Get OAuth Credentials (5 minutes)

You need OAuth credentials from Google and Microsoft to enable social login.

#### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use existing)
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth client ID**
5. Choose **Web application**
6. Add redirect URI: `http://localhost:8000/api/auth/google/callback`
7. **Copy Client ID and Client Secret**

#### Microsoft OAuth

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Add redirect URI: `http://localhost:8000/api/auth/microsoft/callback`
5. Go to **Certificates & secrets** → **New client secret**
6. **Copy Application ID and Client Secret value**

> **Note**: For detailed OAuth setup, see `SETUP_OAUTH.md`

---

### 2. Configure Environment (2 minutes)

#### Backend Configuration

Create `backend/.env`:

```bash
# OpenAI (required for chat)
OPENAI_API_KEY=sk-your-openai-api-key-here

# JWT Security (generate random string)
JWT_SECRET_KEY=your-random-32-character-secret-key-here

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:4200/auth/callback/google

# Microsoft OAuth
MS_CLIENT_ID=your-microsoft-client-id
MS_CLIENT_SECRET=your-microsoft-client-secret
MS_TENANT=common
MS_REDIRECT_URI=http://localhost:4200/auth/callback/microsoft

# App Config
FRONTEND_BASE_URL=http://localhost:4200
CORS_ORIGINS=http://localhost:4200,http://localhost:5173
DATABASE_URL=sqlite:///./data/legal_bot.db
```

**Generate JWT Secret**:
```bash
# Linux/Mac
openssl rand -base64 32

# Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

#### Frontend Configuration (Optional)

Create `frontend/.env`:

```bash
VITE_API_URL=http://localhost:8000
```

---

### 3. Install Dependencies (2 minutes)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend (in new terminal)
cd frontend
npm install
```

---

### 4. Initialize Database (1 minute)

```bash
cd backend
python init_database.py init
```

Expected output:
```
✅ Database tables created successfully!
Created 14 tables:
  - users
  - oauth_identities
  - conversations
  - messages
  ...
```

---

### 5. Start Services (1 minute)

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

---

### 6. Test Authentication (2 minutes)

1. **Open browser**: http://localhost:4200/login

2. **Test Email/Password Signup**:
   - Click "Sign up" link
   - Enter name, email, password
   - Click "Create Account"
   - Should redirect to chat

3. **Test Google OAuth**:
   - Click "Continue with Google"
   - Login with Google account
   - Should redirect back to chat

4. **Test Microsoft OAuth**:
   - Click "Continue with Microsoft"
   - Login with Microsoft account
   - Should redirect back to chat

---

## ✅ Verification Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:4200
- [ ] Can sign up with email/password
- [ ] Can login with email/password
- [ ] Can login with Google
- [ ] Can login with Microsoft
- [ ] User data saved to database
- [ ] Redirected to chat after login

---

## 🐛 Troubleshooting

### "Module not found" errors

**Fix**:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### "redirect_uri_mismatch" error

**Fix**: Make sure your OAuth redirect URIs in Google/Microsoft consoles exactly match:
- Google: `http://localhost:8000/api/auth/google/callback`
- Microsoft: `http://localhost:8000/api/auth/microsoft/callback`

### CORS errors

**Fix**: Ensure `CORS_ORIGINS` in backend `.env` includes `http://localhost:4200`

### Database errors

**Fix**:
```bash
cd backend
python init_database.py reset
```

### Port already in use

**Fix**:
```bash
# Kill process on port 8000 (backend)
# Linux/Mac:
lsof -ti:8000 | xargs kill

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 4200 (frontend)
# Similar commands with port 4200
```

---

## 📚 Next Steps

### Wire Up Frontend Components

The backend is fully functional. To complete the frontend:

1. **Profile Chip** - Wire to `/api/me` endpoint
   ```typescript
   // In your profile component
   this.authService.getCurrentUserFromAPI().subscribe(user => {
     // Display user.display_name, user.email, user.avatar_url
   });
   ```

2. **Chat Sidebar** - Wire to `/api/conversations` endpoint
   ```typescript
   // In your chat component
   this.http.get('/api/conversations').subscribe(conversations => {
     // Display conversation list
   });
   ```

3. **Send Messages** - Wire to `/api/conversations/{id}/messages`
   ```typescript
   this.http.post(`/api/conversations/${id}/messages`, {
     content: userMessage
   }).subscribe(response => {
     // Display assistant response
   });
   ```

4. **Preferences** - Wire to `/api/preferences`
   ```typescript
   // Load preferences
   this.http.get('/api/preferences').subscribe(prefs => {
     // Apply theme, fontSize, etc.
   });

   // Save preferences
   this.http.put('/api/preferences', newPrefs).subscribe();
   ```

### Deploy to Production

See `DEPLOYMENT_GUIDE.md` for complete deployment instructions:

```bash
# Quick deploy to Cloud Run
cd backend
gcloud run deploy legid-backend --source .

cd frontend
gcloud run deploy legid-frontend --source .
```

---

## 📖 Documentation

- **SETUP_OAUTH.md** - Detailed OAuth setup guide
- **DEPLOYMENT_GUIDE.md** - Complete deployment guide
- **README_AUTH_IMPLEMENTATION.md** - Full implementation details

---

## 🆘 Need Help?

### Check Logs

**Backend:**
```bash
# Backend logs show detailed error messages
# Check terminal where uvicorn is running
```

**Frontend:**
```bash
# Check browser console (F12)
# Check network tab for API errors
```

### Common Issues

1. **OAuth not working**: Check redirect URIs in OAuth consoles
2. **CORS errors**: Update `CORS_ORIGINS` in backend `.env`
3. **Database errors**: Run `python init_database.py reset`
4. **Token errors**: Check `JWT_SECRET_KEY` is set in `.env`

---

## 🎉 Success!

If you can:
- ✅ Sign up with email/password
- ✅ Login with Google
- ✅ Login with Microsoft
- ✅ See your user data in the database

**Congratulations! Your OAuth authentication system is working.**

Now you can:
1. Wire up the remaining frontend components
2. Add unit tests
3. Deploy to production
4. Build your chat features

---

## 📝 Quick Reference

### Backend Endpoints

```
POST   /api/auth/signup          - Email/password signup
POST   /api/auth/login           - Email/password login
POST   /api/auth/refresh         - Refresh access token
POST   /api/auth/logout          - Logout
GET    /api/auth/me              - Get current user

GET    /api/auth/google/login    - Start Google OAuth
GET    /api/auth/google/callback - Google OAuth callback
GET    /api/auth/microsoft/login - Start Microsoft OAuth
GET    /api/auth/microsoft/callback - Microsoft OAuth callback

POST   /api/conversations        - Create conversation
GET    /api/conversations        - List conversations
GET    /api/conversations/{id}   - Get conversation
DELETE /api/conversations/{id}   - Delete conversation

POST   /api/conversations/{id}/messages - Send message
GET    /api/conversations/{id}/messages - Get messages

GET    /api/preferences          - Get preferences
PUT    /api/preferences          - Update preferences
```

### Database Commands

```bash
# Initialize database
python init_database.py init

# Reset database (delete all data)
python init_database.py reset

# Check database status
python init_database.py check

# Drop all tables
python init_database.py drop
```

### Development Commands

```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Start frontend
cd frontend
npm run dev

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
```

---

**Ready to code? Start building your chat features! 🚀**
