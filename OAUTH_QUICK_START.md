# 🚀 Google OAuth Quick Start Guide

## ⚠️ CRITICAL FIRST STEP

**You shared your OAuth credentials in plain text.** For security, you MUST:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Find client ID: `1086283983680-3ug6e2c1oqaq9vf30e5k61f4githchr3.apps.googleusercontent.com`
3. Click **"Reset Secret"** or **"Regenerate Secret"**
4. Update your `.env` file with the new secret

---

## 🎯 Quick Setup (3 Steps)

### Step 1: Run Setup Script

```bash
setup_oauth.bat
```

This will:
- Create `backend/.env` if it doesn't exist
- Add your Google OAuth credentials
- Display security warnings

### Step 2: Verify Google Cloud Console

Ensure these redirect URIs are configured:

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Click on your OAuth 2.0 Client ID
3. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8000/api/auth/google/callback
   http://localhost:5173/auth/callback/google
   ```

### Step 3: Test OAuth Login

**Start Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**Open Test Page:**
```
http://localhost:8000/frontend/oauth-login-test.html
```

or if using a separate frontend server:
```
Open: frontend/oauth-login-test.html
```

Click **"Sign in with Google"** and you should see the Google login page!

---

## 📁 Files Created/Modified

### New Files:
1. **`OAUTH_SETUP_GUIDE.md`** - Complete documentation
2. **`setup_oauth.bat`** - Automated setup script
3. **`frontend/oauth-login-test.html`** - Test login page
4. **`OAUTH_QUICK_START.md`** - This file

### Modified Files:
- `backend/.env` - Will be updated by setup script

---

## ✅ What's Already Implemented

Your backend has a complete OAuth system:

✅ **Backend OAuth Service** (`backend/app/services/oauth_service.py`)
- Google OAuth flow
- Microsoft OAuth flow
- User info fetching
- Token exchange

✅ **API Endpoints** (`backend/app/api/routes/auth_oauth.py`)
- `GET /api/auth/google/login` - Initiates Google OAuth
- `GET /api/auth/google/callback` - Handles callback
- `GET /api/auth/microsoft/login` - Initiates Microsoft OAuth
- `GET /api/auth/microsoft/callback` - Handles callback

✅ **Database Models** (`backend/app/models/db_models.py`)
- User table
- OAuth identity linking
- Token refresh management
- Audit logging

✅ **Security Features**
- State parameter validation (CSRF protection)
- JWT token authentication
- Secure password hashing
- Database audit logs

---

## 🧪 Testing the OAuth Flow

### Option 1: Browser Test (Easiest)

1. Start backend: `cd backend && python -m uvicorn app.main:app --reload`
2. Open: `http://localhost:8000/frontend/oauth-login-test.html`
3. Click "Sign in with Google"
4. Authenticate with Google
5. You'll be redirected back with your user info!

### Option 2: API Test (Manual)

**Step 1: Get OAuth URL**
```bash
curl http://localhost:8000/api/auth/google/login
```

Response:
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "random-state-token"
}
```

**Step 2: Visit the URL**
- Copy the `auth_url` from the response
- Paste it in your browser
- Log in with Google

**Step 3: Check Callback**
- After login, Google redirects to: `/api/auth/google/callback?code=...`
- Your backend exchanges the code for tokens
- You receive JWT tokens for API access

---

## 🔐 Environment Variables

After running `setup_oauth.bat`, your `backend/.env` should contain:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=1086283983680-3ug6e2c1oqaq9vf30e5k61f4githchr3.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback/google

# Microsoft OAuth (Optional)
# MS_CLIENT_ID=your-microsoft-client-id
# MS_CLIENT_SECRET=your-microsoft-client-secret
# MS_REDIRECT_URI=http://localhost:5173/auth/callback/microsoft
```

**Remember to rotate the secret after initial setup!**

---

## 🎨 Frontend Integration

### Current Status
- ✅ Static test page created (`oauth-login-test.html`)
- ✅ Google Sign-In button
- ✅ Microsoft Sign-In button (optional)
- ✅ Token storage in localStorage
- ✅ User info display

### For Production
You'll want to integrate OAuth into your main app (`legid-tailwind-demo.html`):

```javascript
// Add this to your main app
function loginWithGoogle() {
  fetch('http://localhost:8000/api/auth/google/login')
    .then(res => res.json())
    .then(data => {
      localStorage.setItem('oauth_state', data.state);
      window.location.href = data.auth_url;
    });
}

// Handle callback on page load
const urlParams = new URLSearchParams(window.location.search);
const accessToken = urlParams.get('access_token');
if (accessToken) {
  localStorage.setItem('access_token', accessToken);
  // User is now logged in!
}
```

---

## 🛡️ Security Checklist

Before going to production:

- [ ] Rotate OAuth credentials from Google Cloud Console
- [ ] Use HTTPS (OAuth requires SSL in production)
- [ ] Update redirect URIs for production domain
- [ ] Set up proper CORS for your frontend
- [ ] Enable rate limiting on auth endpoints
- [ ] Monitor audit logs for suspicious activity
- [ ] Use secure cookies for token storage (instead of localStorage)
- [ ] Implement token refresh logic
- [ ] Add CSRF protection
- [ ] Set up security headers (HSTS, CSP, etc.)

---

## 🔧 Troubleshooting

### "OAuth not configured" error
- Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are in `backend/.env`
- Restart the backend server after modifying `.env`

### "Redirect URI mismatch" error
- Verify redirect URIs in Google Cloud Console match your backend settings
- Default backend redirect: `http://localhost:8000/api/auth/google/callback`

### Backend not starting
- Ensure all dependencies are installed: `pip install -r backend/requirements.txt`
- Check for port conflicts (default: 8000)

### Google login page doesn't appear
- Check browser console for CORS errors
- Verify backend is running: `http://localhost:8000/health`
- Check that OAuth URL is correctly formatted

---

## 📚 Additional Resources

- **Complete Guide**: See `OAUTH_SETUP_GUIDE.md` for full documentation
- **Backend Code**: `backend/app/services/oauth_service.py`
- **API Routes**: `backend/app/api/routes/auth_oauth.py`
- **Test Page**: `frontend/oauth-login-test.html`

---

## 🚀 Next Steps

1. ✅ Run `setup_oauth.bat`
2. ⚠️ Rotate OAuth secret
3. ✅ Test login with `oauth-login-test.html`
4. 📝 Integrate into main app
5. 🔒 Set up production HTTPS

---

## ❓ Need Help?

If you encounter issues:

1. Check `backend/backend_detailed.log` for errors
2. Review the `OAUTH_SETUP_GUIDE.md` for detailed explanations
3. Verify Google Cloud Console settings
4. Ensure all environment variables are set correctly

---

**Your OAuth credentials:**
- Client ID: `1086283983680-3ug6e2c1oqaq9vf30e5k61f4githchr3.apps.googleusercontent.com`
- Secret: `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` ⚠️ **ROTATE THIS**

**Ready to test?** Run `setup_oauth.bat` and open `frontend/oauth-login-test.html`!
