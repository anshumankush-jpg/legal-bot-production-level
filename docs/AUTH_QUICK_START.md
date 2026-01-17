# LegalAI Authentication - Quick Start Guide

## ✅ **What's Been Implemented (30%)**

I've built the **foundation** of your production-grade authentication system:

### **1. Database Schema** 
- ✅ BigQuery tables for user identity, lawyer applications, login events
- ✅ Optimized with partitioning and clustering
- ✅ RBAC permissions table
- ✅ Upsert (MERGE) strategies for idempotency
- **Location**: `docs/bigquery_schema.sql`

### **2. Backend Auth Services**
- ✅ Firebase Auth integration (Google, Microsoft, Email/Password)
- ✅ BigQuery identity client with upsert logic
- ✅ Authentication middleware for FastAPI
- ✅ Role-based dependencies (customer, lawyer, admin)
- **Files Created**:
  - `backend/app/auth/firebase_auth.py`
  - `backend/app/auth/bigquery_client.py`
  - `backend/app/middleware/auth_middleware.py`

---

## 🔧 **Setup Instructions**

### **Step 1: Install Backend Dependencies**

```bash
cd backend
pip install firebase-admin google-cloud-bigquery google-cloud-storage slowapi
```

### **Step 2: Setup Firebase**

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create new project: "LegalAI"
3. Enable Authentication:
   - Email/Password
   - Google
   - Microsoft (optional for now)
4. Download service account:
   - Project Settings → Service Accounts
   - Generate new private key → Save as `firebase-adminsdk.json`
5. Place in `backend/config/firebase-adminsdk.json`

### **Step 3: Setup BigQuery**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable BigQuery API
3. Create dataset:
   ```sql
   CREATE SCHEMA IF NOT EXISTS legalai;
   ```
4. Run the schema SQL:
   ```bash
   bq query --use_legacy_sql=false < docs/bigquery_schema.sql
   ```
5. Create service account:
   - IAM & Admin → Service Accounts
   - Create account with role: "BigQuery Admin"
   - Generate JSON key → Save as `bigquery-service-account.json`
6. Place in `backend/config/bigquery-service-account.json`

### **Step 4: Configure Environment Variables**

Create `backend/.env`:

```bash
# Firebase
FIREBASE_CREDENTIALS_PATH=./config/firebase-adminsdk.json
FIREBASE_PROJECT_ID=your-firebase-project-id

# BigQuery
GCP_PROJECT_ID=your-gcp-project-id
BIGQUERY_DATASET=legalai
GOOGLE_APPLICATION_CREDENTIALS=./config/bigquery-service-account.json

# Application
ENVIRONMENT=dev
BASE_URL=http://localhost:4200
API_BASE_URL=http://localhost:8000

# Security
JWT_SECRET_KEY=your-super-secret-key-change-this
ALLOWED_ORIGINS=http://localhost:4200,http://localhost:4201

# Google Cloud Storage (for lawyer documents)
GCS_BUCKET_NAME=legalai-lawyer-documents
GCS_CREDENTIALS_PATH=./config/gcs-service-account.json
```

---

## 📁 **File Structure Created**

```
backend/
├── app/
│   ├── auth/
│   │   ├── __init__.py                ✅ Created
│   │   ├── firebase_auth.py           ✅ Created
│   │   └── bigquery_client.py         ✅ Created
│   ├── middleware/
│   │   └── auth_middleware.py         ✅ Created
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py                ⏳ TODO
│   │       ├── lawyer.py              ⏳ TODO
│   │       └── admin.py               ⏳ TODO
│   └── services/
│       └── storage_service.py         ⏳ TODO
└── config/                            📁 You create this
    ├── firebase-adminsdk.json         🔐 You add this
    ├── bigquery-service-account.json  🔐 You add this
    └── gcs-service-account.json       🔐 You add this

docs/
├── bigquery_schema.sql                ✅ Created
├── AUTH_IMPLEMENTATION_SUMMARY.md     ✅ Created
└── AUTH_QUICK_START.md                ✅ Created (this file)

frontend/
├── src/
│   ├── app/
│   │   ├── auth/                      ⏳ TODO
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── auth.service.ts
│   │   ├── lawyer/                    ⏳ TODO
│   │   │   ├── onboarding/
│   │   │   └── dashboard/
│   │   └── admin/                     ⏳ TODO
│   │       └── lawyers/
│   └── environments/
│       ├── environment.ts             🔧 You update this
│       └── environment.prod.ts        🔧 You update this
```

