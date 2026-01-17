# 🔑 Environment Values Needed

**Please provide the following values to complete your setup.**

Once you provide these, I can generate ready-to-use `.env` files for you.

---

## A) Google OAuth

Get from: [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials

```
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

**Local redirect URI**: `http://localhost:4200/auth/callback/google` (already configured)  
**Production redirect URI** (when deploying): `https://your-domain.com/auth/callback/google`

---

## B) Microsoft OAuth (Azure AD)

Get from: [Azure Portal](https://portal.azure.com/) → Azure Active Directory → App registrations

```
MICROSOFT_TENANT_ID=common
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=
```

**Local redirect URI**: `http://localhost:4200/auth/callback/microsoft` (already configured)  
**Production redirect URI** (when deploying): `https://your-domain.com/auth/callback/microsoft`

---

## C) App URLs

**Local (defaults work fine):**
```
FRONTEND_URL=http://localhost:4200
BACKEND_URL=http://localhost:8000
```

**Production (when deploying):**
```
FRONTEND_URL=https://your-frontend-domain.com
BACKEND_URL=https://your-backend-url.run.app
```

---

## D) JWT / Cookies

**JWT Secret** (generate a random 32+ character string):

**Linux/Mac:**
```bash
openssl rand -base64 32
```

**Windows PowerShell:**
```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

**Or use an online generator**: https://www.random.org/strings/

```
JWT_SECRET=
```

**Token TTLs** (defaults are fine):
```
ACCESS_TOKEN_TTL_MIN=30
REFRESH_TOKEN_TTL_DAYS=30
```

**Cookie mode**: Using HttpOnly cookies (already configured)

---

## E) Database

**Local development** (default - no action needed):
```
DATABASE_URL=sqlite:///./data/legal_bot.db
```

**Production** (PostgreSQL on Cloud SQL):
```
DATABASE_URL=postgresql://user:password@/dbname?host=/cloudsql/project:region:instance
```

**BigQuery logging** (optional - leave disabled for now):
```
BIGQUERY_ENABLED=false
```

---

## 📝 What to Do

### Option 1: Provide Values Now

Reply with:
```
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
MS_CLIENT_ID=xxx
MS_CLIENT_SECRET=xxx
JWT_SECRET=xxx
```

And I'll generate complete `.env` files for you.

### Option 2: Set Up OAuth First

Follow [SETUP_OAUTH.md](SETUP_OAUTH.md) to:
1. Create Google OAuth client (5 min)
2. Create Microsoft app registration (5 min)
3. Get credentials

Then provide the values.

### Option 3: Use Placeholders for Now

You can start with placeholder values in local development:

```bash
# backend/.env
GOOGLE_CLIENT_ID=placeholder-google-client-id
GOOGLE_CLIENT_SECRET=placeholder-google-secret
MS_CLIENT_ID=placeholder-microsoft-client-id
MS_CLIENT_SECRET=placeholder-microsoft-secret
JWT_SECRET=placeholder-jwt-secret-at-least-32-chars
```

This will let you test email/password authentication while you set up OAuth.

---

## 🚀 Quick Start Without OAuth

If you want to test immediately without OAuth:

1. **Create minimal `.env`**:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `backend/.env`** - only set these:
   ```bash
   OPENAI_API_KEY=sk-your-openai-key
   JWT_SECRET_KEY=any-random-32-character-string-here
   DATABASE_URL=sqlite:///./data/legal_bot.db
   FRONTEND_BASE_URL=http://localhost:4200
   CORS_ORIGINS=http://localhost:4200
   ```

3. **Initialize database**:
   ```bash
   python init_database.py init
   ```

4. **Start backend**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. **Start frontend** (new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

6. **Test email/password authentication**:
   - Go to http://localhost:4200/signup
   - Create account with email/password
   - Login works!

7. **Add OAuth later** when you get credentials.

---

## ✅ Summary

**Mandatory to run locally:**
- ✅ `OPENAI_API_KEY` (for chat)
- ✅ `JWT_SECRET_KEY` (for auth)

**Optional but recommended:**
- 🔑 `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`
- 🔑 `MS_CLIENT_ID` + `MS_CLIENT_SECRET`

**For production:**
- 🌐 Production URLs
- 🗄️ PostgreSQL database
- 🔐 Updated OAuth redirect URIs

---

## 📖 Next Steps

1. **Choose your approach**:
   - Quick test → Use placeholders for OAuth, start now
   - Complete setup → Get OAuth credentials first
   - Production → Get all production values

2. **Follow the guide**:
   - [QUICK_START.md](QUICK_START.md) for local setup
   - [SETUP_OAUTH.md](SETUP_OAUTH.md) for OAuth credentials
   - [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production

3. **Get running**:
   - Initialize database
   - Start services
   - Test authentication

---

## 🆘 Need Help?

- **Getting OAuth credentials**: [SETUP_OAUTH.md](SETUP_OAUTH.md)
- **Local setup**: [QUICK_START.md](QUICK_START.md)
- **Production deployment**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

**Ready to provide values? Just reply with your credentials and I'll generate complete `.env` files!**

**Or proceed with placeholders and add OAuth later using [SETUP_OAUTH.md](SETUP_OAUTH.md).**
