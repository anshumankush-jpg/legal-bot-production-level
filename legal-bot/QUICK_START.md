# 🚀 LEGID - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (2 minutes)

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Step 2: Configure Environment (1 minute)

```bash
cd backend
cp env_example_complete.txt .env
```

Edit `.env` - **Minimum required:**
```bash
DATABASE_URL=sqlite:///./data/legal_bot.db
JWT_SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-your-openai-key  # Optional for AI features

# OAuth (optional for testing with demo accounts)
GOOGLE_CLIENT_ID=your-id
GOOGLE_CLIENT_SECRET=your-secret
```

### Step 3: Initialize Database (1 minute)

```bash
cd backend
python -m alembic upgrade head
python -m scripts.seed_demo_data
```

### Step 4: Start Application (1 minute)

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Step 5: Access & Login

1. Open http://localhost:5173
2. Click "Continue as Employee"
3. Login: `employee@demo.com` / `password123`
4. Explore the employee portal!

---

## 🎯 Demo Accounts

| Email | Password | Role | Access |
|-------|----------|------|--------|
| `client@demo.com` | `password123` | CLIENT | Chat interface, create matters |
| `employee@demo.com` | `password123` | EMPLOYEE | View 2 assigned matters, send emails |
| `admin@demo.com` | `password123` | EMPLOYEE_ADMIN | View all matters, assign employees |
| `lawyer@demo.com` | `password123` | LAWYER | View shared matters, bookings |

---

## 🔑 OAuth Setup (Optional)

### For Google Login:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Google+ API
3. OAuth consent screen → Add scopes (openid, email, profile)
4. Create credentials → OAuth 2.0 Client ID
5. Add redirect URI: `http://localhost:5173/auth/callback/google`
6. Copy Client ID & Secret to `.env`

**Full guide:** [OAUTH_SETUP_GUIDE.md](./OAUTH_SETUP_GUIDE.md)

---

## 📱 Test Scenarios

### Test 1: Password Login
```
1. Visit http://localhost:5173
2. Click "Continue as Employee"
3. Enter: employee@demo.com / password123
4. ✓ Should see employee dashboard
```

### Test 2: View Assigned Matters
```
1. Login as employee
2. Click "Matters" tab
3. ✓ Should see 2 assigned matters
4. Click on a matter
5. ✓ Should see chat history and documents
```

### Test 3: Employee Admin
```
1. Login as admin@demo.com
2. Click "Matters" tab
3. ✓ Should see all 3 matters (not just assigned)
```

### Test 4: Forgot Password
```
1. Click "Forgot password?"
2. Enter: employee@demo.com
3. Check backend console for reset link
4. Visit link and set new password
5. ✓ Should be able to login with new password
```

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.8+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start
```bash
# Check Node version (need 14+)
node --version

# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database errors
```bash
# Reset database
rm data/legal_bot.db
python -m alembic upgrade head
python -m scripts.seed_demo_data
```

### Can't see matters in employee portal
- Make sure you're logged in as `employee@demo.com` or `admin@demo.com`
- Demo data creates assignments for employee account
- Admin can see all matters

---

## 📚 Documentation

- **[IMPLEMENTATION_COMPLETE.md](./IMPLEMENTATION_COMPLETE.md)** - Full feature list
- **[OAUTH_SETUP_GUIDE.md](./OAUTH_SETUP_GUIDE.md)** - Complete OAuth setup
- **[PRODUCTION_SETUP_GUIDE.md](./PRODUCTION_SETUP_GUIDE.md)** - Production deployment
- **[README.md](./README.md)** - Original project README

---

## 🎨 Frontend Components

To use the new authentication system, update `frontend/src/main.jsx`:

```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import AppNew from './AppNew.jsx'  // ← Change this
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AppNew />  {/* ← Change this */}
  </React.StrictMode>,
)
```

---

## 🔐 Security Notes

**Development Mode:**
- Token encryption: base64 (NOT SECURE for production)
- CORS: allows all origins
- HTTPS: not enforced

**For Production:**
- Implement AES-256 token encryption with KMS
- Restrict CORS to your domain
- Enforce HTTPS
- Use PostgreSQL with SSL
- See [PRODUCTION_SETUP_GUIDE.md](./PRODUCTION_SETUP_GUIDE.md)

---

## 📞 Need Help?

1. Check [IMPLEMENTATION_COMPLETE.md](./IMPLEMENTATION_COMPLETE.md) for feature details
2. Check [OAUTH_SETUP_GUIDE.md](./OAUTH_SETUP_GUIDE.md) for OAuth issues
3. Check backend logs: `backend/backend_detailed.log`
4. Contact: info@predictivetechlabs.com

---

## ✅ Quick Checklist

- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] `.env` file configured
- [ ] Database initialized
- [ ] Demo data seeded
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can login with demo account
- [ ] Employee portal accessible

---

**🎉 You're ready to go! Start with the demo accounts and explore the features.**

For OAuth setup, see [OAUTH_SETUP_GUIDE.md](./OAUTH_SETUP_GUIDE.md)

Last Updated: January 2026
