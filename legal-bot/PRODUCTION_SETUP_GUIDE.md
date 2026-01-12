# LEGID Production-Level Setup Guide

## 🚀 Complete Implementation Summary

This guide covers the **production-grade** legal bot application with:

✅ **Multi-role authentication** (Client, Employee, Lawyer, Employee Admin)  
✅ **OAuth 2.0** with Google & Microsoft (PKCE flow)  
✅ **Password authentication** with JWT + refresh token rotation  
✅ **Forgot password** flow with email reset links  
✅ **Employee portal** with matter management & email integration  
✅ **Gmail OAuth** for employee email sending  
✅ **Role-based access control** (RBAC)  
✅ **Matter scoping** for employees  
✅ **Audit logging** for all sensitive actions  
✅ **Database migrations** with Alembic  

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [OAuth Configuration](#oauth-configuration)
6. [Database Setup](#database-setup)
7. [Demo Data](#demo-data)
8. [Testing](#testing)
9. [Security Considerations](#security-considerations)
10. [Production Deployment](#production-deployment)

---

## Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 14+** and npm
- **PostgreSQL** (optional, SQLite works for dev)
- **Google Cloud account** (for OAuth)
- **Azure account** (for Microsoft OAuth, optional)

### 1. Clone and Install

```bash
# Clone repository
cd legal-bot

# Backend setup
cd backend
pip install -r requirements.txt
cp env_example_complete.txt .env
# Edit .env with your credentials

# Frontend setup
cd ../frontend
npm install
```

### 2. Configure Environment

Edit `backend/.env`:

```bash
# Required
DATABASE_URL=sqlite:///./data/legal_bot.db
JWT_SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-your-openai-key

# OAuth (see OAUTH_SETUP_GUIDE.md)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret
MS_CLIENT_ID=your-microsoft-client-id
MS_CLIENT_SECRET=your-microsoft-secret
```

### 3. Initialize Database

```bash
cd backend
python -m alembic upgrade head
python -m scripts.seed_demo_data
```

### 4. Run Application

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 5. Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 6. Login with Demo Accounts

```
Client:         client@demo.com     / password123
Lawyer:         lawyer@demo.com     / password123
Employee:       employee@demo.com   / password123
Employee Admin: admin@demo.com      / password123
```

---

## Architecture Overview

### Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy 2.0 (ORM)
- Alembic (database migrations)
- JWT + refresh tokens (authentication)
- Authlib (OAuth 2.0 client)
- OpenAI API (AI features)

**Frontend:**
- React 18
- Vite (build tool)
- CSS3 (styling)

**Database:**
- SQLite (development)
- PostgreSQL (recommended for production)

### Database Schema

```
users
├── oauth_identities (Google/Microsoft links)
├── refresh_tokens (JWT refresh tokens)
├── password_resets (forgot password tokens)
├── email_connections (Gmail OAuth for employees)
├── matters (client legal matters)
│   ├── messages (chat history)
│   ├── documents (uploaded/generated docs)
│   ├── share_packages (sharing with lawyers)
│   └── employee_assignments (employee access)
├── audit_logs (security audit trail)
├── booking_requests (lawyer bookings)
└── lawyer_profiles (lawyer metadata)
```

### User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **CLIENT** | Normal user | Create matters, chat, upload docs, share with lawyers |
| **LAWYER** | Legal professional | View shared matters, accept bookings, access client docs |
| **EMPLOYEE** | Support staff | View assigned matters, see chat/docs, send emails |
| **EMPLOYEE_ADMIN** | Super admin | All employee permissions + assign employees, manage all matters |

---

## Backend Setup

### Directory Structure

```
backend/
├── app/
│   ├── api/routes/
│   │   ├── auth.py          # Auth endpoints
│   │   ├── employee.py      # Employee portal
│   │   ├── email.py         # Email integration
│   │   └── matters.py       # Matter management
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── oauth_service.py
│   │   ├── password_reset_service.py
│   │   ├── email_service.py
│   │   └── ...
│   ├── models/
│   │   └── db_models.py     # All database models
│   ├── database.py
│   └── main.py
├── alembic/                 # Database migrations
├── scripts/
│   └── seed_demo_data.py
├── requirements.txt
└── .env
```

### Key Backend Features

#### 1. Authentication System

**Password Auth:**
- Email/password registration and login
- Bcrypt password hashing
- JWT access tokens (30 min expiry)
- Refresh tokens with rotation (30 day expiry)
- HttpOnly secure cookies (optional)

**OAuth 2.0:**
- Google OAuth with PKCE
- Microsoft OAuth with PKCE
- State validation (CSRF protection)
- Automatic user creation/linking
- Role assignment on first login

**Password Reset:**
- Forgot password flow
- One-time use tokens (30 min expiry)
- Email delivery (console log in dev, SMTP/SendGrid in prod)

#### 2. Employee Portal Features

**Matter Management:**
- View assigned matters only (scoped by EmployeeAssignment)
- Employee Admin sees all matters
- View chat history for assigned matters
- Access documents for assigned matters
- Matter details with AI summary

**Email Integration:**
- Gmail OAuth connection
- Send emails from employee account
- Email audit trail (SentEmail table)
- Matter association for emails
- Encrypted token storage (base64 in dev, AES-256+KMS in prod)

#### 3. Security Features

**RBAC:**
- Role-based permissions
- Matter-level scoping for employees
- SharePackage-based access for lawyers
- Audit logging for all sensitive actions

**Audit Log Events:**
- AUTH_LOGIN_PASSWORD
- AUTH_LOGIN_OAUTH
- AUTH_LOGOUT
- PASSWORD_RESET_REQUESTED
- PASSWORD_RESET_COMPLETED
- OAUTH_LINKED
- MATTER_VIEWED
- MESSAGE_VIEWED
- DOCUMENT_DOWNLOADED
- EMAIL_SENT
- EMPLOYEE_ASSIGNED

---

## Frontend Setup

### Directory Structure

```
frontend/src/
├── components/
│   ├── RoleSelection.jsx      # Landing page
│   ├── AuthPage.jsx           # Login/register/forgot
│   ├── OAuthCallback.jsx      # OAuth redirect handler
│   ├── ResetPassword.jsx      # Password reset page
│   ├── EmployeePortal.jsx     # Employee dashboard
│   ├── ChatInterface.jsx      # Client chat (existing)
│   └── ...
├── AppNew.jsx                 # Main app with routing
└── main.jsx
```

### Frontend Flow

```
1. Role Selection (/)
   ↓
2. Auth Page (/auth?mode=client|employee|lawyer)
   ├─ Email/Password Login
   ├─ Google OAuth
   ├─ Microsoft OAuth
   ├─ Create Account
   └─ Forgot Password
   ↓
3. OAuth Callback (/auth/callback/google|microsoft)
   ↓
4. Portal Routing:
   ├─ Client → /app/matters (ChatInterface)
   ├─ Employee → /employee/dashboard (EmployeePortal)
   ├─ Lawyer → /lawyer/leads (LawyerPortal - placeholder)
   └─ Admin → /admin (same as employee)
```

### Using the New Frontend

Replace `frontend/src/main.jsx`:

```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import AppNew from './AppNew.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AppNew />
  </React.StrictMode>,
)
```

---

## OAuth Configuration

See **[OAUTH_SETUP_GUIDE.md](./OAUTH_SETUP_GUIDE.md)** for complete instructions.

### Quick Summary

**Google OAuth:**
1. Create project in Google Cloud Console
2. Enable Google+ API
3. Configure OAuth consent screen
4. Create OAuth 2.0 credentials (Web application)
5. Add redirect URIs: `http://localhost:5173/auth/callback/google`
6. Copy Client ID and Secret to `.env`

**Microsoft OAuth:**
1. Register app in Azure Portal
2. Add redirect URI: `http://localhost:5173/auth/callback/microsoft`
3. Create client secret
4. Add API permissions (openid, email, profile, User.Read)
5. Copy Application ID and Secret to `.env`

**Gmail OAuth (Employee Email):**
1. Enable Gmail API in Google Cloud
2. Add scope: `https://www.googleapis.com/auth/gmail.send`
3. Create separate OAuth client (recommended)
4. Add redirect URI: `http://localhost:5173/employee/email/callback`
5. Copy credentials to `.env`

---

## Database Setup

### Using SQLite (Development)

```bash
# Already configured in .env
DATABASE_URL=sqlite:///./data/legal_bot.db

# Run migrations
cd backend
python -m alembic upgrade head
```

### Using PostgreSQL (Production)

```bash
# Install PostgreSQL
# Create database
createdb legal_bot

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/legal_bot

# Run migrations
python -m alembic upgrade head
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## Demo Data

### Seed Demo Users and Matters

```bash
cd backend
python -m scripts.seed_demo_data
```

This creates:
- 4 demo users (one for each role)
- 3 sample matters
- Chat messages and documents
- Employee assignments

### Demo Accounts

| Email | Password | Role |
|-------|----------|------|
| client@demo.com | password123 | CLIENT |
| lawyer@demo.com | password123 | LAWYER |
| employee@demo.com | password123 | EMPLOYEE |
| admin@demo.com | password123 | EMPLOYEE_ADMIN |

---

## Testing

### Test Scenarios

#### 1. Role Selection & Auth

```
✓ Visit http://localhost:5173
✓ Click "Continue as User"
✓ Click "Continue with Google"
✓ Sign in with Google account
✓ Should redirect to client portal
```

#### 2. Password Auth

```
✓ Click "Continue as Employee"
✓ Enter: employee@demo.com / password123
✓ Should redirect to employee dashboard
```

#### 3. Forgot Password

```
✓ Click "Forgot password?"
✓ Enter email address
✓ Check backend console for reset link
✓ Visit reset link
✓ Set new password
✓ Login with new password
```

#### 4. Employee Portal

```
✓ Login as employee@demo.com
✓ View assigned matters (should see 2)
✓ Click on a matter to view details
✓ See chat history and documents
✓ Go to Email tab
✓ Connect Gmail (requires OAuth setup)
✓ Send test email
```

#### 5. Matter Scoping

```
✓ Login as employee@demo.com
✓ Should only see 2 assigned matters
✓ Login as admin@demo.com
✓ Should see all 3 matters
```

---

## Security Considerations

### ⚠️ Development vs Production

**Current Implementation (Development):**
- ✅ JWT with refresh token rotation
- ✅ PKCE for OAuth
- ✅ State validation
- ✅ Password hashing (bcrypt)
- ✅ Token hashing (SHA-256)
- ⚠️ Token encryption: **base64 only** (NOT SECURE)
- ⚠️ CORS: allows all origins

**Required for Production:**

1. **Token Encryption:**
   ```python
   # Replace base64 with AES-256
   from cryptography.fernet import Fernet
   
   # Use KMS (AWS KMS, Google Cloud KMS, Azure Key Vault)
   # Store encryption key in secret manager
   ```

2. **HTTPS Only:**
   ```python
   # Enforce HTTPS
   # Set secure cookies
   # Update OAuth redirect URIs to https://
   ```

3. **CORS Configuration:**
   ```python
   # Update main.py
   CORS_ORIGINS = ["https://yourdomain.com"]
   ```

4. **Rate Limiting:**
   ```python
   # Add rate limiting to auth endpoints
   from slowapi import Limiter
   ```

5. **Environment Variables:**
   - Use secret manager (AWS Secrets Manager, etc.)
   - Never commit `.env` files
   - Rotate secrets regularly

6. **Database:**
   - Use PostgreSQL with SSL
   - Enable connection pooling
   - Regular backups

7. **Monitoring:**
   - Set up error tracking (Sentry)
   - Monitor audit logs
   - Alert on suspicious activity

---

## Production Deployment

### 1. Update Environment Variables

```bash
# Production .env
DATABASE_URL=postgresql://user:pass@prod-db:5432/legal_bot
JWT_SECRET_KEY=<long-random-production-key>
FRONTEND_BASE_URL=https://yourdomain.com
CORS_ORIGINS=https://yourdomain.com

# OAuth with production URLs
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/callback/google
MS_REDIRECT_URI=https://yourdomain.com/auth/callback/microsoft
GMAIL_REDIRECT_URI=https://yourdomain.com/employee/email/callback
```

### 2. Update OAuth Providers

- Add production redirect URIs in Google Cloud Console
- Add production redirect URIs in Azure Portal
- Publish OAuth consent screen (Google)

### 3. Build Frontend

```bash
cd frontend
npm run build
# Deploy dist/ folder to CDN or static hosting
```

### 4. Deploy Backend

```bash
# Using Docker
docker build -t legal-bot-backend .
docker run -p 8000:8000 --env-file .env legal-bot-backend

# Or using Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 5. Database Migration

```bash
# On production server
python -m alembic upgrade head
```

### 6. SSL/TLS

- Use Let's Encrypt for free SSL certificates
- Configure Nginx/Apache as reverse proxy
- Enforce HTTPS redirects

---

## API Documentation

Once backend is running, visit:

**Swagger UI:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

### Key Endpoints

**Auth:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/oauth/{provider}/start` - Start OAuth flow
- `POST /api/auth/oauth/{provider}/exchange` - Exchange OAuth code
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password

**Employee:**
- `GET /api/employee/dashboard` - Get dashboard stats
- `GET /api/employee/matters` - List assigned matters
- `GET /api/employee/matters/{id}` - Get matter details
- `GET /api/employee/matters/{id}/messages` - Get chat history
- `GET /api/employee/matters/{id}/documents` - Get documents

**Email:**
- `GET /api/email/connect/gmail/start` - Start Gmail OAuth
- `POST /api/email/connect/gmail/exchange` - Complete Gmail OAuth
- `POST /api/email/send` - Send email
- `GET /api/email/sent` - List sent emails

---

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt

# Check database
python -c "from app.database import engine; print(engine)"
```

### Frontend won't start

```bash
# Clear node_modules
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 14+
```

### OAuth errors

- Check redirect URIs match exactly (including http/https)
- Verify Client ID and Secret in `.env`
- Check OAuth consent screen is configured
- Add test users (Google) or grant permissions (Microsoft)

### Database errors

```bash
# Reset database
rm data/legal_bot.db
python -m alembic upgrade head
python -m scripts.seed_demo_data
```

---

## Support

**Documentation:**
- [OAuth Setup Guide](./OAUTH_SETUP_GUIDE.md)
- [Main README](./README.md)

**Contact:**
- Email: info@predictivetechlabs.com
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)

---

## License

MIT License - See LICENSE file for details.

---

**Built with ❤️ for production-grade legal tech**

Last Updated: January 2026
