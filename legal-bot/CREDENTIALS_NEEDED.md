# 🔑 Credentials Needed - Complete Checklist

This document lists **exactly** what credentials you need to provide to make the application fully functional.

---

## ✅ Required Credentials

### 1. JWT Secret Key (Required)

**What:** Secret key for signing JWT tokens  
**Where to get:** Generate a random string  
**How to generate:**
```python
import secrets
print(secrets.token_urlsafe(64))
```

**Add to `.env`:**
```bash
JWT_SECRET_KEY=your-generated-secret-key-here
```

---

### 2. OpenAI API Key (Optional - for AI features)

**What:** API key for OpenAI GPT models  
**Where to get:** https://platform.openai.com/api-keys  
**Cost:** Pay-as-you-go (gpt-4o-mini is cheapest)

**Add to `.env`:**
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_CHAT_MODEL=gpt-4o-mini
```

**Note:** Without this, AI chat features won't work, but authentication and employee portal will work fine.

---

## 🔵 Google OAuth Credentials (For "Continue with Google")

### Setup Steps:

1. **Go to:** https://console.cloud.google.com/
2. **Create project:** "LEGID-Auth" (or your name)
3. **Enable APIs:**
   - Google+ API
   - Gmail API (for employee email feature)
4. **Configure OAuth consent screen:**
   - App name: LEGID
   - User support email: your-email@example.com
   - Scopes: openid, email, profile
   - Add test users (your email addresses)
5. **Create credentials:**
   - Type: OAuth 2.0 Client ID
   - Application type: Web application
   - Name: LEGID Web Client
   - Authorized JavaScript origins:
     ```
     http://localhost:5173
     http://localhost:3000
     http://localhost:4200
     ```
   - Authorized redirect URIs:
     ```
     http://localhost:5173/auth/callback/google
     ```
6. **Copy credentials:**
   - Client ID (looks like: `xxxxx.apps.googleusercontent.com`)
   - Client Secret

### Add to `.env`:

```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback/google
```

**Detailed guide:** [OAUTH_SETUP_GUIDE.md](./OAUTH_SETUP_GUIDE.md#google-oauth-setup)

---

## 🟦 Microsoft OAuth Credentials (For "Continue with Microsoft")

### Setup Steps:

1. **Go to:** https://portal.azure.com/
2. **Search:** "Azure Active Directory" or "Microsoft Entra ID"
3. **App registrations** → **New registration**
4. **Configure:**
   - Name: LEGID
   - Supported account types: Multitenant + personal accounts
   - Redirect URI: Web → `http://localhost:5173/auth/callback/microsoft`
5. **Add more redirect URIs:**
   - Go to Authentication → Add URI
   - Add: `http://localhost:3000/auth/callback/microsoft`
   - Add: `http://localhost:4200/auth/callback/microsoft`
