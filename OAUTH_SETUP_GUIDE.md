# Google OAuth Setup Guide for LEGID

## ⚠️ SECURITY WARNING - READ THIS FIRST

**CRITICAL**: The OAuth credentials you shared should be rotated immediately!

### Why You Need to Rotate
You shared these credentials in plain text in our chat:
- Client ID: `1086283983680-3ug6e2c1oqaq9vf30e5k61f4githchr3.apps.googleusercontent.com`
- Client Secret: `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`

Anyone who sees these can impersonate your application. **Regenerate them now**.

### How to Rotate Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Find your OAuth 2.0 Client ID: `1086283983680-3ug6e2c1oqaq9vf30e5k61f4githchr3.apps.googleusercontent.com`
4. Click the **"Reset Secret"** or **"Regenerate Secret"** button
5. Update your `backend/.env` file with the new secret

---

## ✅ Good News - OAuth is Already Implemented!

Your backend already has a complete Google OAuth implementation:
- ✅ OAuth service (`backend/app/services/oauth_service.py`)
- ✅ Authentication routes (`/api/auth/google/login`, `/api/auth/google/callback`)
- ✅ Database models for OAuth identities
- ✅ User creation and linking logic

---

## Setup Instructions

### 1. Configure Backend Environment Variables

Run the provided setup script:

```bash
setup_oauth.bat
```

**OR** manually edit `backend/.env` and add:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=1086283983680-3ug6e2c1oqaq9vf30e5k61f4githchr3.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback/google
```

**Then immediately rotate the secret** as described above and update the file.

### 2. Verify .gitignore

Check that your `.gitignore` includes:

```
.env
*.env
.env.local
.env.production
client_secret_*.json
```

### 3. Google Cloud Console - Authorized Redirect URIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Click on your OAuth 2.0 Client ID
4. Under **Authorized redirect URIs**, ensure these are added:
   - `http://localhost:5173/auth/callback/google` (local development)
   - `http://localhost:8000/api/auth/google/callback` (backend API)
   - Add production URLs when deploying

### 4. Test the Backend OAuth Flow

Start your backend:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Test endpoints:
- **Login URL**: `http://localhost:8000/api/auth/google/login`
- **Callback URL**: `http://localhost:8000/api/auth/google/callback`

---

## How the OAuth Flow Works

### Backend Flow (Already Implemented)

1. **User clicks "Sign in with Google"** → Frontend redirects to `/api/auth/google/login`
2. **Backend generates auth URL** with state parameter for security
3. **User authenticates with Google** and approves permissions
4. **Google redirects back** to `/api/auth/google/callback?code=...`
5. **Backend exchanges code for tokens** using your client secret
6. **Backend fetches user info** from Google
7. **Backend creates or links user account** in the database
8. **Backend issues JWT tokens** for session management
9. **Frontend receives tokens** and stores them

### Database Schema (Already Implemented)

Your system stores:
- **Users** table: email, name, profile picture
- **OAuth Identities** table: links Google ID to user account
- **Refresh Tokens** table: for session management
- **Audit Logs** table: tracks OAuth login attempts

---

## Frontend Integration Needed

Your current frontend (`frontend/legid-tailwind-demo.html`) is a static demo. You need to:

### Option 1: Simple HTML/JavaScript (Quick Test)

Add a Google Sign-In button:

```html
<button onclick="loginWithGoogle()">
  <img src="google-icon.png" /> Sign in with Google
</button>

<script>
function loginWithGoogle() {
  window.location.href = 'http://localhost:8000/api/auth/google/login';
}
</script>
```

### Option 2: Full React/Vue Integration (Production)

Use a proper frontend framework with:
- OAuth popup window
- JWT token storage
- Protected routes
- User session management

---

## Backend API Endpoints

Your backend exposes these OAuth endpoints:

### GET `/api/auth/google/login`
Returns Google authorization URL
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
  "state": "random-state-token"
}
```

### GET `/api/auth/google/callback?code=...&state=...`
Handles OAuth callback, returns JWT tokens
```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "picture": "https://..."
  }
}
```

---

## Security Best Practices

✅ **Already Implemented in Your Backend:**
- State parameter validation (prevents CSRF attacks)
- JWT token authentication
- Secure password hashing (for email/password users)
- Database audit logging
- Token refresh mechanism

⚠️ **You Still Need To:**
1. **Rotate the client secret** immediately
2. **Use HTTPS in production** (OAuth requires SSL)
3. **Set up proper CORS** for your frontend domain
4. **Add rate limiting** to prevent abuse
5. **Monitor audit logs** for suspicious activity

---

## Testing the OAuth Flow

### 1. Start the Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Test in Browser

Visit: `http://localhost:8000/api/auth/google/login`

You should be redirected to Google's login page.

### 3. After Login

Google will redirect back with tokens. Check the URL for:
- `access_token`: Use this for API calls
- `refresh_token`: Use this to get new access tokens

### 4. Make Authenticated API Calls

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/protected-endpoint
```

---

## Next Steps

1. ✅ **Run `setup_oauth.bat`** to configure environment variables
2. ⚠️ **Rotate your client secret** in Google Cloud Console
3. ✅ **Start the backend server** and test OAuth login
4. 📝 **Update the frontend** to use OAuth (I can help with this)
5. 🔒 **Set up HTTPS** before going to production

---

## Need Help?

I can help you:
1. ✅ Create a React/Vue frontend with Google Sign-In
2. ✅ Add Microsoft OAuth as well
3. ✅ Set up email/password authentication fallback
4. ✅ Implement user profile management
5. ✅ Add role-based access control
6. ✅ Deploy to production with HTTPS

---

## File Reference

- **OAuth Service**: `backend/app/services/oauth_service.py`
- **Auth Routes**: `backend/app/api/routes/auth_oauth.py`
- **Configuration**: `backend/app/core/config.py`
- **Database Models**: `backend/app/models/db_models.py`
- **Setup Script**: `setup_oauth.bat`
