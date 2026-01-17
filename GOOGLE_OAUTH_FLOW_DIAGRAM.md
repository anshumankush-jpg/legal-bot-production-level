# Google OAuth 2.0 Flow - LEGID

## 🔄 Authentication Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GOOGLE OAUTH 2.0 FLOW                           │
└─────────────────────────────────────────────────────────────────────────┘

   USER                 FRONTEND                BACKEND              GOOGLE
    │                      │                       │                    │
    │  1. Opens App        │                       │                    │
    ├──────────────────────>                       │                    │
    │                      │                       │                    │
    │  2. Shows Login      │                       │                    │
    <──────────────────────┤                       │                    │
    │                      │                       │                    │
    │  3. Click "Sign in   │                       │                    │
    │     with Google"     │                       │                    │
    ├──────────────────────>                       │                    │
    │                      │                       │                    │
    │                      │  4. Redirect to       │                    │
    │                      │     /auth/google/login│                    │
    │                      ├───────────────────────>                    │
    │                      │                       │                    │
    │                      │  5. Generate Auth URL │                    │
    │                      │     with Client ID    │                    │
    │                      <───────────────────────┤                    │
    │                      │                       │                    │
    │                      │  6. Redirect to Google│                    │
    │                      │     OAuth Consent     │                    │
    │                      ├───────────────────────┼────────────────────>
    │                      │                       │                    │
    │  7. Google Login     │                       │                    │
    │     & Consent        │                       │                    │
    ├──────────────────────┼───────────────────────┼────────────────────>
    │                      │                       │                    │
    │  8. User Approves    │                       │                    │
    <──────────────────────┼───────────────────────┼────────────────────┤
    │                      │                       │                    │
    │                      │  9. Callback with code│                    │
    │                      <───────────────────────┼────────────────────┤
    │                      │                       │                    │
    │                      │ 10. Send code to      │                    │
    │                      │     /auth/google/     │                    │
    │                      │     callback          │                    │
    │                      ├───────────────────────>                    │
    │                      │                       │                    │
    │                      │                       │ 11. Exchange code  │
    │                      │                       │     for token      │
    │                      │                       ├────────────────────>
    │                      │                       │                    │
    │                      │                       │ 12. Access Token + │
    │                      │                       │     Refresh Token  │
    │                      │                       <────────────────────┤
    │                      │                       │                    │
    │                      │                       │ 13. Get User Info  │
    │                      │                       ├────────────────────>
    │                      │                       │                    │
    │                      │                       │ 14. User Profile   │
    │                      │                       <────────────────────┤
    │                      │                       │                    │
    │                      │ 15. Create JWT Token  │                    │
    │                      │     Sign with Secret  │                    │
    │                      │                       │                    │
    │                      │ 16. Redirect to       │                    │
    │                      │     frontend with JWT │                    │
    │                      <───────────────────────┤                    │
    │                      │                       │                    │
    │ 17. Save JWT in      │                       │                    │
    │     localStorage     │                       │                    │
    <──────────────────────┤                       │                    │
    │                      │                       │                    │
    │ 18. Show Main App    │                       │                    │
    <──────────────────────┤                       │                    │
    │                      │                       │                    │
    │ 19. Use App          │                       │                    │
    │     (JWT in headers) │                       │                    │
    ├──────────────────────>                       │                    │
    │                      │                       │                    │
    │                      │ 20. API Request with  │                    │
    │                      │     Authorization:    │                    │
    │                      │     Bearer {JWT}      │                    │
    │                      ├───────────────────────>                    │
    │                      │                       │                    │
    │                      │ 21. Verify JWT        │                    │
    │                      │     Decode & Check    │                    │
    │                      │                       │                    │
    │                      │ 22. API Response      │                    │
    │                      <───────────────────────┤                    │
    │                      │                       │                    │
    │ 23. Display Response │                       │                    │
    <──────────────────────┤                       │                    │
    │                      │                       │                    │

```

---

## 🔐 Security Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SECURITY LAYERS                                 │
└─────────────────────────────────────────────────────────────────────────┘

1. OAUTH 2.0 AUTHORIZATION CODE FLOW
   ├── State Parameter (CSRF Protection)
   ├── Secure Authorization Code Exchange
   └── Short-lived Authorization Codes

2. JWT TOKEN MANAGEMENT
   ├── Signed with Secret Key (HS256)
   ├── Expiration Time (24 hours default)
   ├── Contains User Claims (email, name, sub)
   └── Stateless Authentication

3. HTTPS READY
   ├── Works with SSL/TLS in Production
   ├── Secure Cookie Options Available
   └── Token Transmission via HTTPS

4. ENVIRONMENT VARIABLES
   ├── Credentials Never Hardcoded
   ├── Separate Dev/Prod Configuration
   └── .env Files Excluded from Git

5. CORS CONFIGURATION
   ├── Configured Origins Only
   ├── Credentials Allowed
   └── Specific Methods/Headers
```

---

## 📦 Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      BACKEND ARCHITECTURE                               │
└─────────────────────────────────────────────────────────────────────────┘