6. **Create client secret:**
   - Go to Certificates & secrets
   - New client secret
   - Copy the **Value** immediately (won't show again)
7. **API permissions:**
   - Add permission → Microsoft Graph → Delegated
   - Add: openid, email, profile, User.Read
8. **Copy credentials:**
   - Application (client) ID from Overview page
   - Client secret value from step 6

### Add to `.env`:

```bash
MS_CLIENT_ID=your-application-client-id
MS_CLIENT_SECRET=your-client-secret-value
MS_TENANT=common
MS_REDIRECT_URI=http://localhost:5173/auth/callback/microsoft
```

**Detailed guide:** [OAUTH_SETUP_GUIDE.md](./OAUTH_SETUP_GUIDE.md#microsoft-oauth-setup)

---

## 📧 Gmail OAuth Credentials (For Employee Email Feature)

### Setup Steps:

1. **Use same Google Cloud project** from Google OAuth setup
2. **Enable Gmail API:**
   - APIs & Services → Library
   - Search "Gmail API"
   - Click Enable
3. **Update OAuth consent screen:**
   - OAuth consent screen → Edit App
   - Scopes → Add or Remove Scopes
   - Add: `https://www.googleapis.com/auth/gmail.send`
   - Add: `https://www.googleapis.com/auth/userinfo.email`
4. **Create separate OAuth client** (recommended):
   - Credentials → Create Credentials → OAuth 2.0 Client ID
   - Type: Web application
   - Name: LEGID Gmail Integration
   - Redirect URI: `http://localhost:5173/employee/email/callback`
5. **Copy credentials:**
   - Client ID
   - Client Secret

### Add to `.env`:

```bash
GMAIL_CLIENT_ID=your-gmail-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-gmail-client-secret
GMAIL_REDIRECT_URI=http://localhost:5173/employee/email/callback
```

**Note:** You can use the same credentials as Google OAuth if you prefer, but separate credentials are recommended for security.

**Detailed guide:** [OAUTH_SETUP_GUIDE.md](./OAUTH_SETUP_GUIDE.md#gmail-oauth-setup-for-employee-email)

---

## 📝 Complete `.env` File Template

```bash
# ============================================
# Required for Basic Functionality
# ============================================
DATABASE_URL=sqlite:///./data/legal_bot.db
JWT_SECRET_KEY=CHANGE_THIS_TO_LONG_RANDOM_STRING
FRONTEND_BASE_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:3000,http://localhost:4200,http://localhost:5173

# ============================================
# Optional - OpenAI (for AI features)
# ============================================
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_CHAT_MODEL=gpt-4o-mini
LLM_PROVIDER=openai

# ============================================
# Optional - Google OAuth (for "Continue with Google")
# ============================================
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback/google

# ============================================
# Optional - Microsoft OAuth (for "Continue with Microsoft")
# ============================================
MS_CLIENT_ID=your-application-client-id
MS_CLIENT_SECRET=your-client-secret-value
MS_TENANT=common
MS_REDIRECT_URI=http://localhost:5173/auth/callback/microsoft

# ============================================
# Optional - Gmail OAuth (for employee email feature)
# ============================================
GMAIL_CLIENT_ID=your-gmail-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-gmail-client-secret
GMAIL_REDIRECT_URI=http://localhost:5173/employee/email/callback

# ============================================
# Server Configuration
# ============================================
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
```

---

## 🎯 What Works Without OAuth?

You can test the application **without** setting up OAuth:

✅ **Works:**
- Email/password login
- Email/password registration
- Forgot password flow
- Password reset
- Employee portal
- Matter management
- Chat history viewing
- Document viewing
- All RBAC features

❌ **Doesn't Work:**
- "Continue with Google" button
- "Continue with Microsoft" button
- Employee email sending (requires Gmail OAuth)

---

## 🔄 Priority Order

If you want to test features incrementally:

1. **Start with:** JWT Secret Key only
   - Test password authentication
   - Test employee portal
   - Test matter viewing

2. **Add next:** Google OAuth
   - Test "Continue with Google"
   - Test OAuth flow

3. **Add next:** Gmail OAuth
   - Test employee email feature
   - Test email sending

4. **Optional:** Microsoft OAuth
   - Test "Continue with Microsoft"

---

## ✅ Verification Checklist

After adding credentials, verify:

- [ ] Backend starts without errors
- [ ] Can login with demo account (employee@demo.com)
- [ ] Can see employee dashboard
- [ ] "Continue with Google" button works (if Google OAuth configured)
- [ ] "Continue with Microsoft" button works (if MS OAuth configured)
- [ ] Can connect Gmail in employee portal (if Gmail OAuth configured)
- [ ] Can send test email (if Gmail OAuth configured)

---

## 🆘 Troubleshooting

### "redirect_uri_mismatch" error
- Check redirect URI in Google Cloud Console matches exactly
- Include http:// or https://
- No trailing slashes

### "invalid_client" error
- Double-check Client ID and Client Secret
- Make sure you copied the full string
- Check for extra spaces

### "access_denied" error
- Add your email as test user in OAuth consent screen (Google)
- Grant admin consent (Microsoft)

### Email sending fails
- Check Gmail API is enabled
- Check scopes include gmail.send
- Check redirect URI for Gmail OAuth

---

## 📞 Need Help?

1. **Full OAuth setup guide:** [OAUTH_SETUP_GUIDE.md](./OAUTH_SETUP_GUIDE.md)
2. **Backend logs:** Check `backend/backend_detailed.log`
3. **Browser console:** Check for frontend errors
4. **Contact:** info@predictivetechlabs.com

---

## 🎉 Ready to Start?

1. Copy `backend/env_example_complete.txt` to `backend/.env`
2. Add JWT_SECRET_KEY (required)
3. Add OpenAI API key (optional)
4. Add OAuth credentials (optional)
5. Run `python -m alembic upgrade head`
6. Run `python -m scripts.seed_demo_data`
7. Start backend and frontend
8. Test with demo accounts!

**Quick start guide:** [QUICK_START.md](./QUICK_START.md)

---

Last Updated: January 2026
