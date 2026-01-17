# 🚀 Quick Start: Google OAuth Authentication

## Your Credentials

✅ **Client ID:** `1086283983680-3ug6e2c1oqaq9vf30e5k61f4githchr3.apps.googleusercontent.com`  
✅ **Client Secret:** `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`  
✅ **Project ID:** `auth-login-page-481522`

---

## 3-Minute Setup

### Step 1: Run Setup Script

```bash
SETUP_GOOGLE_OAUTH.bat
```

This will:
- Install required dependencies
- Create `.env` file with your credentials
- Verify the setup

### Step 2: Configure Google Cloud Console

1. Go to [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials?project=auth-login-page-481522)

2. Click on your OAuth 2.0 Client ID

3. Add these **Authorized redirect URIs**:
   ```
   http://localhost:8000/auth/google/callback
   ```

4. Add these **Authorized JavaScript origins** (optional but recommended):
   ```
   http://localhost:3000
   http://localhost:8000
   ```

5. Click **Save**

### Step 3: Start Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use your existing script:
```bash
START_BACKEND.bat
```

### Step 4: Start Frontend

**Open a new terminal:**

```bash
cd frontend
python -m http.server 3000
```

### Step 5: Test It!

Open your browser to:
```
http://localhost:3000/legid-with-google-auth.html
```

Click **"Sign in with Google"** and you're done! 🎉

---

## 🧪 Test the Backend

Run the test script to verify everything is working:

```bash
cd backend
python test_google_oauth.py
```

Expected output:
```
✓ All tests passed! OAuth integration is ready.
```

---

## 📝 Quick Reference

### Backend Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/google/login` | GET | Start OAuth flow |
| `/auth/google/callback` | GET | OAuth callback |
| `/auth/verify` | GET | Verify JWT token |
| `/auth/logout` | POST | Logout user |
| `/auth/config` | GET | Get OAuth config |

### Frontend Files

| File | Description |
|------|-------------|
| `legid-with-google-auth.html` | New version with OAuth |
| `legid-tailwind-demo.html` | Original version (no auth) |

---

## ⚡ Troubleshooting

### "redirect_uri_mismatch" Error

**Solution:** Add `http://localhost:8000/auth/google/callback` to Authorized redirect URIs in Google Cloud Console.

### "GOOGLE_CLIENT_ID must be set" Error

**Solution:** Ensure `backend/.env` file exists and contains your credentials.

### CORS Error

**Solution:** Backend is already configured for CORS. Ensure it's running on port 8000.

### Token Not Saving

**Solution:** Check browser console. Ensure frontend is served via HTTP server (not file://).

---

## 🎯 What's Next?

Your OAuth is ready! Consider:

1. **Add Database Integration** - Store user profiles
2. **Implement Chat History** - Save chats per user
3. **Add User Preferences** - Customize experience
4. **Deploy to Production** - Use HTTPS and update redirect URIs

See `GOOGLE_OAUTH_IMPLEMENTATION.md` for complete documentation.

---

## 📞 Need Help?

Check the logs:
- Backend: `backend/backend_detailed.log`
- Browser: Open Developer Tools (F12) → Console

---

**Happy coding! 🚀**
