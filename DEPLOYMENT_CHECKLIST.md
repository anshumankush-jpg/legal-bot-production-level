# Deployment Checklist - Profile System

## Pre-Deployment Checklist

Use this checklist to ensure everything is configured before deploying to production.

---

## ✅ Backend Configuration

### Environment Variables
- [ ] `OPENAI_API_KEY` set
- [ ] `BIGQUERY_PROJECT_ID` set to production project
- [ ] `BIGQUERY_DATASET` set to `legalai`
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` points to production service account
- [ ] `GCS_BUCKET` created and configured (e.g., `legalai-avatars`)
- [ ] `JWT_SECRET_KEY` is strong (min 32 characters, random)
- [ ] `JWT_ALGORITHM` set to `HS256`
- [ ] `JWT_EXPIRATION_HOURS` set (default: 24)
- [ ] `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` set (production OAuth app)
- [ ] `MICROSOFT_CLIENT_ID` and `MICROSOFT_CLIENT_SECRET` set (production OAuth app)
- [ ] `MS_TENANT` set (usually `common`)
- [ ] `HOST` set to `0.0.0.0` (for Cloud Run) or specific IP
- [ ] `PORT` set (default: 8000)
- [ ] `DEBUG` set to `False`

### Google Cloud Setup

#### BigQuery
- [ ] Dataset `legalai` created in production project
- [ ] Tables created using `backend/docs/bigquery_schema.sql`:
  - [ ] `identity_users`
  - [ ] `user_profiles`
  - [ ] `user_consent`
  - [ ] `access_requests`
  - [ ] `conversations` (optional)
  - [ ] `messages` (optional)
- [ ] Service account has `BigQuery Data Editor` role
- [ ] Service account has `BigQuery Job User` role
- [ ] First admin user provisioned (with `is_provisioned=TRUE`)

#### Cloud Storage (GCS)
- [ ] Bucket `legalai-avatars` created
- [ ] Bucket region matches backend region
- [ ] Service account has `Storage Object Admin` role
- [ ] CORS configured on bucket:
```json
[
  {
    "origin": ["https://app.legid.ai"],
    "method": ["GET", "PUT", "POST"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
```
- [ ] Lifecycle policy set (optional, for old avatars cleanup)

#### Firebase (OAuth)
- [ ] Firebase project created
- [ ] Google Sign-In enabled
- [ ] Microsoft Sign-In enabled
- [ ] OAuth redirect URIs configured:
  - [ ] `https://app.legid.ai/auth/callback/google`
  - [ ] `https://app.legid.ai/auth/callback/microsoft`
- [ ] Authorized domains include production domain

#### Cloud Run (if deploying to Cloud Run)
- [ ] Backend service created
- [ ] Environment variables set in Cloud Run service
- [ ] Service account attached to Cloud Run service
- [ ] Min/max instances configured
- [ ] Memory and CPU allocated (recommended: 1 CPU, 2GB RAM)
- [ ] Timeout set (default: 300s)
- [ ] Allow unauthenticated (if public) or configure IAM

---

## ✅ Frontend Configuration

### Environment Variables
Update `frontend/src/environments/environment.prod.ts`:
- [ ] `production` set to `true`
- [ ] `apiUrl` set to production backend URL (e.g., `https://api.legid.ai`)
- [ ] `googleClientId` set to production OAuth client ID (public, safe to expose)
- [ ] `microsoftClientId` set to production OAuth client ID
- [ ] `enableMultiAccount` set (true/false)
- [ ] `enableLawyerVerification` set (true/false)

### Build
- [ ] Run production build: `npm run build`
- [ ] Verify `dist/` folder created
- [ ] Test built files locally: `npm run preview`

### Hosting (choose one)

#### Option 1: Cloud Run
- [ ] Dockerfile exists and tested
- [ ] Docker image built and pushed to GCR
- [ ] Cloud Run service created for frontend
- [ ] Custom domain configured
- [ ] HTTPS enforced

#### Option 2: Firebase Hosting
- [ ] Firebase project initialized
- [ ] `firebase.json` configured
- [ ] Deploy: `firebase deploy --only hosting`
- [ ] Custom domain configured

#### Option 3: Vercel/Netlify
- [ ] Repository connected
- [ ] Build command: `npm run build`
- [ ] Output directory: `dist/`
- [ ] Environment variables set
- [ ] Custom domain configured

---

## ✅ Security

### Backend
- [ ] CORS configured with production origins only (no `*`)
- [ ] Rate limiting enabled (consider using Cloud Armor or API Gateway)
- [ ] HTTPS enforced (redirect HTTP to HTTPS)
- [ ] JWT secret is strong and never committed to git
- [ ] Sensitive data encrypted at rest (GCS/BigQuery default encryption)
- [ ] Audit logging enabled (Cloud Logging)
- [ ] Error messages don't expose sensitive info

### Frontend
- [ ] No API keys or secrets in frontend code
- [ ] OAuth redirect URIs whitelist only production domain
- [ ] HTTPS enforced
- [ ] Content Security Policy (CSP) headers set
- [ ] XSS protection headers set

### Database
- [ ] Service account has minimal required permissions
- [ ] BigQuery dataset access restricted
- [ ] Scheduled queries for cleanup (optional, e.g., old access_requests)
- [ ] Backup strategy in place

---

## ✅ Testing

### Functionality
- [ ] Login with Google works
- [ ] Login with Microsoft works
- [ ] Provisioned users can access app
- [ ] Non-provisioned users see "Not Provisioned" page
- [ ] Access request form submits and stores in database
- [ ] Profile menu opens and all items work
- [ ] Edit profile modal opens and saves correctly
- [ ] Avatar upload works (upload to GCS)
- [ ] Username validation works (format + uniqueness)
- [ ] Personalization settings save and apply
- [ ] Theme changes persist after refresh
- [ ] Settings page displays correct user info
- [ ] Cookie consent toggles save
- [ ] Logout works and clears session
- [ ] Logout all devices works
- [ ] Help pages all render correctly
- [ ] Role-based access works (lawyer-only routes blocked for non-lawyers)

### Performance
- [ ] Backend API responds within acceptable time (<500ms)
- [ ] Frontend loads within 3 seconds
- [ ] Avatar uploads complete within 10 seconds
- [ ] No memory leaks in long-running sessions
- [ ] Database queries optimized (use EXPLAIN in BigQuery)

### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Android)

---

## ✅ Monitoring & Logging

### Cloud Logging
- [ ] Backend logs streaming to Cloud Logging
- [ ] Frontend errors tracked (consider using Sentry or similar)
- [ ] Log-based alerts configured for errors
- [ ] Log retention policy set

### Monitoring
- [ ] Uptime checks configured (Cloud Monitoring)
- [ ] Alerts for:
  - [ ] Backend down (HTTP 5xx errors)
  - [ ] High error rate (>5% of requests)
  - [ ] High latency (>1s response time)
  - [ ] BigQuery quota exceeded
  - [ ] GCS quota exceeded
- [ ] Dashboard created for key metrics

---

## ✅ Documentation

- [ ] README updated with production setup instructions
- [ ] API documentation available (FastAPI `/docs`)
- [ ] Environment variables documented
- [ ] Database schema documented (`backend/docs/bigquery_schema.sql`)
- [ ] Deployment process documented
- [ ] Troubleshooting guide created

---

## ✅ User Onboarding

### First Users
- [ ] Admin user provisioned in `identity_users` table
- [ ] Test user accounts created (customer, lawyer)
- [ ] Lawyer verification process documented
- [ ] Welcome email template created (optional)

### Support
- [ ] Support email configured (e.g., support@legid.ai)
- [ ] Help center populated with FAQs
- [ ] Bug report form tested and working
- [ ] Contact information updated in app

---

## ✅ Legal & Compliance

- [ ] Terms of Service published and linked
- [ ] Privacy Policy published and linked
- [ ] Cookie Policy published and linked
- [ ] Acceptable Use Policy published and linked
- [ ] GDPR compliance checked (if serving EU users)
- [ ] Data retention policy defined
- [ ] User data deletion process documented

---

## ✅ Backup & Disaster Recovery

- [ ] BigQuery backups scheduled (automated by GCP)
- [ ] GCS versioning enabled for avatars
- [ ] Database restore procedure documented
- [ ] Rollback plan documented
- [ ] Disaster recovery plan created

---

## ✅ Post-Deployment

### Immediate (within 24 hours)
- [ ] Monitor logs for errors
- [ ] Test critical user flows
- [ ] Verify analytics tracking (if enabled)
- [ ] Check uptime and performance
- [ ] Confirm emails are being sent (if applicable)

### Short-term (within 1 week)
- [ ] Review user feedback
- [ ] Fix any critical bugs
- [ ] Monitor database growth
- [ ] Review performance metrics
- [ ] Update documentation based on issues found

### Ongoing
- [ ] Weekly review of logs and errors
- [ ] Monthly security audit
- [ ] Quarterly dependency updates
- [ ] Regular backups verification
- [ ] User feedback integration

---

## 🚨 Rollback Plan

If deployment fails or critical issues arise:

1. **Frontend**: Revert to previous deployment
   - Cloud Run: Deploy previous revision
   - Firebase: `firebase hosting:rollback`
   - Vercel/Netlify: Use dashboard to rollback

2. **Backend**: Rollback Cloud Run service to previous revision

3. **Database**: BigQuery changes are usually backwards compatible
   - If needed, restore from backup or delete new columns

4. **Notify users**: If downtime occurred, send status update

---

## ✅ Launch Day Checklist

1. [ ] All above items completed
2. [ ] Final smoke test in production
3. [ ] Team briefed on support process
4. [ ] Monitoring dashboards open
5. [ ] Support channels ready
6. [ ] Announcement ready (if applicable)
7. [ ] Rollback plan reviewed
8. [ ] On-call engineer assigned

---

## 📊 Success Metrics

After deployment, track:
- [ ] User sign-up rate
- [ ] Session duration
- [ ] Feature adoption (profile edits, personalization usage)
- [ ] Error rate (<1% target)
- [ ] Page load time (<3s target)
- [ ] API response time (<500ms target)
- [ ] User satisfaction (surveys)

---

## 🎉 Ready to Deploy!

When all checkboxes are complete, you're ready for production deployment.

**Good luck!** 🚀

---

**For questions or issues**: See `PROFILE_ACCOUNT_SYSTEM_COMPLETE.md` for detailed troubleshooting.
