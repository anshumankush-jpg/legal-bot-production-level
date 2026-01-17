# ChatGPT-Style Profile & Account System - Complete Implementation

## Overview

This document describes the complete implementation of the ChatGPT-like profile and account management system for LEGID/LegalAI. The system includes a full-stack solution with Angular frontend, FastAPI backend, and BigQuery database.

---

## ✅ Features Implemented

### 1. **Profile Menu (Bottom-Left Sidebar)**
- Avatar with initials fallback
- Display name and email
- Dropdown menu with the following items:
  - **Profile Header** (clickable to open Edit Profile modal)
  - Personalization
  - Settings
  - Help (with submenu)
  - Log out
- **Account Summary Card** showing current account with role label
- Clicking outside closes menu (with keyboard support: ESC)

### 2. **Edit Profile Modal**
- Large avatar circle with camera icon
- Click to upload avatar (PNG/JPG/WEBP, max 5MB)
- Preview before save
- Upload to Google Cloud Storage via signed URL
- **Display name** input
- **Username** input:
  - Must be unique (checked via API)
  - Validation: lowercase letters, numbers, underscore only
  - Length: 3-20 characters
  - Real-time validation feedback
- **Email** (read-only)
- **Phone** (optional)
- **Address fields** (optional):
  - Address line 1 & 2
  - City, Province/State, Postal/Zip
  - Country (select)
- Cancel/Save buttons
- Instant UI update after save

### 3. **Personalization Page** (`/personalization`)
Allows users to customize their experience:
- **Theme**: Dark / Light / System
- **Font Size**: Small / Medium / Large
- **Response Style**: Concise / Balanced / Detailed
- **Legal Tone**: Neutral / Firm / Very Formal
- **Auto-Read Responses**: Toggle for text-to-speech
- **Language**: English / Français / Español / Deutsch
- Auto-save (1-second debounce)
- Changes persist and apply immediately

### 4. **Settings Page** (`/settings`)
- **Profile Section**: Link to edit profile modal
- **Privacy & Cookies Section**:
  - Necessary cookies (always active)
  - Analytics cookies (toggle)
  - Marketing cookies (toggle)
  - Links to Cookie Policy and Privacy Policy
- **Account Information**:
  - Email (read-only)
  - Role display (Client / Lawyer / Employee)
  - Lawyer verification status (if applicable)
  - Member since date
- **Danger Zone**:
  - "Log out from all devices" button

### 5. **Help System** (`/help`)
Tabbed interface with the following sections:
- **Help Center**: FAQ with expandable questions
- **Release Notes**: Version history with changes
- **Terms & Policies**: Links to legal documents
- **Report Bug**: Form to submit bug reports
- **Keyboard Shortcuts**: List of all shortcuts
- **Download Apps**: iOS / Android / Desktop / Web

### 6. **Backend API Endpoints**

All endpoints are in `/backend/app/api/routes/profile.py`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/api/me` | Get current user info + profile |
| **POST** | `/api/logout` | Logout current session |
| **POST** | `/api/logout/all` | Logout from all devices |
| **GET** | `/api/profile` | Get user profile |
| **PUT** | `/api/profile` | Update user profile |
| **GET** | `/api/profile/check-username/{username}` | Check if username is available |
| **POST** | `/api/avatar/upload-url` | Get signed URL for avatar upload |
| **PUT** | `/api/profile/avatar` | Update avatar URL after upload |
| **PUT** | `/api/profile/preferences` | Update user preferences |
| **GET** | `/api/consent` | Get user consent settings |
| **PUT** | `/api/consent` | Update user consent settings |
| **POST** | `/api/request-access` | Request access (non-provisioned users) |

### 7. **Database (BigQuery)**

Complete schema defined in `/backend/docs/bigquery_schema.sql`:

#### Tables:
1. **identity_users** - User authentication and identity
   - user_id, auth_provider, auth_uid, email
   - role (customer/lawyer/admin)
   - lawyer_status (not_applicable/pending/approved/rejected)
   - is_provisioned (boolean)
   - env (dev/prod)

2. **user_profiles** - Profile information
   - user_id, display_name, username, avatar_url
   - phone, address fields
   - preferences_json (JSON string with all preferences)

3. **user_consent** - Cookie and data usage consent
   - user_id, necessary, analytics, marketing, functional

4. **access_requests** - Non-provisioned user access requests
   - id, email, name, requested_role, reason, organization
   - status (pending/approved/rejected)

### 8. **Route Guards**

- **AuthGuard**: Ensures user is authenticated
- **ProvisionedGuard**: Blocks non-provisioned users
- **RoleGuard**: Checks user role and lawyer verification status
- **SetupGuard**: Ensures first-time setup is complete

### 9. **Access Control**

- **Provisioning System**: Only users in `identity_users` table with `is_provisioned=true` can access the app
- **Not-Provisioned Page**: Users not in the system see a dedicated page with "Request Access" form
- **Role-Based Access**: Lawyer-only routes require `role='lawyer'` AND `lawyer_status='approved'`

---

## 🏗️ Architecture

### Frontend (Angular)
```
frontend/src/app/
├── components/
│   ├── sidebar-profile-menu/       # Bottom-left profile menu
│   └── edit-profile-modal/         # Edit profile modal
├── pages/
│   ├── personalization/            # Personalization settings
│   ├── settings/                   # Account settings
│   ├── help/                       # Help system
│   ├── not-provisioned/            # Access denied page
│   └── access-denied/              # Role-restricted page
├── services/
│   ├── auth.service.ts             # Authentication + session
│   └── profile.service.ts          # Profile management
└── guards/
    ├── auth.guard.ts               # Auth check
    ├── provisioned.guard.ts        # Provisioning check
    ├── role.guard.ts               # Role-based access
    └── setup.guard.ts              # Setup completion check
