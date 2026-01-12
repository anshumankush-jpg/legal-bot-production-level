# Legal Data Management System

## Overview

This system provides **jurisdiction-specific legal information** with **automated daily updates** from official legal sources. It filters responses based on:

- **Country** (Canada/USA)
- **Province/State** (Ontario, Quebec, BC, Alberta, etc.)
- **Law Type** (Criminal, Family, Employment, Traffic, etc.)
- **Specific Legal Matter** (e.g., "Wrongful Dismissal" under Employment Law)

## Key Features

### 1. Law Type Selection System
- **Professional interface** without emojis
- **12 major law categories** with 80+ specific law types
- **Jurisdiction-aware** - only shows applicable law types for user's location
- Based on real law firm structure (Mills & Mills LLP)

### 2. Automated Data Updates
- **Daily scraper** runs at 2:00 AM to fetch latest:
  - Case law from CanLII and court websites
  - Recent legislation updates
  - Case summaries with citations
- **Smart caching** - reduces API calls while keeping data fresh
- **Comprehensive logging** - track all updates and errors

### 3. Official Data Sources

#### Canada - Federal
- **CanLII** (Canadian Legal Information Institute) - Primary case law
- **Department of Justice Canada** - Federal legislation
- **Supreme Court of Canada** - Supreme Court decisions

#### Canada - Provincial
**Ontario:**
- Ontario Court of Appeal
- Ontario Superior Court of Justice
- Ontario Regulations
- Law Society of Ontario

**Quebec:**
- SOQUIJ
- Publications du Québec

**British Columbia:**
- BC Laws

**Alberta:**
- Alberta Queen's Printer

#### USA - Federal
- PACER - Federal court documents
- Supreme Court of the United States
- Cornell Legal Information Institute
- GovInfo - Federal government information

### 4. Jurisdiction-Based Filtering

Responses automatically filtered by:
```
User Location: Canada → Ontario
Law Category: Family Law
Law Type: Child Support
→ System returns only Ontario family law related to child support
```

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     USER INTERFACE                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Onboarding  │→ │ Law Selector │→ │ Chat Interface│  │
│  │   Wizard     │  │              │  │   (Filtered)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    BACKEND API                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  /api/artillery/chat                             │   │
│  │  • Accepts: law_category, law_type, jurisdiction │   │
│  │  • Filters: documents, case law, legislation     │   │
│  │  • Returns: jurisdiction-specific answers        │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              DATA MANAGEMENT LAYER                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Legal Data Scraper (legal_data_scraper.py)      │  │
│  │  • Fetches from official sources                 │  │
│  │  • Smart caching (24-hour cache duration)        │  │
│  │  • Structured data with citations                │  │
│  └──────────────────────────────────────────────────┘  │
│                           ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Daily Scheduler (daily_update_scheduler.py)     │  │
│  │  • Runs daily at 2:00 AM                         │  │
│  │  • Updates all jurisdictions                     │  │
│  │  • Comprehensive logging                         │  │
│  └──────────────────────────────────────────────────┘  │
│                           ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Data Sources Config (legal_data_sources.py)     │  │
│  │  • Official source URLs                          │  │
│  │  • API endpoints                                 │  │
│  │  • Search keywords by law type                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              EXTERNAL DATA SOURCES                       │
│  • CanLII API                                            │
│  • Court Websites                                        │
│  • Government Legal Databases                            │
│  • Official Legislation Repositories                     │
└─────────────────────────────────────────────────────────┘
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Key new dependencies:
- `schedule` - For daily automated updates
- `lxml` - For web scraping and data parsing

### 2. Start the Daily Update Scheduler

In a separate terminal:

```bash
cd backend
python daily_update_scheduler.py
```

This will:
- Run immediately on startup (optional)
- Schedule daily updates at 2:00 AM
- Log all activities to `legal_data_updates.log`

### 3. Start the Backend Server

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Start the Frontend

```bash
cd frontend
npm start
```

## Usage Flow

1. **User completes onboarding**
   - Selects language, country, province

2. **Law Type Selection**
   - Chooses law category (e.g., "Family Law")
   - Selects specific matter (e.g., "Child Support")
   - System confirms jurisdiction

3. **Chat Interface**
   - All responses filtered by jurisdiction and law type
   - Sources are clickable and verifiable
   - Professional appearance without emojis

## Law Categories

### Supported Categories:
1. **Business Law** (12 types)
2. **Criminal Law** (7 types)
3. **Employment Law** (6 types)
4. **Family Law** (9 types)
5. **Real Estate Law** (4 types)
6. **Traffic Law** (8 types)
7. **Tax Law** (6 types)
8. **Litigation & ADR** (7 types)
9. **Wills, Estates, and Trusts** (8 types)
10. **Health Law** (5 types)
11. **Entertainment and Media Law** (5 types)
12. **Not-For-Profit & Charities** (4 types)

## Data Sources

All data sourced from **official, verified legal databases**:

✓ **Free sources** where available
✓ **API integration** where provided
✓ **Daily updates** to ensure current information
✓ **Clickable citations** to original sources
✓ **Professional presentation** without emojis

## API Endpoints

### Chat Endpoint (Enhanced)

```http
POST /api/artillery/chat
Content-Type: application/json

{
  "message": "What are the penalties for careless driving?",
  "law_category": "Traffic Law",
  "law_type": "Careless Driving",
  "jurisdiction": "Ontario",
  "country": "CA",
  "province": "Ontario",
  "language": "en"
}
```

Response includes:
- Answer filtered by jurisdiction
- Relevant case law with citations
- Applicable legislation
- Official source links

## File Structure

```
backend/
├── legal_data_sources.py          # Data source configuration
├── legal_data_scraper.py           # Scraping and caching logic
├── daily_update_scheduler.py      # Automated updates
├── legal_data_cache/              # Cached data (auto-created)
│   ├── canlii_*.json
│   ├── legislation_*.json
│   └── summaries_*.json
└── legal_data_updates.log         # Update logs

frontend/
├── src/
│   ├── components/
│   │   ├── LawTypeSelector.jsx    # Law type selection interface
│   │   ├── LawTypeSelector.css
│   │   ├── ChatInterface.jsx      # Enhanced with filtering
│   │   └── OnboardingWizard.jsx
│   └── App.jsx                    # Main app with routing
```

## Maintenance

### View Update Logs

```bash
tail -f backend/legal_data_updates.log
```

### Force Manual Update

```bash
cd backend
python legal_data_scraper.py
```

### Clear Cache

```bash
rm -rf backend/legal_data_cache/*
```

## Future Enhancements

1. **API Integration**
   - Full CanLII API integration
   - PACER API for US federal courts
   - Real-time case notifications

2. **Advanced Features**
   - Case law similarity matching
   - Precedent analysis
   - Legislative change tracking
   - Automated legal summaries

3. **Additional Jurisdictions**
   - All Canadian provinces
   - US state courts
   - International law sources

## Support

For issues or questions:
- Check logs: `backend/legal_data_updates.log`
- Review cache: `backend/legal_data_cache/`
- Verify sources: Review `legal_data_sources.py`

## Legal Disclaimer

This system provides **general legal information** only. It is **not legal advice**. 
All information is sourced from official legal databases and updated daily, but users 
should always consult a licensed legal professional for advice specific to their situation.

Sources are provided for verification and further research.
