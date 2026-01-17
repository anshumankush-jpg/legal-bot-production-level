# Court/Ticket Lookup Dataset Collector

Production-grade dataset generator for LEGID that maps jurisdictions to official court and ticket lookup portals for Canada and USA.

## Overview

This collector system:
- Collects court and ticket portal URLs for all provinces/states and major cities
- Validates and verifies portal URLs
- Normalizes geographic names
- Provides a lookup API for the LEGID bot
- Outputs structured JSON datasets

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Collect Dataset

```bash
# Collect all (Canada + USA)
python -m collector.cli collect all

# Collect Canada only
python -m collector.cli collect canada

# Collect USA only
python -m collector.cli collect usa

# Test with limited cities (faster)
python -m collector.cli collect all --limit 5
```

### 2. Validate Dataset

```bash
python -m collector.cli validate
```

### 3. Export to CSV

```bash
python -m collector.cli export-csv
```

### 4. Test Lookup

```bash
# Lookup by city
python -m collector.cli lookup --city Toronto --country Canada

# Free-text search
python -m collector.cli lookup --search "Toronto traffic ticket"
```

## Data Model

Each jurisdiction record contains:

```json
{
  "id": "unique_hash",
  "country": "Canada|USA",
  "province_state": "Ontario",
  "city_or_county": "Toronto",
  "jurisdiction_level": "city|county|province_state|state",
  "ticket_types": ["traffic", "parking", "bylaw"],
  "portals": [
    {
      "name": "Portal Name",
      "url": "https://...",
      "authority": "City of Toronto",
      "portal_type": "case_lookup|pay_ticket|request_trial|court_directory",
      "requires": ["ticket_number", "offence_number"],
      "notes": "Additional information"
    }
  ],
  "language": ["en", "fr"],
  "last_verified_at": "2026-01-15T00:00:00",
  "verification_status": "verified|unverified|broken",
  "confidence": 0.9
}
```

## Output Files

- `output/canada.json` - Canadian jurisdictions
- `output/usa.json` - USA jurisdictions
- `output/all.json` - Combined dataset
- `output/all.csv` - CSV export

## Manual Overrides

Add custom portals in `overrides/manual_portals.json`. These will override auto-collected data.

Example (Toronto already included):

```json
{
  "id": "manual_toronto_traffic",
  "country": "Canada",
  "province_state": "Ontario",
  "city_or_county": "Toronto",
  "portals": [
    {
      "name": "City of Toronto Court Case Lookup",
      "url": "https://secure.toronto.ca/CourtCaseLookUp/welcome.jsf",
      "portal_type": "case_lookup"
    }
  ]
}
```

## Using the Lookup API

### In Python

```python
from collector.lookup_api import lookup_jurisdiction, get_lookup_api

# Simple lookup
results = lookup_jurisdiction(
    country="Canada",
    province_state="Ontario",
    city="Toronto",
    ticket_type="traffic"
)

# Advanced search
api = get_lookup_api()
results = api.search("Toronto traffic ticket")

# Get statistics
stats = api.get_stats()
```

### In LEGID Bot

The bot integration is in `backend/app/services/court_lookup_service.py` (see next section).

## Integration with LEGID

The dataset is integrated with the LEGID bot to:

1. **Auto-detect jurisdiction from OCR-scanned tickets**
2. **Provide case lookup links in responses**
3. **Search for relevant portals**
4. **Guide users to the right portal**

See `INTEGRATION_GUIDE.md` for details.

## How It Works

### Collection Process

1. **Load Seeds**: Reads province/state definitions from `seeds/`
2. **Scrape Directories**: Fetches official court directory pages
3. **Discover Portals**: Uses search patterns to find municipal portals
4. **Validate URLs**: Checks domains, keywords, and accessibility
5. **Normalize Data**: Standardizes city and province/state names
6. **Merge Overrides**: Applies manual corrections
7. **Generate Output**: Saves to JSON/CSV

### Verification

URLs are verified by:
- Checking for official domains (`.gov`, `.ca`, etc.)
- Parsing page content for court-related keywords
- Detecting captchas or blocked pages
- Assigning confidence scores

### Search Index

The lookup API builds an index for fast searches:
- By city name
- By province/state + city
- By country + province/state + city
- Free-text search across all fields

## Adding New Provinces/States

1. Edit `seeds/canada_provinces.json` or `seeds/us_states.json`
2. Add region definition:

```json
{
  "region_name": "New Province",
  "region_code": "NP",
  "country": "Canada",
  "official_directory_urls": ["https://..."],
  "search_patterns": ["{city} New Province court"],
  "top_cities": ["City1", "City2"]
}
```

3. Re-run collection

## Testing

```bash
# Run with limited data for testing
python -m collector.cli collect all --limit 3

# Validate output
python -m collector.cli validate

# Test specific lookup
python -m collector.cli lookup --city "Your City" --country Canada
```

## Production Deployment

### Weekly Re-verification Job

```bash
# Create a cron job or scheduled task
0 2 * * 0 python -m collector.cli collect all --verify
```

### CI/CD Integration

```yaml
# .github/workflows/update-dataset.yml
name: Update Court Dataset
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Collect dataset
        run: python -m collector.cli collect all
      - name: Validate
        run: python -m collector.cli validate
```

## Limitations & Future Improvements

### Current MVP

- Auto-collected records are placeholders (not real scraped portals)
- Manual overrides contain verified portals (Toronto, Vancouver, LA, etc.)
- Search API integration not implemented (would require API keys)

### Production Enhancements

1. **Search API Integration**
   - Google Custom Search API
   - Bing Search API
   - SerpAPI for discovery

2. **Advanced Scraping**
   - Selenium for JavaScript-rendered pages
   - Captcha solving services
   - Proxy rotation for rate limits

3. **Continuous Verification**
   - Automated re-verification
   - Broken link detection
   - Email alerts for broken portals

4. **Machine Learning**
   - Auto-classify portal types
   - Extract requirements from page content
   - Improve confidence scoring

5. **Admin UI**
   - Dashboard for dataset management
   - Manual verification interface
   - Analytics and monitoring

## License

Part of the LEGID legal assistant system.