```

### Backend (FastAPI)
```
backend/
├── app/
│   ├── api/routes/
│   │   └── profile.py              # Profile & account endpoints
│   ├── models/
│   │   └── db_models.py            # SQLAlchemy models
│   └── services/
│       └── profile_service.py      # Profile business logic
└── docs/
    └── bigquery_schema.sql         # BigQuery schema + queries
```

---

## 📦 Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Cloud account (for BigQuery & GCS)
- Firebase project (for OAuth)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Edit `.env`** with:
```env
# API Keys
OPENAI_API_KEY=your_openai_api_key

# Database
BIGQUERY_PROJECT_ID=your-gcp-project-id
BIGQUERY_DATASET=legalai
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Storage (Avatar uploads)
GCS_BUCKET=legalai-avatars
GCS_REGION=us-central1

# OAuth (for backend verification)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MS_TENANT=common

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

**Create BigQuery tables**:
```bash
# Run the SQL schema file
bq query --use_legacy_sql=false < docs/bigquery_schema.sql
```

**Start backend**:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Update environment config
# Edit src/environments/environment.ts
```

**Edit `src/environments/environment.ts`**:
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
  
  // OAuth Client IDs (public, safe to expose)
  googleClientId: 'your-google-client-id.apps.googleusercontent.com',
  microsoftClientId: 'your-microsoft-client-id',
  
  // Feature flags
  enableMultiAccount: false,
  enableLawyerVerification: true
};
```

**Start frontend**:
```bash
npm start
# Opens at http://localhost:4200
```

### 3. Google Cloud Setup

#### BigQuery
1. Create dataset: `legalai`
2. Run schema SQL from `backend/docs/bigquery_schema.sql`
3. Grant service account permissions: `BigQuery Data Editor`, `BigQuery Job User`

#### Cloud Storage (Avatar uploads)
1. Create bucket: `legalai-avatars`
2. Set bucket permissions: `Storage Object Admin` for service account
3. Configure CORS:
```json
[
  {
    "origin": ["http://localhost:4200", "https://app.legid.ai"],
    "method": ["GET", "PUT", "POST"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
```

#### Firebase (OAuth)
1. Create Firebase project
2. Enable Google and Microsoft auth providers
3. Add OAuth redirect URIs:
   - Dev: `http://localhost:4200/auth/callback/google`
   - Prod: `https://app.legid.ai/auth/callback/google`

### 4. Provision First User

Insert a user into BigQuery:
```sql
INSERT INTO `legalai.identity_users` (user_id, auth_provider, auth_uid, email, role, lawyer_status, is_provisioned, env, created_at, updated_at)
VALUES (
  GENERATE_UUID(),
  'google',
  'google-oauth-user-id',
  'your-email@example.com',
  'admin',
  'not_applicable',
  TRUE,
  'dev',
  CURRENT_TIMESTAMP(),
  CURRENT_TIMESTAMP()
);
```

---

## 🔒 Security Features

1. **Session Management**
   - JWT tokens with expiration
   - HttpOnly cookies in production
   - Refresh token rotation
   - Multi-device session tracking

2. **Access Control**
   - Provisioning check on all protected routes
   - Role-based permissions
   - Lawyer verification system
   - Guard-protected frontend routes

