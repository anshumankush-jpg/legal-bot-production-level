# PLAZA-AI Legal Assistant - Quick Start Guide

## System Status

✅ **Backend**: Running on http://localhost:8000
✅ **Frontend**: Running on http://localhost:4201
✅ **Law Type Selector**: Integrated
✅ **Data Sources**: 15 official sources configured
✅ **Daily Updater**: Ready to start

## What's New

### 1. Law Type Selection System
After onboarding, you'll now see a **professional law type selector** where you:
1. Choose a law category (e.g., "Family Law", "Traffic Law")
2. Select a specific legal matter (e.g., "Child Support", "Careless Driving")
3. Confirm your jurisdiction

### 2. Jurisdiction-Based Filtering
All responses are now filtered by:
- Your country (Canada/USA)
- Your province/state (Ontario, Quebec, etc.)
- Your selected law type
- Applicable jurisdiction level (Federal/Provincial/Municipal)

### 3. Official Data Sources
Every response includes clickable links to:
- CanLII (Canadian Legal Information Institute)
- Court websites
- Government legislation databases
- Official legal resources

### 4. Professional Interface
- **No emojis** - clean, professional appearance
- Clear labels and descriptions
- Readable text
- Modern design

## How to Use

### First Time Setup

1. **Complete Onboarding**
   - Select your language
   - Choose your country
   - Select your province/state

2. **Select Law Type**
   - Browse 12 law categories
   - Choose your specific legal matter
   - Confirm jurisdiction

3. **Start Chatting**
   - Ask legal questions
   - Get jurisdiction-specific answers
   - View official sources

### Changing Your Settings

**To Change Law Type:**
- Click "Change Law Type" button in the header
- Select a new category and law type

**To Change Location/Language:**
- Click "Settings" button in the header
- Complete onboarding again with new preferences

### Using the Chat Interface

**Ask Questions:**
```
"What are the penalties for careless driving?"
"How do I file for divorce in Ontario?"
"What are my rights as an employee?"
```

**Upload Documents:**
- Click the "+" button
- Choose file type (PDF, DOC, IMG, TXT)
- Upload your legal document

**Use Andy (Text-to-Speech):**
- Click "Andy ON" to enable auto-read
- Click speaker icon on any message to read it
- Click "Stop" to halt speech

## Available Law Types

### Business Law (12 types)
- Business Formation and Organization
- Business Litigation
- Contracts
- Intellectual Property
- And more...

### Criminal Law (7 types)
- Assault and Violent Crimes
- Drug Offences
- Fraud and White Collar Crimes
- Impaired Driving (DUI)
- And more...

### Employment Law (6 types)
- Employees Rights
- Employers Rights
- Wrongful Dismissal
- Employment Contracts
- And more...

### Family Law (9 types)
- Child Support
- Custody and Access
- Divorce
- Spousal Support
- And more...

### Traffic Law (8 types)
- Speeding Tickets
- Careless Driving
- Stunt Driving
- Drive Suspended
- And more...

### Real Estate Law (4 types)
- Commercial Real Estate
- Residential Real Estate
- Real Estate Litigation
- And more...

### Tax Law (6 types)
- Business Tax
- Personal Tax
- Corporate Tax
- Tax Disputes
- And more...

### Litigation & ADR (7 types)
- Alternative Dispute Resolution
- Corporate Commercial Litigation
- Mediation
- Personal Injury
- And more...

### Wills, Estates, and Trusts (8 types)
- Estate Administration
- Powers of Attorney
- Wills & Estate Planning
- Probate
- And more...

### Health Law (5 types)
- Medical Malpractice
- Healthcare Compliance
- Mental Health Law
- And more...

### Entertainment and Media Law (5 types)
- Copyright
- Trademark
- Media Contracts
- And more...

### Not-For-Profit & Charities (4 types)
- Charity Registration
- Governance
- Compliance
- And more...

## Data Sources

### Canada - Federal
- ✓ CanLII (API available)
- ✓ Department of Justice Canada
- ✓ Supreme Court of Canada

### Canada - Ontario
- ✓ Ontario Court of Appeal
- ✓ Ontario Superior Court of Justice
- ✓ Ontario Regulations
- ✓ Law Society of Ontario

### Canada - Other Provinces
- ✓ Quebec (SOQUIJ, Publications du Québec)
- ✓ British Columbia (BC Laws)
- ✓ Alberta (Alberta Queen's Printer)

### USA - Federal
- ✓ PACER (API available)
- ✓ Supreme Court of the United States
- ✓ Cornell Legal Information Institute
- ✓ GovInfo (API available)

## Daily Data Updates

### Automatic Updates
The system automatically updates legal data daily at 2:00 AM, fetching:
- Recent case law
- Legislation changes
- Case summaries with citations

### Manual Update
To run updates manually:
```bash
cd backend
python legal_data_scraper.py
```

### Start Daily Scheduler
To enable automatic daily updates:
```bash
# Option 1: Use batch file
START_DATA_UPDATER.bat

# Option 2: Run directly
cd backend
python daily_update_scheduler.py
```

## Troubleshooting

### Frontend Not Loading
1. Check if frontend is running: http://localhost:4201
2. Check terminal for errors
3. Restart: `cd frontend; npm start`

### Backend Not Responding
1. Check if backend is running: http://localhost:8000
2. Check terminal for errors
3. Restart: `cd backend; python -m uvicorn app.main:app --reload`

### Law Selector Not Showing
1. Clear browser cache
2. Clear localStorage: Open browser console, run `localStorage.clear()`
3. Refresh page

### No Responses
1. Check backend is running
2. Check browser console for errors
3. Verify API URL in `frontend/src/environments/environment.ts`

## Testing the System

Run the test suite:
```bash
cd backend
python test_data_system.py
```

Expected output:
```
✓ 15 official legal sources configured
✓ 11 Canada sources
✓ 4 USA sources
✓ 13 free sources
✓ 3 sources with API access
✓ 21 law categories
```

## URLs

- **Frontend**: http://localhost:4201
- **Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Features

✓ **Jurisdiction-specific filtering**
✓ **80+ law types across 12 categories**
✓ **15 official data sources (13 free)**
✓ **Automated daily updates**
✓ **Professional UI (no emojis)**
✓ **Real case studies with citations**
✓ **Clickable, verifiable sources**
✓ **Text-to-speech (Andy)**
✓ **Document upload**
✓ **Chat history saving**

## Important Notes

1. **This is general legal information, NOT legal advice**
2. **Always consult a licensed legal professional for your specific situation**
3. **Sources are provided for verification and further research**
4. **Data is updated daily but may not reflect the very latest changes**

## Support

For detailed documentation, see:
- `LEGAL_DATA_SYSTEM_README.md` - Complete system documentation
- `IMPLEMENTATION_SUMMARY.md` - What was built and how it works

For logs:
- Backend: Check uvicorn output
- Daily updates: `backend/legal_data_updates.log`
- Frontend: Check browser console

---

**Enjoy using PLAZA-AI Legal Assistant!**

Your jurisdiction-specific legal information system with professional appearance and official data sources.
