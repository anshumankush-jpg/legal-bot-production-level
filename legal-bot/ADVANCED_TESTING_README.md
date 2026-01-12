

# Advanced Legal Source Testing & Daily Updates System

## Overview

This comprehensive testing and update system verifies that your legal chatbot provides accurate sources, articles, and website references for different law types across multiple jurisdictions. It also includes an automated daily scraper to keep your legal database up-to-date.

---

## 📋 Table of Contents

1. [Test Suite Overview](#test-suite-overview)
2. [Test Cases (25 Questions)](#test-cases-25-questions)
3. [Test Results by Law Type](#test-results-by-law-type)
4. [Daily Update System](#daily-update-system)
5. [How to Run Tests](#how-to-run-tests)
6. [Understanding Test Results](#understanding-test-results)
7. [Daily Scraper Setup](#daily-scraper-setup)

---

## Test Suite Overview

### Files Included

1. **advanced_legal_source_test.py** - Main test suite with 25 comprehensive test cases
2. **legal_news_scraper.py** - Daily web scraper for legal updates
3. **daily_legal_updater.py** - Scheduler to run scraper daily at 2:00 AM
4. **ADVANCED_TESTING_README.md** - This documentation file

### What Gets Tested

For each question, the system verifies:
- ✅ **Sources** - Legal codes, acts, and statutes mentioned
- ✅ **Articles** - Specific sections and article numbers
- ✅ **Websites** - Official government and legal websites referenced
- ✅ **Citations** - Number and quality of citations provided
- ✅ **Answer Quality** - Relevance and completeness of the response

---

## Test Cases (25 Questions)

### 🇨🇦 Canada - Criminal Law (5 tests)

#### Test #1: Theft Under $5000
**Question:** "What is the penalty for theft under $5000 in Canada?"

**Expected Sources:**
- Criminal Code
- section 334
- theft
- summary conviction

**Expected Articles:**
- Section 334
- Section 322

**Expected Websites:**
- laws-lois.justice.gc.ca
- Criminal Code

**What the Chatbot Should Provide:**
- Reference to Criminal Code Section 334
- Explanation of summary conviction penalties
- Maximum penalties (fine and/or imprisonment)
- Link to official Justice Canada website

---

#### Test #2: Drug Possession
**Question:** "What are the penalties for drug possession in Canada?"

**Expected Sources:**
- Controlled Drugs and Substances Act
- CDSA
- possession

**Expected Articles:**
- Section 4
- Schedule

**Expected Websites:**
- laws-lois.justice.gc.ca
- CDSA

**What the Chatbot Should Provide:**
- Reference to CDSA Section 4
- Schedule classifications (I, II, III, etc.)
- Penalties based on drug schedule
- Link to official legislation

---

#### Test #3: Sexual Assault
**Question:** "What constitutes sexual assault under Canadian law?"

**Expected Sources:**
- Criminal Code
- section 271
- sexual assault

**Expected Articles:**
- Section 271
- Section 273

**Expected Websites:**
- Criminal Code
- justice.gc.ca

**What the Chatbot Should Provide:**
- Definition from Criminal Code Section 271
- Different levels of sexual assault (271, 272, 273)
- Penalties for each level
- Official government resources

---

#### Test #4: Robbery
**Question:** "What is the punishment for robbery in Canada?"

**Expected Sources:**
- Criminal Code
- section 344
- robbery
- indictable

**Expected Articles:**
- Section 343
- Section 344

**Expected Websites:**
- Criminal Code
- laws-lois.justice.gc.ca

**What the Chatbot Should Provide:**
- Criminal Code Section 343 (definition)
- Section 344 (punishment)
- Maximum life imprisonment
- Distinction between armed and unarmed robbery

---

#### Test #5: Impaired Driving Causing Death
**Question:** "What are the penalties for impaired driving causing death in Canada?"

**Expected Sources:**
- Criminal Code
- section 320.14
- impaired driving
- death

**Expected Articles:**
- Section 320.14
- Section 320.19

**Expected Websites:**
- Criminal Code
- justice.gc.ca

**What the Chatbot Should Provide:**
- Criminal Code Section 320.14
- Maximum life imprisonment
- Mandatory minimum sentences
- Recent law changes (Bill C-46)

---

### 🇨🇦 Canada - Traffic Law (5 tests)

#### Test #6: Stunt Driving (Ontario)
**Question:** "What is the penalty for stunt driving in Ontario?"

**Expected Sources:**
- Highway Traffic Act
- section 172
- stunt driving
- Ontario

**Expected Articles:**
- Section 172
- HTA

**Expected Websites:**
- ontario.ca
- Highway Traffic Act

**What the Chatbot Should Provide:**
- HTA Section 172 reference
- Immediate 30-day license suspension
- 14-day vehicle impoundment
- Fines ($2,000-$10,000)
- Demerit points and insurance implications

---

#### Test #7: Excessive Speeding (BC)
**Question:** "What are the penalties for excessive speeding in BC?"

**Expected Sources:**
- Motor Vehicle Act
- excessive speeding
- British Columbia

**Expected Articles:**
- Section 146
- MVA

**Expected Websites:**
- bclaws.gov.bc.ca
- Motor Vehicle Act

**What the Chatbot Should Provide:**
- Motor Vehicle Act Section 146
- Definition of excessive speeding (40+ km/h over limit)
- Vehicle impoundment periods
- Fines and penalties
- Driving prohibitions

---

#### Test #8: Driving Without Insurance (Alberta)
**Question:** "What is the penalty for driving without insurance in Alberta?"

**Expected Sources:**
- Traffic Safety Act
- insurance
- Alberta

**Expected Articles:**
- Section 54
- TSA

**Expected Websites:**
- alberta.ca
- Traffic Safety Act

**What the Chatbot Should Provide:**
- Traffic Safety Act Section 54
- Fines ($2,875 minimum)
- Vehicle seizure
- License suspension
- Proof of insurance requirements

---

#### Test #9: Cell Phone While Driving (Quebec)
**Question:** "What are the penalties for using a cell phone while driving in Quebec?"

**Expected Sources:**
- Highway Safety Code
- cell phone
- Quebec
- distracted

**Expected Articles:**
- Section 439.1
- Code de la sécurité routière

**Expected Websites:**
- saaq.gouv.qc.ca
- Quebec

**What the Chatbot Should Provide:**
- Highway Safety Code Section 439.1
- Fines ($300-$600)
- Demerit points (5 points)
- License suspension for repeat offenders
- SAAQ regulations

---

#### Test #10: Breathalyzer Refusal (Ontario)
**Question:** "What happens if you refuse a breathalyzer test in Ontario?"

**Expected Sources:**
- Criminal Code
- section 320.15
- refuse
- breathalyzer

**Expected Articles:**
- Section 320.15
- refusal

**Expected Websites:**
- Criminal Code
- ontario.ca

**What the Chatbot Should Provide:**
- Criminal Code Section 320.15
- Same penalties as impaired driving
- Mandatory minimum fines
- License suspension
- Criminal record implications

---

### 🇺🇸 USA - Criminal Law (5 tests)

#### Test #11: Bank Fraud
**Question:** "What is the federal penalty for bank fraud?"

**Expected Sources:**
- 18 U.S.C.
- 1344
- bank fraud
- federal

**Expected Articles:**
- 18 USC 1344
- Title 18

**Expected Websites:**
- uscode.house.gov
- law.cornell.edu

**What the Chatbot Should Provide:**
- 18 U.S.C. § 1344 reference
- Up to 30 years imprisonment
- Fines up to $1,000,000
- Definition of bank fraud
- Recent case examples

---

#### Test #12: Identity Theft
**Question:** "What constitutes identity theft under federal law?"

**Expected Sources:**
- 18 U.S.C.
- 1028
- identity theft

**Expected Articles:**
- 18 USC 1028
- identity fraud

**Expected Websites:**
- uscode.house.gov
- justice.gov

**What the Chatbot Should Provide:**
- 18 U.S.C. § 1028 reference
- Definition of identity theft
- Penalties (up to 15 years)
- Aggravated identity theft (additional 2 years)
- FTC resources

---

#### Test #13: Drug Trafficking
**Question:** "What are the penalties for drug trafficking under federal law?"

**Expected Sources:**
- 21 U.S.C.
- 841
- drug trafficking
- controlled substance

**Expected Articles:**
- 21 USC 841
- Schedule I

**Expected Websites:**
- uscode.house.gov
- dea.gov

**What the Chatbot Should Provide:**
- 21 U.S.C. § 841 reference
- Penalties by drug schedule and quantity
- Mandatory minimum sentences
- Enhanced penalties for repeat offenders
- DEA drug schedules

---

#### Test #14: Tax Evasion
**Question:** "What is the penalty for tax evasion in the United States?"

**Expected Sources:**
- 26 U.S.C.
- 7201
- tax evasion
- IRS

**Expected Articles:**
- 26 USC 7201
- Internal Revenue Code

**Expected Websites:**
- uscode.house.gov
- irs.gov

**What the Chatbot Should Provide:**
- 26 U.S.C. § 7201 reference
- Up to 5 years imprisonment
- Fines up to $250,000 (individuals)
- Civil penalties
- IRS enforcement procedures

---

#### Test #15: Racketeering (RICO)
**Question:** "What constitutes racketeering under RICO?"

**Expected Sources:**
- 18 U.S.C.
- 1961
- RICO
- racketeering

**Expected Articles:**
- 18 USC 1961
- RICO Act

**Expected Websites:**
- uscode.house.gov
- fbi.gov

**What the Chatbot Should Provide:**
- 18 U.S.C. § 1961 reference
- Definition of racketeering activity
- Pattern of racketeering
- Penalties (up to 20 years per count)
- Civil RICO provisions

---

### 🇺🇸 USA - Traffic Law (3 tests)

#### Test #16: Reckless Driving (California)
**Question:** "What is the penalty for reckless driving in California?"

**Expected Sources:**
- Vehicle Code
- 23103
- reckless driving
- California

**Expected Articles:**
- VC 23103
- California Vehicle Code

**Expected Websites:**
- leginfo.legislature.ca.gov
- dmv.ca.gov

**What the Chatbot Should Provide:**
- California Vehicle Code § 23103
- Misdemeanor charges
- 5-90 days jail time
- $145-$1,000 fine
- 2 points on license

---

#### Test #17: Street Racing (Texas)
**Question:** "What are the penalties for street racing in Texas?"

**Expected Sources:**
- Transportation Code
- 545.420
- racing
- Texas

**Expected Articles:**
- Section 545.420
- Texas Transportation Code

**Expected Websites:**
- statutes.capitol.texas.gov
- txdmv.gov

**What the Chatbot Should Provide:**
- Texas Transportation Code § 545.420
- Class B misdemeanor
- Up to 180 days jail
- Up to $2,000 fine
- License suspension

---

#### Test #18: Suspended License (New York)
**Question:** "What is the penalty for driving with a suspended license in New York?"

**Expected Sources:**
- Vehicle and Traffic Law
- VTL 511
- suspended license
- New York

**Expected Articles:**
- VTL 511
- New York VTL

**Expected Websites:**
- nysenate.gov
- dmv.ny.gov

**What the Chatbot Should Provide:**
- New York VTL § 511
- Misdemeanor charges
- Up to 30 days jail (first offense)
- $200-$500 fine
- Additional suspension period

---

### 👨‍👩‍👧 Family Law (2 tests)

#### Test #19: Child Support (Canada)
**Question:** "How is child support calculated in Canada?"

**Expected Sources:**
- Federal Child Support Guidelines
- child support
- calculation

**Expected Articles:**
- Section 3
- Guidelines

**Expected Websites:**
- justice.gc.ca
- Child Support Guidelines

**What the Chatbot Should Provide:**
- Federal Child Support Guidelines reference
- Section 3 calculation method
- Income-based tables
- Provincial/territorial variations
- Special expenses (Section 7)

---

#### Test #20: Adoption Requirements (USA)
**Question:** "What are the requirements for adoption in the United States?"

**Expected Sources:**
- adoption
- requirements
- federal
- state law

**Expected Articles:**
- adoption law
- requirements

**Expected Websites:**
- childwelfare.gov
- adoption.gov

**What the Chatbot Should Provide:**
- Federal and state requirements
- Home study process
- Age and residency requirements
- Background checks
- State-specific variations

---

### ©️ Copyright Law (2 tests)

#### Test #21: Copyright Duration (USA)
**Question:** "What is the duration of copyright protection in the United States?"

**Expected Sources:**
- 17 U.S.C.
- 302
- copyright
- duration

**Expected Articles:**
- 17 USC 302
- Copyright Act

**Expected Websites:**
- copyright.gov
- uscode.house.gov

**What the Chatbot Should Provide:**
- 17 U.S.C. § 302 reference
- Life of author + 70 years
- Works made for hire (95 years)
- Anonymous works (95 years)
- Pre-1978 works

---

#### Test #22: Fair Dealing (Canada)
**Question:** "What constitutes fair dealing under Canadian copyright law?"

**Expected Sources:**
- Copyright Act
- fair dealing
- section 29

**Expected Articles:**
- Section 29
- Copyright Act

**Expected Websites:**
- laws-lois.justice.gc.ca
- cipo.gc.ca

**What the Chatbot Should Provide:**
- Copyright Act Section 29
- Fair dealing purposes (research, private study, etc.)
- Six-factor fairness test
- Comparison with US fair use
- Recent Supreme Court decisions

---

### 💼 Employment Law (2 tests)

#### Test #23: Minimum Wage (Ontario)
**Question:** "What is the minimum wage in Ontario?"

**Expected Sources:**
- Employment Standards Act
- minimum wage
- Ontario

**Expected Articles:**
- ESA
- minimum wage

**Expected Websites:**
- ontario.ca
- Employment Standards

**What the Chatbot Should Provide:**
- Employment Standards Act reference
- Current minimum wage rate
- Student minimum wage
- Special rates (liquor servers, etc.)
- Upcoming increases

---

#### Test #24: Fair Labor Standards Act (USA)
**Question:** "What protections does the Fair Labor Standards Act provide?"

**Expected Sources:**
- FLSA
- 29 U.S.C.
- Fair Labor Standards Act

**Expected Articles:**
- 29 USC 201
- FLSA

**Expected Websites:**
- dol.gov
- uscode.house.gov

**What the Chatbot Should Provide:**
- 29 U.S.C. § 201 reference
- Minimum wage protections
- Overtime pay requirements
- Child labor restrictions
- Recordkeeping requirements

---

### 📜 Constitutional Law (1 test)

#### Test #25: Charter Section 8 (Canada)
**Question:** "What does Section 8 of the Charter protect against?"

**Expected Sources:**
- Charter
- section 8
- unreasonable search
- seizure

**Expected Articles:**
- Section 8
- Charter of Rights

**Expected Websites:**
- laws-lois.justice.gc.ca
- Charter

**What the Chatbot Should Provide:**
- Charter Section 8 reference
- Protection against unreasonable search and seizure
- Warrant requirements
- Reasonable expectation of privacy
- Key Supreme Court cases (R v. Collins, etc.)

---

## Test Results by Law Type

### Scoring System

Each test is scored based on:
- **Source Match (50%)** - Did it mention the expected legal sources?
- **Article Match (30%)** - Did it cite the specific articles/sections?
- **Website Match (20%)** - Did it reference official websites?

**Pass Threshold:** 40% overall score

### Expected Results Format

```
TEST #1: Criminal Law - Canada (Federal)
Question: What is the penalty for theft under $5000 in Canada?

--- RESPONSE STATUS ---
Answer: [OK] Under the Canadian Criminal Code, theft under $5000...
Citations: [OK] 5 sources

--- SOURCE VERIFICATION ---
Overall Score: 75.0%

Expected Sources: Criminal Code, section 334, theft, summary conviction
[OK] Found: Criminal Code, section 334, theft
[!] Missing: summary conviction
Match Rate: 75%

Expected Articles: Section 334, Section 322
[OK] Found: Section 334
[!] Missing: Section 322
Match Rate: 50%

Expected Websites: laws-lois.justice.gc.ca, Criminal Code
[OK] Found: Criminal Code
[!] Missing: laws-lois.justice.gc.ca
Match Rate: 50%

--- CITATION DETAILS ---
1. Source: Criminal Code Section 334
   Text: Theft under $5000 is punishable by summary conviction...
2. Source: Justice Canada
   Text: The Criminal Code defines theft as...

[PASS] TEST PASSED
```

---

## Daily Update System

### How It Works

The daily update system automatically:
1. **Scrapes** legal news websites at 2:00 AM daily
2. **Detects** new laws, amendments, and legal updates
3. **Compares** with previous scrapes to find only NEW content
4. **Generates** daily reports
5. **Prepares** documents for ingestion into vector database

### Scraped Sources

#### Canadian Sources
- Justice Canada - What's New
- Canada Gazette
- Ontario Laws Updates
- BC Laws Updates
- Alberta Laws
- Supreme Court of Canada RSS

#### US Sources
- Congress.gov Recent Laws
- Federal Register
- DOJ Press Releases
- California Legislative Information
- Texas Legislature Online
- New York State Senate
- US Supreme Court RSS

### Example: Daily Update Flow

**Saturday (Day 7):**
- Scraper runs at 2:00 AM
- Finds 15 new legal updates
- Saves to: `legal_updates/legal_updates_20260107.json`
- Updates hash database to track what's been seen

**Sunday (Day 8):**
- Scraper runs at 2:00 AM
- Finds 8 new legal updates (different from Day 7)
- Saves to: `legal_updates/legal_updates_20260108.json`
- Only includes NEW content not seen on Day 7

### Update Report Format

```json
{
  "date": "2026-01-08T02:00:00",
  "total_updates": 8,
  "updates": {
    "canada_federal": [
      {
        "title": "New Amendments to Criminal Code",
        "link": "https://justice.gc.ca/...",
        "date": "2026-01-07",
        "summary": "Bill C-XX introduces changes to...",
        "source": "Justice Canada",
        "jurisdiction": "Canada Federal",
        "type": "legislation"
      }
    ],
    "usa_federal": [
      {
        "title": "Supreme Court Rules on Privacy Case",
        "link": "https://supremecourt.gov/...",
        "date": "2026-01-07",
        "summary": "In a landmark decision...",
        "source": "US Supreme Court",
        "jurisdiction": "USA Federal",
        "type": "case_law"
      }
    ]
  }
}
```

---

## How to Run Tests

### Prerequisites

```bash
# Install required packages
pip install requests beautifulsoup4 schedule lxml
```

### Running the Test Suite

```bash
# Make sure backend is running
# Then run:
python advanced_legal_source_test.py
```

**Output:**
- Console output with detailed results
- JSON file: `advanced_legal_test_results_YYYYMMDD_HHMMSS.json`

### Running Tests for Specific Law Type

Edit the script to filter test cases:

```python
# Only run Criminal Law tests
filtered_tests = [t for t in COMPREHENSIVE_TEST_CASES if t['law_type'] == 'Criminal Law']
```

---

## Understanding Test Results

### Test Summary

```
================================================================================
TEST SUMMARY
================================================================================
Total Tests: 25
[OK] Passed: 22 (88.0%)
[X] Failed: 3 (12.0%)

--- RESULTS BY LAW TYPE AND COUNTRY ---
Canada - Criminal Law: 5/5 (100.0%)
Canada - Traffic Law: 5/5 (100.0%)
USA - Criminal Law: 4/5 (80.0%)
USA - Traffic Law: 3/3 (100.0%)
Canada - Family Law: 1/1 (100.0%)
USA - Family Law: 1/1 (100.0%)
USA - Copyright Law: 1/1 (100.0%)
Canada - Copyright Law: 1/1 (100.0%)
Canada - Employment Law: 1/1 (100.0%)
USA - Employment Law: 0/1 (0.0%)  ← NEEDS ATTENTION
Canada - Constitutional Law: 1/1 (100.0%)

--- AVERAGE SCORES ---
Overall Score: 68.5%
Source Match: 72.0%
Article Match: 58.0%
Website Match: 45.0%
Citations per Response: 5.0
```

### Interpreting Scores

- **90-100%**: Excellent - All expected sources found
- **70-89%**: Good - Most sources found, minor gaps
- **50-69%**: Acceptable - Core sources found, some missing
- **40-49%**: Marginal - Passes but needs improvement
- **Below 40%**: Failed - Insufficient source attribution

---

## Daily Scraper Setup

### Option 1: Manual Run

```bash
# Run scraper once
python legal_news_scraper.py
```

### Option 2: Scheduled Daily Run

```bash
# Run with scheduler (runs at 2:00 AM daily)
python daily_legal_updater.py
```

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Legal News Scraper"
4. Trigger: Daily at 2:00 AM
5. Action: Start a program
6. Program: `python`
7. Arguments: `C:\path\to\daily_legal_updater.py`
8. Start in: `C:\path\to\project`

### Option 4: Linux Cron Job

```bash
# Edit crontab
crontab -e

# Add this line (runs at 2:00 AM daily)
0 2 * * * cd /path/to/project && python daily_legal_updater.py >> scraper.log 2>&1
```

---

## Viewing Scraper Results

### Daily Report Location

```
legal_updates/
├── legal_updates_20260107.json  ← Saturday's updates
├── legal_updates_20260108.json  ← Sunday's updates
├── to_ingest_20260107.json      ← Prepared for ingestion
├── to_ingest_20260108.json
└── previous_updates.json         ← Hash database
```

### Checking What's New

```bash
# View today's updates
cat legal_updates/legal_updates_$(date +%Y%m%d).json

# Count new updates
python -c "import json; print(json.load(open('legal_updates/legal_updates_$(date +%Y%m%d).json'))['total_updates'])"
```

---

## Ingesting Scraped Updates

### Manual Ingestion

1. Open web interface: http://localhost:4200
2. Go to Upload section
3. Upload file: `legal_updates/to_ingest_YYYYMMDD.json`
4. System will process and add to vector database

### Automatic Ingestion (Future)

The `daily_legal_updater.py` script includes a placeholder for automatic ingestion. To enable:

1. Implement backend API endpoint for bulk document upload
2. Update `ingest_new_updates()` function
3. Add API authentication

---

## Troubleshooting

### Tests Failing

**Problem:** Low source match percentage

**Solutions:**
1. Check if documents are in vector database
2. Verify embedding model is working
3. Increase `top_k` parameter for more citations
4. Add more legal documents to database

### Scraper Not Finding Updates

**Problem:** 0 new updates every day

**Solutions:**
1. Check if websites changed structure
2. Verify internet connection
3. Update scraper selectors
4. Check `previous_updates.json` - may need to reset

### Scheduler Not Running

**Problem:** Daily job not executing

**Solutions:**
1. Check if script is running: `ps aux | grep daily_legal_updater`
2. Verify schedule time: `schedule.every().day.at("02:00")`
3. Check system time zone
4. Review logs for errors

---

## Files Generated

### Test Results
- `advanced_legal_test_results_YYYYMMDD_HHMMSS.json` - Full test results

### Scraper Output
- `legal_updates/legal_updates_YYYYMMDD.json` - Daily scrape results
- `legal_updates/to_ingest_YYYYMMDD.json` - Documents ready for ingestion
- `legal_updates/previous_updates.json` - Hash database for duplicate detection

---

## Next Steps

1. **Run Initial Test**
   ```bash
   python advanced_legal_source_test.py
   ```

2. **Review Results**
   - Check which law types need improvement
   - Identify missing sources

3. **Add Missing Documents**
   - Upload documents for low-scoring law types
   - Re-run tests to verify improvement

4. **Setup Daily Scraper**
   ```bash
   python daily_legal_updater.py
   ```

5. **Monitor Daily Updates**
   - Check `legal_updates/` folder daily
   - Ingest new documents weekly

---

## Support

For issues or questions:
1. Check test output JSON files for detailed error messages
2. Review backend logs: `backend_detailed.log`
3. Verify backend is running: http://localhost:8000/health

---

**Last Updated:** January 8, 2026  
**Version:** 1.0  
**Status:** Ready for Testing
