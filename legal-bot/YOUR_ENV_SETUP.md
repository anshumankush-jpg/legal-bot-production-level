# 🔧 Your .env File Configuration

## ✅ Step 1: Create `.env` file

In `backend/` folder, create a file named `.env` (with the dot at the start)

## ✅ Step 2: Copy This Exact Content

```bash
# ============================================
# LEGID Backend Environment Configuration
# ============================================

# ============================================
# Database Configuration
# ============================================
DATABASE_URL=sqlite:///./data/legal_bot.db

# ============================================
# JWT Authentication Configuration
# ============================================
JWT_SECRET_KEY=REPLACE_THIS_WITH_GENERATED_SECRET_SEE_BELOW
JWT_ACCESS_TTL_MIN=30
JWT_REFRESH_TTL_DAYS=30

# ============================================
# Frontend Configuration
# ============================================
FRONTEND_BASE_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:3000,http://localhost:4200,http://localhost:5173

# ============================================
# Google OAuth Configuration (User Authentication)
# ============================================
GOOGLE_CLIENT_ID=1086283983680-m0rg0loe9ktg0vd4rv5onmarr8lgpqbu.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=REPLACE_WITH_YOUR_CLIENT_SECRET_FROM_GOOGLE_CONSOLE
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback/google

# ============================================
# Server Configuration
# ============================================
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
```

---

## ✅ Step 3: Get Your Client Secret

1. **Go back to Google Cloud Console**
2. **On the OAuth client page** (where you saw the Client ID)
3. **Look for "Client Secret"** - it looks like: `GOCSPX-xxxxxxxxxxxxx`
4. **Copy it**
5. **Replace** `REPLACE_WITH_YOUR_CLIENT_SECRET_FROM_GOOGLE_CONSOLE` in the `.env` file

---

## ✅ Step 4: Generate JWT Secret Key

**Run this command:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

**Example output:**
```
TaB9xK3mN8pQrS4vW5yZ1aC7dE2fG6hJ8iL0mN3oP5qR7sT9uV1wX3yZ5aB7cD9e
```

**Replace** `REPLACE_THIS_WITH_GENERATED_SECRET_SEE_BELOW` with the output

---

## ✅ Step 5: Your Complete `.env` Should Look Like

```bash
DATABASE_URL=sqlite:///./data/legal_bot.db

JWT_SECRET_KEY=TaB9xK3mN8pQrS4vW5yZ1aC7dE2fG6hJ8iL0mN3oP5qR7sT9uV1wX3yZ5aB7cD9e
JWT_ACCESS_TTL_MIN=30
JWT_REFRESH_TTL_DAYS=30

FRONTEND_BASE_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:3000,http://localhost:4200,http://localhost:5173

GOOGLE_CLIENT_ID=1086283983680-m0rg0loe9ktg0vd4rv5onmarr8lgpqbu.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-AbCdEfGhIjKlMnOpQrStUvWxYz
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback/google

HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
```

*(With your actual secret values)*

---

## ✅ Step 6: Initialize Database

```bash
cd backend
python -m alembic upgrade head
python -m scripts.seed_demo_data
```

---

## ✅ Step 7: Start Everything

**Terminal 1:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2:**
```bash
cd frontend
npm run dev
```

---

## ✅ Step 8: Test It!

1. Open: http://localhost:5173
2. Click "Continue as User"
3. Click "Continue with Google"
4. Should redirect to Google and back! ✨

---

## 🔍 What You Need:

- ✅ **Client ID:** `1086283983680-m0rg0loe9ktg0vd4rv5onmarr8lgpqbu.apps.googleusercontent.com` (DONE)
- ⏳ **Client Secret:** Get from Google Console (looks like `GOCSPX-...`)
- ⏳ **JWT Secret:** Generate with Python command above

---

## 📋 Quick Checklist

- [ ] Created `backend/.env` file
- [ ] Copied the template above
- [ ] Got Client Secret from Google Console
- [ ] Generated JWT Secret Key
- [ ] Replaced both placeholders in `.env`
- [ ] Saved the file
- [ ] Run: `python -m alembic upgrade head`
- [ ] Run: `python -m scripts.seed_demo_data`
- [ ] Start backend
- [ ] Start frontend
- [ ] Test at http://localhost:5173

**You're almost there!** 🚀
