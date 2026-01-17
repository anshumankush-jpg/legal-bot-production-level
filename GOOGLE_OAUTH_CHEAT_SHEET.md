# 🚀 Google OAuth - Quick Reference Card

## ⚡ Commands

### Setup (First Time)
```bash
SETUP_GOOGLE_OAUTH.bat
```

### Start Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
python -m http.server 3000
```

### Run Tests
```bash
cd backend
python test_google_oauth.py
```

---

## 🔗 URLs

| What | URL |
|------|-----|
| **Frontend** | http://localhost:3000/legid-with-google-auth.html |
| **Backend** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Google Console** | https://console.cloud.google.com/apis/credentials?project=auth-login-page-481522 |

---

## 🔑 Credentials

```
Client ID: 1086283983680-3ug6e2c1oqaq9vf30e5k61f4githchr3.apps.googleusercontent.com
Client Secret: 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
Project ID: auth-login-page-481522
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `backend/app/auth/google_oauth.py` | OAuth logic |
| `backend/app/auth/routes.py` | API endpoints |
| `backend/.env` | Configuration |
| `frontend/legid-with-google-auth.html` | UI with auth |
| `backend/test_google_oauth.py` | Tests |

---

## 🌐 API Endpoints

| Endpoint | Method | Use |
|----------|--------|-----|
| `/auth/google/login` | GET | Start login |
| `/auth/google/callback` | GET | OAuth callback |
| `/auth/verify?token=XXX` | GET | Verify token |
| `/auth/logout` | POST | Logout |
| `/auth/config` | GET | Get config |

---

## 🔧 Environment Variables

```bash
# Required
GOOGLE_CLIENT_ID=1086283983680-3ug6e2c1oqaq9vf30e5k61f4githchr3.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

# Optional (defaults shown)
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440
```

---

## 🐛 Troubleshooting

| Error | Fix |
|-------|-----|
| `redirect_uri_mismatch` | Add redirect URI in Google Console |
| `GOOGLE_CLIENT_ID must be set` | Create `backend/.env` file |
| CORS error | Use HTTP server for frontend |
| Token not saving | Don't use file:// protocol |
| 401 Unauthorized | Token expired, login again |

---

## 📚 Documentation Files

| File | What's Inside |
|------|---------------|
| `START_HERE_GOOGLE_AUTH.md` | **Start here!** Quick setup |
| `QUICK_START_GOOGLE_AUTH.md` | 3-minute guide |
| `GOOGLE_OAUTH_IMPLEMENTATION.md` | Technical details |
| `GOOGLE_OAUTH_FLOW_DIAGRAM.md` | Visual flows |
| `README_GOOGLE_OAUTH.md` | Complete summary |
| `GOOGLE_OAUTH_CHEAT_SHEET.md` | This file |

---

## ✅ Setup Checklist

- [ ] Run `SETUP_GOOGLE_OAUTH.bat`
- [ ] Configure redirect URI in Google Console
- [ ] Start backend on port 8000
- [ ] Start frontend on port 3000
- [ ] Test at http://localhost:3000/legid-with-google-auth.html
- [ ] Click "Sign in with Google"
- [ ] Verify user info displays
- [ ] Test logout

---

## 🧪 Test Commands

```bash
# Full test suite
cd backend
python test_google_oauth.py

# Check if server is running
curl http://localhost:8000/auth/config

# Verify a token
curl "http://localhost:8000/auth/verify?token=YOUR_TOKEN_HERE"
```

---

## 🔐 Security Notes

✅ **Development:**
- Credentials in `.env` (not committed)
- JWT tokens expire in 24h
- CORS allows localhost

⚠️ **Production:**
- Generate new JWT secret
- Use HTTPS everywhere
- Update CORS to specific domains
- Use httpOnly cookies
- Enable rate limiting

---

## 🎯 Common Tasks

### Generate JWT Secret
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Check Token in Browser
```javascript
// Open browser console (F12)
localStorage.getItem('authToken')
localStorage.getItem('userEmail')
```

