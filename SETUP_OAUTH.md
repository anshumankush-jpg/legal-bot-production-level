# OAuth Setup Guide for LEGID

This guide will walk you through setting up Google and Microsoft OAuth authentication for LEGID.

## Prerequisites

- Google Cloud Platform account
- Microsoft Azure account
- Access to your backend and frontend deployment URLs

---

## Part 1: Google OAuth Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: "LEGID" (or your preferred name)
4. Click "Create"

### Step 2: Configure OAuth Consent Screen

1. In the left menu, go to **APIs & Services** → **OAuth consent screen**
2. Select **External** (or Internal if using Google Workspace)
3. Click **Create**
4. Fill in the required fields:
   - **App name**: LEGID
   - **User support email**: your-email@example.com
   - **Developer contact email**: your-email@example.com
5. Click **Save and Continue**
6. On the **Scopes** page, click **Add or Remove Scopes**
7. Select these scopes:
   - `openid`
   - `email`
   - `profile`
8. Click **Update** → **Save and Continue**
9. On **Test users** (if in External mode), add your test email addresses
10. Click **Save and Continue** → **Back to Dashboard**

### Step 3: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Select **Application type**: Web application
4. Enter name: "LEGID Web Client"
5. Under **Authorized JavaScript origins**, add:
   ```
   http://localhost:4200
   http://localhost:5173
   https://your-production-domain.com
   ```
6. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:4200/auth/callback/google
   http://localhost:8000/api/auth/google/callback
   https://your-production-domain.com/auth/callback/google
   https://your-backend-domain.run.app/api/auth/google/callback
   ```
7. Click **Create**
8. **Copy the Client ID and Client Secret** - you'll need these for your `.env` file

### Step 4: Update Your Backend .env

Add these to `backend/.env`:

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:4200/auth/callback/google
```

For production:
```bash
GOOGLE_REDIRECT_URI=https://your-domain.com/auth/callback/google
```

---

## Part 2: Microsoft OAuth Setup

### Step 1: Register an Application

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** (or use search)
3. Click **App registrations** → **New registration**
4. Fill in:
   - **Name**: LEGID
   - **Supported account types**: Accounts in any organizational directory and personal Microsoft accounts
   - **Redirect URI**: 
     - Platform: **Web**
     - URL: `http://localhost:8000/api/auth/microsoft/callback`
5. Click **Register**

### Step 2: Add Additional Redirect URIs

1. In your app registration, go to **Authentication**
2. Click **Add a platform** → **Web**
3. Add these redirect URIs:
   ```
   http://localhost:4200/auth/callback/microsoft
   http://localhost:8000/api/auth/microsoft/callback
   https://your-production-domain.com/auth/callback/microsoft
   https://your-backend-domain.run.app/api/auth/microsoft/callback
   ```
4. Under **Implicit grant and hybrid flows**, check:
   - ☑ Access tokens
   - ☑ ID tokens
5. Click **Save**

