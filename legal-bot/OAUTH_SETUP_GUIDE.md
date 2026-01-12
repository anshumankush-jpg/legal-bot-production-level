# OAuth Setup Guide for LEGID

This guide will walk you through setting up Google and Microsoft OAuth authentication for the LEGID application.

## Table of Contents

1. [Google OAuth Setup](#google-oauth-setup)
2. [Microsoft OAuth Setup](#microsoft-oauth-setup)
3. [Gmail OAuth Setup (for Employee Email)](#gmail-oauth-setup-for-employee-email)
4. [Environment Variables](#environment-variables)
5. [Testing OAuth Flow](#testing-oauth-flow)

---

## Google OAuth Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `LEGID-Auth` (or your preferred name)
4. Click "Create"

### Step 2: Enable Google+ API

1. In the left sidebar, go to **APIs & Services** → **Library**
2. Search for "Google+ API"
3. Click on it and click "Enable"

### Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** (unless you have a Google Workspace)
3. Click "Create"
4. Fill in the required fields:
   - **App name**: LEGID
   - **User support email**: your-email@example.com
   - **Developer contact**: your-email@example.com
5. Click "Save and Continue"
6. **Scopes**: Click "Add or Remove Scopes"
   - Add: `openid`
   - Add: `email`
   - Add: `profile`
7. Click "Save and Continue"
8. **Test users** (for development):
   - Add your email addresses that will test the app
9. Click "Save and Continue"

### Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click "Create Credentials" → "OAuth client ID"
3. Select **Application type**: Web application
4. **Name**: LEGID Web Client
5. **Authorized JavaScript origins**:
   ```
   http://localhost:5173
   http://localhost:3000
   http://localhost:4200
   ```
6. **Authorized redirect URIs**:
   ```
   http://localhost:5173/auth/callback/google
   http://localhost:3000/auth/callback/google
   http://localhost:4200/auth/callback/google
   ```
7. Click "Create"
8. **IMPORTANT**: Copy the **Client ID** and **Client Secret**

### Step 5: Add Credentials to Backend .env

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback/google
```

---

## Microsoft OAuth Setup

### Step 1: Register Application in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com/)
2. Search for "Azure Active Directory" or "Microsoft Entra ID"
3. Click **App registrations** → **New registration**

### Step 2: Configure Application

1. **Name**: LEGID
2. **Supported account types**: 
   - Select "Accounts in any organizational directory (Any Azure AD directory - Multitenant) and personal Microsoft accounts"
3. **Redirect URI**:
   - Platform: **Web**
   - URI: `http://localhost:5173/auth/callback/microsoft`
4. Click "Register"

### Step 3: Add Additional Redirect URIs

1. Go to **Authentication** in the left sidebar
2. Under **Platform configurations** → **Web**, click "Add URI"
3. Add:
   ```
   http://localhost:3000/auth/callback/microsoft
   http://localhost:4200/auth/callback/microsoft
   ```
4. Click "Save"

### Step 4: Create Client Secret

1. Go to **Certificates & secrets** in the left sidebar
2. Click **New client secret**
3. **Description**: LEGID Backend
4. **Expires**: 24 months (or your preference)
5. Click "Add"
6. **IMPORTANT**: Copy the **Value** (this is your client secret) immediately - it won't be shown again

### Step 5: Configure API Permissions

1. Go to **API permissions** in the left sidebar
2. Click "Add a permission"
3. Select **Microsoft Graph**
4. Select **Delegated permissions**
5. Add:
   - `openid`
   - `email`
   - `profile`
   - `User.Read`
6. Click "Add permissions"
7. (Optional) Click "Grant admin consent" if you're an admin

### Step 6: Get Application (Client) ID

1. Go to **Overview** in the left sidebar
2. Copy the **Application (client) ID**

### Step 7: Add Credentials to Backend .env

```bash
MS_CLIENT_ID=your-application-client-id
MS_CLIENT_SECRET=your-client-secret-value
MS_TENANT=common
MS_REDIRECT_URI=http://localhost:5173/auth/callback/microsoft
```

---

## Gmail OAuth Setup (for Employee Email)

This uses the same Google Cloud project but with additional scopes for sending emails.

### Step 1: Enable Gmail API

1. In your Google Cloud project, go to **APIs & Services** → **Library**
2. Search for "Gmail API"
3. Click on it and click "Enable"

### Step 2: Update OAuth Consent Screen Scopes

1. Go to **APIs & Services** → **OAuth consent screen**
2. Click "Edit App"
3. Go to **Scopes** step
4. Click "Add or Remove Scopes"
5. Add:
   - `https://www.googleapis.com/auth/gmail.send` (Send email on your behalf)
   - `https://www.googleapis.com/auth/userinfo.email` (See your email address)
6. Click "Update" and "Save and Continue"

### Step 3: Create Separate OAuth Client (Optional but Recommended)

1. Go to **APIs & Services** → **Credentials**
2. Click "Create Credentials" → "OAuth client ID"
3. Select **Application type**: Web application
4. **Name**: LEGID Gmail Integration
5. **Authorized redirect URIs**:
   ```
   http://localhost:5173/employee/email/callback
   ```
6. Click "Create"
7. Copy the **Client ID** and **Client Secret**

### Step 4: Add Credentials to Backend .env

```bash
GMAIL_CLIENT_ID=your-gmail-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-gmail-client-secret
GMAIL_REDIRECT_URI=http://localhost:5173/employee/email/callback
```

**Note**: You can use the same credentials as Google OAuth if you prefer, but separate credentials are recommended for security.

---

## Environment Variables

Complete `.env` file for backend:

```bash
# Database
DATABASE_URL=sqlite:///./data/legal_bot.db

# JWT
JWT_SECRET_KEY=your-long-random-secret-key-change-in-production
JWT_ACCESS_TTL_MIN=30
JWT_REFRESH_TTL_DAYS=30

# Frontend
FRONTEND_BASE_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:3000,http://localhost:4200,http://localhost:5173

# OpenAI (for AI features)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_CHAT_MODEL=gpt-4o-mini
LLM_PROVIDER=openai

# Google OAuth (User Authentication)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback/google

# Microsoft OAuth (User Authentication)
MS_CLIENT_ID=your-microsoft-client-id
MS_CLIENT_SECRET=your-microsoft-client-secret
MS_TENANT=common
MS_REDIRECT_URI=http://localhost:5173/auth/callback/microsoft

# Gmail OAuth (Employee Email Feature)
GMAIL_CLIENT_ID=your-gmail-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-gmail-client-secret
GMAIL_REDIRECT_URI=http://localhost:5173/employee/email/callback

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
```

---

## Testing OAuth Flow

### Test Google OAuth

1. Start backend: `cd backend && python -m uvicorn app.main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Open http://localhost:5173
4. Click "Continue as User" (or any role)
5. Click "Continue with Google"
6. Sign in with your Google account
7. You should be redirected back and logged in

### Test Microsoft OAuth

1. Follow same steps as Google OAuth
2. Click "Continue with Microsoft" instead
3. Sign in with your Microsoft account

### Test Gmail Email Feature (Employee Only)

1. Login as an employee user
2. Go to Email tab
3. Click "Connect Gmail"
4. Authorize Gmail access
5. Compose and send a test email

---

## Troubleshooting

### Error: "redirect_uri_mismatch"

**Solution**: Make sure the redirect URI in your code exactly matches what you configured in Google Cloud Console or Azure Portal.

### Error: "invalid_client"

**Solution**: Double-check your Client ID and Client Secret in the `.env` file.

### Error: "access_denied"

**Solution**: 
- For Google: Make sure you added your email as a test user in the OAuth consent screen
- For Microsoft: Check API permissions are granted

### Gmail API "insufficient permissions"

**Solution**: Make sure you enabled the Gmail API and added the correct scopes to your OAuth consent screen.

---

## Production Deployment

When deploying to production:

1. **Update Redirect URIs** in Google Cloud Console and Azure Portal to use your production domain:
   ```
   https://yourdomain.com/auth/callback/google
   https://yourdomain.com/auth/callback/microsoft
   https://yourdomain.com/employee/email/callback
   ```

2. **Update Environment Variables**:
   ```bash
   FRONTEND_BASE_URL=https://yourdomain.com
   GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/callback/google
   MS_REDIRECT_URI=https://yourdomain.com/auth/callback/microsoft
   GMAIL_REDIRECT_URI=https://yourdomain.com/employee/email/callback
   ```

3. **Publish OAuth Consent Screen** (Google):
   - Go to OAuth consent screen
   - Click "Publish App"
   - Submit for verification if needed

4. **Use HTTPS** - OAuth requires HTTPS in production

5. **Implement Token Encryption** - Replace base64 encoding with proper encryption (AES-256 + KMS)

---

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use different credentials** for development and production
3. **Rotate secrets** regularly
4. **Implement rate limiting** on auth endpoints
5. **Use HTTPS** in production
6. **Implement proper token encryption** for stored OAuth tokens
7. **Monitor audit logs** for suspicious activity
8. **Set token expiration** appropriately
9. **Validate state parameter** to prevent CSRF attacks
10. **Use PKCE** for OAuth flows (already implemented)

---

## Support

If you encounter issues:

1. Check the backend logs: `backend/backend_detailed.log`
2. Check browser console for frontend errors
3. Verify all environment variables are set correctly
4. Ensure redirect URIs match exactly (including http/https and trailing slashes)
5. Contact: info@predictivetechlabs.com

---

**Last Updated**: January 2026