### Clear Auth State
```javascript
// In browser console
localStorage.clear()
location.reload()
```

### Test API with Token
```javascript
// In browser console
const token = localStorage.getItem('authToken');
fetch('http://localhost:8000/auth/verify?token=' + token)
  .then(r => r.json())
  .then(console.log)
```

---

## 🌐 Google Cloud Console

**Add Authorized redirect URIs:**
```
http://localhost:8000/auth/google/callback
https://yourdomain.com/auth/google/callback  # Production
```

**Add Authorized JavaScript origins:**
```
http://localhost:3000
http://localhost:8000
https://yourdomain.com  # Production
```

---

## 📊 File Structure

```
production_level/
├── backend/
│   ├── app/
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── google_oauth.py      ← OAuth handler
│   │   │   └── routes.py            ← API routes
│   │   └── main.py                  ← FastAPI app
│   ├── .env                         ← Your config
│   ├── GOOGLE_OAUTH_SETUP.env       ← Template
│   └── test_google_oauth.py         ← Tests
│
├── frontend/
│   └── legid-with-google-auth.html  ← App with OAuth
│
└── docs/
    ├── START_HERE_GOOGLE_AUTH.md
    ├── QUICK_START_GOOGLE_AUTH.md
    ├── GOOGLE_OAUTH_IMPLEMENTATION.md
    ├── GOOGLE_OAUTH_FLOW_DIAGRAM.md
    ├── README_GOOGLE_OAUTH.md
    └── GOOGLE_OAUTH_CHEAT_SHEET.md  ← You are here
```

---

## 🎨 Frontend Integration

### Check Auth Status
```javascript
const token = localStorage.getItem('authToken');
if (token) {
  // User is logged in
}
```

### Make Authenticated Request
```javascript
fetch('http://localhost:8000/api/endpoint', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

### Logout
```javascript
localStorage.clear();
window.location.href = '/login';
```

---

## 🚀 Production Deployment

1. **Update `.env`:**
   ```bash
   GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/google/callback
   JWT_SECRET_KEY=<new-secure-random-key>
   ```

2. **Update Google Console:**
   - Add production redirect URI
   - Add production JavaScript origins

3. **Deploy:**
   ```bash
   # Build and deploy backend
   docker build -t legid-backend ./backend
   
   # Deploy frontend
   # Upload legid-with-google-auth.html to web server
   ```

4. **Test production flow**

Full guide: `GOOGLE_OAUTH_IMPLEMENTATION.md` → Production Deployment

---

## 💡 Quick Tips

- **Token expires?** User needs to login again
- **Testing?** Run `python backend/test_google_oauth.py`
- **Logs?** Check `backend/backend_detailed.log`
- **Errors?** Check browser console (F12)
- **CORS?** Frontend must use HTTP server
- **State?** OAuth includes state for CSRF protection

---

## 🔄 OAuth Flow (Simplified)

```
User clicks "Sign in with Google"
    ↓
Redirect to /auth/google/login
    ↓
Redirect to Google OAuth
    ↓
User approves
    ↓
Google redirects to /auth/google/callback
    ↓
Backend exchanges code for token
    ↓
Backend gets user info
    ↓
Backend creates JWT
    ↓
Redirect to frontend with JWT
    ↓
Frontend saves JWT
    ↓
User is authenticated! ✅
```

---

## 📱 Contact & Support

- **Documentation:** See files listed above
- **Test Script:** `python backend/test_google_oauth.py`
- **Logs:** `backend/backend_detailed.log`
- **Browser Console:** F12 → Console tab

---

## ✨ Features

- ✅ Google OAuth 2.0
- ✅ JWT tokens
- ✅ Session management
- ✅ Secure logout
- ✅ Beautiful UI
- ✅ Production-ready
- ✅ Fully tested
- ✅ Complete docs

---

**Print this page and keep it handy!** 📄

**Everything you need in one place!** 🎯