### Step 3: Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Description: "LEGID Backend Secret"
4. Expires: 24 months (or as needed)
5. Click **Add**
6. **Copy the Value immediately** (you can't see it again!)

### Step 4: Configure API Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Select **Delegated permissions**
5. Add these permissions:
   - `openid`
   - `email`
   - `profile`
   - `User.Read`
6. Click **Add permissions**
7. Click **Grant admin consent** (if you're an admin)

### Step 5: Copy Application Details

1. Go to **Overview**
2. Copy these values:
   - **Application (client) ID**
   - **Directory (tenant) ID**

### Step 6: Update Your Backend .env

Add these to `backend/.env`:

```bash
MS_CLIENT_ID=your-application-client-id
MS_CLIENT_SECRET=your-client-secret-value
MS_TENANT=common
MS_REDIRECT_URI=http://localhost:4200/auth/callback/microsoft
```

For production:
```bash
MS_REDIRECT_URI=https://your-domain.com/auth/callback/microsoft
```

**Tenant Options:**
- `common` - Multi-tenant + personal Microsoft accounts (recommended)
- `organizations` - Multi-tenant only (Azure AD accounts)
- `consumers` - Personal Microsoft accounts only
- `your-tenant-id` - Single tenant only

---

## Part 3: Testing OAuth Locally

### Start Your Services

1. **Backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

### Test Google OAuth

1. Go to `http://localhost:4200/login`
2. Click "Continue with Google"
3. You should be redirected to Google's login page
4. After logging in, you'll be redirected back to `/chat`

### Test Microsoft OAuth

1. Go to `http://localhost:4200/login`
2. Click "Continue with Microsoft"
3. You should be redirected to Microsoft's login page
4. After logging in, you'll be redirected back to `/chat`

---

## Part 4: Production Deployment

### Update OAuth Redirect URIs

#### Google Console

1. Go to **Credentials** → Your OAuth Client
2. Add production redirect URIs:
   ```
   https://your-frontend-domain.com/auth/callback/google
   https://your-backend-domain.run.app/api/auth/google/callback
   ```

#### Azure Portal

1. Go to your app registration → **Authentication**
2. Add production redirect URIs:
   ```
   https://your-frontend-domain.com/auth/callback/microsoft
   https://your-backend-domain.run.app/api/auth/microsoft/callback
   ```

### Update Environment Variables

**Backend** (`backend/.env`):
```bash
GOOGLE_REDIRECT_URI=https://your-frontend-domain.com/auth/callback/google
MS_REDIRECT_URI=https://your-frontend-domain.com/auth/callback/microsoft
FRONTEND_BASE_URL=https://your-frontend-domain.com
```

**Frontend** (`frontend/.env`):
```bash
VITE_API_URL=https://your-backend-domain.run.app
VITE_GOOGLE_REDIRECT_URI=https://your-frontend-domain.com/auth/callback/google
VITE_MICROSOFT_REDIRECT_URI=https://your-frontend-domain.com/auth/callback/microsoft
```

---

## Troubleshooting

### "redirect_uri_mismatch" Error

**Problem**: OAuth provider rejects the redirect URI.

**Solution**:
1. Check that the redirect URI in your code **exactly matches** what's in the OAuth provider console
2. Include the protocol (`http://` or `https://`)
3. Don't include trailing slashes unless they're in your code too
4. For Google, make sure the URI is in **both** "Authorized JavaScript origins" AND "Authorized redirect URIs"

### "invalid_client" Error (Google)

**Problem**: Client ID or secret is wrong.

**Solution**:
1. Double-check you copied the correct Client ID and Secret
2. Make sure there are no extra spaces or newlines
3. Regenerate the client secret if needed

### "AADSTS50011" Error (Microsoft)

**Problem**: Redirect URI not registered.

**Solution**:
1. Go to Azure Portal → Your app → Authentication
2. Make sure the redirect URI is listed exactly as your code sends it
3. Save changes and wait a few minutes for propagation

### User Not Created in Database

**Problem**: OAuth succeeds but user isn't in your database.

**Solution**:
1. Check backend logs for errors
2. Ensure database tables are created (run migrations)
3. Verify database connection string is correct

### CORS Errors

**Problem**: Frontend can't call backend OAuth endpoints.

**Solution**:
1. Add frontend URL to `CORS_ORIGINS` in backend `.env`
2. Restart backend server
3. Clear browser cache

---

## Security Best Practices

1. **Never commit `.env` files** - add them to `.gitignore`
2. **Use environment-specific secrets** - different secrets for dev/staging/prod
3. **Rotate secrets regularly** - especially after team member changes
4. **Use HTTPS in production** - OAuth providers require it
5. **Validate state parameter** - prevents CSRF attacks (our implementation includes this)
6. **Limit OAuth scopes** - only request what you need
7. **Monitor OAuth usage** - watch for suspicious patterns

---

## Next Steps

After OAuth is working:

1. ✅ Test user creation and login
2. ✅ Verify user data is saved to database
3. ✅ Test token refresh flow
4. ✅ Implement user profile display
5. ✅ Add logout functionality
6. ⬜ Set up email verification (optional)
7. ⬜ Configure user roles and permissions

---

## Support

If you encounter issues:

1. Check the [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
2. Check the [Microsoft Identity Platform Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
3. Review backend logs for detailed error messages
4. Open an issue in the project repository