---

## 🚀 **How to Use the Auth System (Example)**

### **Backend Example** (FastAPI Route):

```python
from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import (
    get_current_user,
    get_verified_lawyer,
    get_current_admin
)

router = APIRouter()

# Public endpoint (no auth)
@router.get("/public/hello")
async def public_hello():
    return {"message": "Hello, public!"}

# Any authenticated user
@router.get("/auth/me")
async def get_me(user = Depends(get_current_user)):
    return {
        "user_id": user['user_id'],
        "email": user['email'],
        "role": user['role'],
        "lawyer_status": user.get('lawyer_status')
    }

# Only verified lawyers
@router.get("/tools/document-generator")
async def document_generator(lawyer = Depends(get_verified_lawyer)):
    return {"message": f"Welcome, verified lawyer {lawyer['email']}!"}

# Only admins
@router.get("/admin/stats")
async def admin_stats(admin = Depends(get_current_admin)):
    return {"message": "Admin-only data"}
```

### **Frontend Example** (Angular Service):

```typescript
// auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AngularFireAuth } from '@angular/fire/compat/auth';
import { GoogleAuthProvider, OAuthProvider } from 'firebase/auth';

@Injectable({ providedIn: 'root' })
export class AuthService {
  constructor(
    private http: HttpClient,
    private afAuth: AngularFireAuth
  ) {}

  // Google Sign-In
  async signInWithGoogle() {
    const provider = new GoogleAuthProvider();
    const credential = await this.afAuth.signInWithPopup(provider);
    const token = await credential.user?.getIdToken();
    
    // Send token to backend
    return this.http.post('/api/auth/register', {
      token,
      role: 'customer' // or 'lawyer'
    }).toPromise();
  }
  
  // Get current user
  async getCurrentUser() {
    const token = await this.afAuth.currentUser.then(u => u?.getIdToken());
    return this.http.get('/api/auth/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    }).toPromise();
  }
}
```

---

## 🔐 **Security Features Implemented**

1. ✅ **Firebase Auth**: Industry-standard authentication
2. ✅ **Role-Based Access**: Customer, Lawyer, Admin roles
3. ✅ **Status-Based Access**: Pending/Approved/Rejected for lawyers
4. ✅ **Token Verification**: Every request verified with Firebase
5. ✅ **BigQuery Audit Trail**: All logins logged
6. ✅ **Unique User IDs**: Stable UUIDs separate from auth provider IDs

---

## ⏳ **What Still Needs to Be Built (70%)**

### **High Priority**:
1. **FastAPI Auth Routes** (`POST /api/auth/register`, `GET /api/auth/me`)
2. **FastAPI Lawyer Routes** (`POST /api/lawyer/apply`)
3. **FastAPI Admin Routes** (`POST /api/admin/lawyer/{id}/approve`)
4. **Angular Auth Pages** (`/auth` login/register with ChatGPT styling)
5. **Angular Lawyer Onboarding** (`/lawyer/onboarding` form)
6. **File Upload Service** (Google Cloud Storage for documents)

### **Medium Priority**:
7. **Rate Limiting** (10 req/min on auth endpoints)
8. **Security Headers** (CSP, HSTS)
9. **Email Notifications** (application approved/rejected)
10. **Admin Review Panel** (`/admin/lawyers`)

### **Lower Priority**:
11. **Unit Tests** (auth flow, RBAC)
12. **Integration Tests** (E2E scenarios)
13. **Password Reset Flow**
14. **OAuth Redirect Fix** (dev vs prod)

---

## 💡 **Next Steps**

**Would you like me to continue implementing?**

I recommend we proceed in this order:

1. ✅ **Done**: BigQuery schema, Firebase service, Auth middleware
2. **Next**: FastAPI auth routes (`/api/auth/*`)
3. **Then**: Angular auth pages with ChatGPT-style UI
4. **Then**: Lawyer onboarding flow
5. **Finally**: Admin review panel

**Total estimated completion time**: 
- Core auth system: 4-6 hours of coding
- Full system with all features: 12-15 hours
- Testing & documentation: 3-4 hours

**I'm about 30% done. Shall I continue with the FastAPI routes?**

Let me know if you'd like me to:
- A) Continue implementing the remaining 70%
- B) Focus on a specific part (e.g., just the auth pages)
- C) Provide more detailed examples/documentation
- D) Test what's been built so far