backend/
├── app/
│   ├── main.py                      [FastAPI Application]
│   │   ├── CORS Middleware
│   │   ├── Auth Router Registration
│   │   └── API Routes
│   │
│   └── auth/                        [Authentication Module]
│       ├── __init__.py
│       ├── google_oauth.py          [OAuth Handler]
│       │   ├── GoogleOAuthHandler
│       │   │   ├── get_authorization_url()
│       │   │   ├── exchange_code_for_token()
│       │   │   ├── get_user_info()
│       │   │   ├── create_jwt_token()
│       │   │   └── verify_jwt_token()
│       │   │
│       │   └── GoogleUserInfo (Pydantic Model)
│       │
│       └── routes.py                [API Endpoints]
│           ├── GET  /auth/google/login
│           ├── GET  /auth/google/callback
│           ├── POST /auth/google/token
│           ├── GET  /auth/verify
│           ├── POST /auth/logout
│           └── GET  /auth/config
│
├── .env                             [Environment Variables]
│   ├── GOOGLE_CLIENT_ID
│   ├── GOOGLE_CLIENT_SECRET
│   ├── GOOGLE_REDIRECT_URI
│   ├── JWT_SECRET_KEY
│   └── JWT_EXPIRATION_MINUTES
│
└── requirements.txt                 [Dependencies]
    ├── fastapi
    ├── httpx (OAuth HTTP requests)
    ├── PyJWT (JWT handling)
    └── python-dotenv
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────┘

frontend/
└── legid-with-google-auth.html
    │
    ├── [LOGIN PAGE]
    │   ├── Google Sign-In Button
    │   ├── OAuth Flow Initiation
    │   └── Beautiful UI
    │
    ├── [MAIN APPLICATION]
    │   ├── Chat Interface
    │   ├── User Profile Display
    │   ├── Authenticated API Requests
    │   └── Logout Functionality
    │
    └── [JAVASCRIPT]
        ├── Authentication Functions
        │   ├── checkAuthStatus()
        │   ├── handleGoogleLogin()
        │   ├── verifyToken()
        │   ├── handleLogout()
        │   └── updateUserInfo()
        │
        ├── Chat Functions
        │   ├── sendMessage()
        │   ├── createNewChat()
        │   └── autoResize()
        │
        └── State Management
            ├── localStorage (authToken)
            ├── currentUser (object)
            └── authToken (string)
```

---

## 🔑 Token Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         JWT TOKEN STRUCTURE                             │
└─────────────────────────────────────────────────────────────────────────┘

HEADER
{
  "alg": "HS256",        // Algorithm
  "typ": "JWT"           // Type
}

PAYLOAD
{
  "sub": "123456789",              // Google User ID
  "email": "user@example.com",     // Email Address
  "name": "John Doe",              // Full Name
  "picture": "https://...",        // Profile Picture URL
  "email_verified": true,          // Email Verification Status
  "iat": 1642234567,               // Issued At (timestamp)
  "exp": 1642320967                // Expiration (timestamp)
}

SIGNATURE
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  JWT_SECRET_KEY
)
```

---

## 🌐 API Request Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATED API REQUEST                            │
└─────────────────────────────────────────────────────────────────────────┘

Frontend → Backend
─────────────────────
GET /api/legal-query
Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  Content-Type: application/json

Backend Processing
──────────────────
1. Extract JWT from Authorization header
2. Verify JWT signature with JWT_SECRET_KEY
3. Check expiration time
4. Extract user information from payload
5. Process request with user context
6. Return response

Backend → Frontend
─────────────────────
200 OK
{
  "response": "Legal information...",
  "user": "user@example.com"
}
```

---

## 📊 Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA FLOW                                     │
└─────────────────────────────────────────────────────────────────────────┘

Google User Data → Backend → Frontend → localStorage
────────────────────────────────────────────────────

1. Google OAuth Response:
   {
     "sub": "123456789",
     "email": "user@example.com",
     "name": "John Doe",
     "picture": "https://...",
     "email_verified": true
   }

2. Backend Creates JWT:
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0...

3. Frontend Receives Token:
   - URL Parameter: ?token=eyJhbGci...
   - Parsed by JavaScript
   - Stored in localStorage

4. Stored in Browser:
   localStorage:
     authToken: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
     userEmail: user@example.com
     userName: John Doe
     userPicture: https://...

5. Used in Requests:
   All API requests include:
     Authorization: Bearer {authToken}
```

---

## 🚦 Error Handling

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ERROR SCENARIOS                                 │
└─────────────────────────────────────────────────────────────────────────┘

1. INVALID CREDENTIALS
   ├── Missing GOOGLE_CLIENT_ID
   ├── Invalid GOOGLE_CLIENT_SECRET
   └── Response: 500 Internal Server Error

2. OAUTH ERRORS
   ├── User Denies Consent → Redirect with error parameter
   ├── Invalid Authorization Code → 400 Bad Request
   └── Network Error → 500 Internal Server Error

3. JWT ERRORS
   ├── Expired Token → 401 Unauthorized
   ├── Invalid Signature → 401 Unauthorized
   └── Malformed Token → 401 Unauthorized

4. REDIRECT URI MISMATCH
   ├── Google OAuth Error
   └── Fix: Update Google Cloud Console

5. CORS ERRORS
   ├── Frontend Origin Not Allowed
   └── Fix: Update backend CORS configuration
```

---

## ✅ Deployment Checklist

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PRODUCTION DEPLOYMENT                              │
└─────────────────────────────────────────────────────────────────────────┘

□ Environment Variables
  □ Generate secure JWT_SECRET_KEY
  □ Update GOOGLE_REDIRECT_URI to production URL
  □ Update FRONTEND_URL to production URL
  □ Set LOG_LEVEL to INFO or WARNING

□ Google Cloud Console
  □ Add production redirect URI
  □ Add production JavaScript origins
  □ Enable APIs for production project

□ Backend Security
  □ Enable HTTPS
  □ Update CORS to specific origins
  □ Add rate limiting
  □ Implement token refresh
  □ Add logging and monitoring

□ Frontend Security
  □ Use HTTPS
  □ Consider httpOnly cookies instead of localStorage
  □ Implement CSRF protection
  □ Add security headers

□ Testing
  □ Test complete OAuth flow
  □ Test token expiration
  □ Test error scenarios
  □ Load testing
  □ Security audit
```

---

This diagram provides a complete visual reference for the Google OAuth 2.0 integration in your LEGID application!