3. **Data Protection**
   - All API endpoints require authentication
   - User data scoped to user_id
   - Signed URLs for avatar uploads (no direct write access)
   - CORS configured for known origins only

4. **Input Validation**
   - Username format validation (frontend + backend)
   - File type and size validation for avatars
   - Sanitized inputs before database writes

---

## 🧪 Testing

### Test User Flow

1. **Login** → redirected to `/login`
2. **Authenticate** with Google/Microsoft/Email
3. **Provisioning Check**:
   - If `is_provisioned=false` → `/not-provisioned` page
   - User can submit access request
4. **First-Time Setup** (if needed) → `/setup` wizard
5. **Chat Interface** → `/chat` (main app)
6. **Profile Menu**:
   - Click avatar in bottom-left
   - Test all menu items
   - Open Edit Profile modal
7. **Personalization**:
   - Navigate to `/personalization`
   - Change theme, font, preferences
   - Verify auto-save
8. **Settings**:
   - Navigate to `/settings`
   - Update profile, consent
   - Test "Logout all devices"
9. **Help**:
   - Navigate to `/help`
   - Test all tabs
   - Submit bug report

### API Testing

Use the backend API docs at `http://localhost:8000/docs`:

```bash
# Test endpoints with cURL
curl -X GET "http://localhost:8000/api/me" \
  -H "Authorization: Bearer YOUR_TOKEN"

curl -X GET "http://localhost:8000/api/profile/check-username/testuser" \
  -H "Authorization: Bearer YOUR_TOKEN"

curl -X PUT "http://localhost:8000/api/profile" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "John Doe",
    "username": "johndoe",
    "phone": "+1234567890"
  }'
```

---

## 📋 Environment Variables Summary

### Backend Required:
- `OPENAI_API_KEY`
- `BIGQUERY_PROJECT_ID`
- `BIGQUERY_DATASET`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `GCS_BUCKET`
- `JWT_SECRET_KEY`
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `MICROSOFT_CLIENT_ID` / `MICROSOFT_CLIENT_SECRET`

### Frontend Required:
- `apiUrl` (environment.ts)
- `googleClientId` (public OAuth client ID)
- `microsoftClientId` (public OAuth client ID)

---

## 🚀 Deployment

### Production Checklist

1. **Backend**:
   - Set `DEBUG=False`
   - Use production-grade secret for `JWT_SECRET_KEY`
   - Configure HTTPS
   - Set proper CORS origins
   - Enable rate limiting
   - Set up monitoring (Cloud Logging)

2. **Frontend**:
   - Build: `npm run build`
   - Deploy to Cloud Run / Firebase Hosting / Vercel
   - Update `environment.prod.ts` with production API URL
   - Configure OAuth redirect URIs for production domain

3. **Database**:
   - Review BigQuery permissions
   - Set up scheduled queries for cleanup
   - Enable audit logs
   - Implement backup strategy

4. **Storage**:
   - Review GCS bucket permissions
   - Enable versioning
   - Configure lifecycle policies for old avatars

---

## 📝 Notes

- **Username uniqueness**: Case-insensitive (uses `LOWER()` in queries)
- **Avatar storage**: Stored in GCS with signed URL access
- **Preferences**: Stored as JSON string in `preferences_json` field
- **Multi-account support**: Framework in place, disabled by default
- **Lawyer verification**: Manual approval process (admin dashboard required)
- **Session duration**: 24 hours (configurable via `JWT_EXPIRATION_HOURS`)

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Not provisioned" error even though user exists
- **Solution**: Check `is_provisioned` field in BigQuery `identity_users` table
- Ensure `env` field matches (dev/prod)

**Issue**: Avatar upload fails
- **Solution**: 
  - Verify GCS bucket permissions
  - Check CORS configuration
  - Ensure signed URL endpoint is working

**Issue**: Username shows "already taken" for unique username
- **Solution**: 
  - Check for case-insensitive duplicates
  - Clear any test data from `user_profiles` table

**Issue**: Preferences not saving
- **Solution**:
  - Check browser console for errors
  - Verify backend endpoint `/api/profile/preferences` is working
  - Check `preferences_json` field in database

---

## 👥 Support

For issues or questions:
- Backend API: Check logs at `backend/backend_detailed.log`
- Frontend: Open browser DevTools console
- Database: Query BigQuery tables directly
- OAuth: Check Firebase Auth dashboard

---

## 📜 License

This system is proprietary to LEGID/LegalAI. All rights reserved.

---

**Implementation Date**: January 2026  
**Version**: 2.1.0  
**Author**: LegalAI Development Team
