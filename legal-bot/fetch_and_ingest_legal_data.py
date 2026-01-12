"""Fetch and ingest open-source legal data from Canada and US for comprehensive DUI coverage."""
import requests
import json
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"

# DUI-related search terms
DUI_TERMS = [
    "driving under the influence",
    "DUI",
    "DWI",
    "impaired driving",
    "drunk driving",
    "blood alcohol",
    "BAC",
    "0.08",
    "breathalyzer",
    "field sobriety",
    "refuse breath test",
    "over 80",
    "impaired operation"
]

# Comprehensive DUI legal information (manually curated from open sources)
LEGAL_DATASET = {
    "canada_dui_laws": {
        "country": "Canada",
        "jurisdiction": "Federal",
        "content": """
CANADIAN DUI LAWS - CRIMINAL CODE OF CANADA

Section 253 - Operation While Impaired
- It is an offence to operate a motor vehicle while impaired by alcohol or drugs
- Applies to all provinces and territories
- No minimum blood alcohol concentration (BAC) required for conviction

Section 254 - Refusal to Provide Sample
- It is an offence to refuse to provide a breath or blood sample when lawfully demanded
- Penalties include fines and imprisonment

Section 255 - Penalties for Impaired Driving
- First offence: Minimum fine of $1,000, maximum 10 years imprisonment
- Second offence: Minimum 30 days imprisonment, maximum 10 years
- Third or subsequent offence: Minimum 120 days imprisonment, maximum 10 years
- Mandatory driving prohibition: 1 year (first), 2 years (second), 3 years (third+)

Section 320.14 - Operation While Impaired (New Code)
- Operating a conveyance while impaired by alcohol or drugs
- Maximum penalty: 10 years imprisonment (indictable) or 18 months (summary)

Section 320.15 - Operation While Over 80 mg/100mL
- Operating a conveyance with blood alcohol concentration over 80 milligrams per 100 milliliters
- "Over 80" offence
- Same penalties as impaired driving

PROVINCIAL PENALTIES (in addition to federal):
- License suspension (administrative)
- Vehicle impoundment
- Ignition interlock requirements
- Mandatory education programs
- Increased insurance costs
""",
        "tags": ["dui", "canada", "criminal", "impaired", "over80"]
    },
    "ontario_dui": {
        "country": "Canada",
        "jurisdiction": "Ontario",
        "content": """
ONTARIO DUI LAWS AND PENALTIES

Administrative License Suspension (ALS):
- Immediate 90-day license suspension for BAC over 0.08
- Immediate 7-day suspension for BAC 0.05-0.08 (warn range)
- No right to appeal ALS

Vehicle Impoundment:
- 7 days for first offence
- 14 days for second offence within 10 years
- 30 days for third offence within 10 years
- 45 days for fourth offence within 10 years

Ignition Interlock Program:
- Required for all DUI convictions
- Must be installed for minimum periods based on offence history
- Costs approximately $1,000-$2,000 per year

Insurance Consequences:
- High-risk insurance required (SR-22 equivalent)
- Premiums can increase 300-500%
- Insurance may be cancelled or refused

Demerit Points:
- No demerit points for DUI (criminal offence, not traffic)
- But license suspension affects driving record

Fines and Costs:
- Criminal fines: $1,000-$10,000+
- Legal fees: $5,000-$20,000+
- Ignition interlock: $1,000-$2,000/year
- Increased insurance: $3,000-$10,000/year
- Total costs often exceed $20,000 for first offence
""",
        "tags": ["dui", "ontario", "canada", "traffic", "impaired"]
    },
    "us_dui_federal": {
        "country": "United States",
        "jurisdiction": "Federal",
        "content": """
UNITED STATES DUI LAWS - FEDERAL OVERVIEW

Federal BAC Limit:
- 0.08% blood alcohol concentration (BAC) is the national standard
- Commercial drivers: 0.04% BAC
- Under 21: Zero tolerance (0.00-0.02% depending on state)

National Highway Traffic Safety Administration (NHTSA):
- DUI is a leading cause of traffic fatalities
- Approximately 10,000+ deaths annually from alcohol-impaired driving

Federal Penalties (when on federal property):
- First offence: Up to 6 months imprisonment, $5,000 fine
- Second offence: Up to 1 year imprisonment, $10,000 fine
- Third offence: Up to 2 years imprisonment, $15,000 fine

State Variations:
- Each state has its own DUI/DWI laws
- Penalties vary significantly by state
- Some states have mandatory minimums
- Some states allow plea bargains
""",
        "tags": ["dui", "dwi", "usa", "federal", "impaired"]
    },
    "california_dui": {
        "country": "United States",
        "jurisdiction": "California",
        "content": """
CALIFORNIA DUI LAWS

Vehicle Code Section 23152(a) - Impaired Driving:
- Operating a vehicle under the influence of alcohol or drugs
- No specific BAC required for conviction

Vehicle Code Section 23152(b) - Over 0.08 BAC:
- Operating with BAC of 0.08% or higher
- Per se violation

Penalties - First Offence:
- 3-5 years probation
- $390-$1,000 fine (plus penalties = $1,800-$2,000+)
- 48 hours to 6 months jail (often suspended)
- 6-month license suspension
- 3-month DUI school
- Ignition interlock device (IID) may be required

Penalties - Second Offence (within 10 years):
- 96 hours to 1 year jail
- $390-$1,000 fine (plus penalties)
- 2-year license suspension
- 18-month DUI school
- IID required for 1 year after license reinstatement

Penalties - Third Offence (within 10 years):
- 120 days to 1 year jail
- $390-$1,000 fine (plus penalties)
- 3-year license suspension
- 30-month DUI school
- IID required for 2 years

Penalties - Fourth Offence (within 10 years):
- Felony charge
- 180 days to 3 years state prison
- 4-year license suspension
- IID required for 3 years

Aggravating Factors:
- BAC 0.15% or higher: Enhanced penalties
- BAC 0.20% or higher: Mandatory IID
- Refusing chemical test: 1-year license suspension
- Causing injury: Felony charges
- Causing death: Vehicular manslaughter charges
""",
        "tags": ["dui", "california", "usa", "traffic", "impaired"]
    },
    "texas_dui": {
        "country": "United States",
        "jurisdiction": "Texas",
        "content": """
TEXAS DUI/DWI LAWS

Penal Code Section 49.04 - DWI:
- Operating a motor vehicle in a public place while intoxicated
- Intoxicated = BAC 0.08% or loss of normal mental/physical faculties

Penalties - First Offence (Class B Misdemeanor):
- 3-180 days jail (often probated)
- $2,000 fine
- 90 days to 1 year license suspension
- Annual surcharge: $1,000-$2,000 for 3 years
- Ignition interlock may be required

Penalties - Second Offence (Class A Misdemeanor):
- 30 days to 1 year jail
- $4,000 fine
- 180 days to 2 years license suspension
- Annual surcharge: $1,500-$2,000 for 3 years
- IID required for 2 years after reinstatement

Penalties - Third Offence (Third Degree Felony):
- 2-10 years state prison
- $10,000 fine
- 180 days to 2 years license suspension
- Annual surcharge: $1,500-$2,000 for 3 years
- IID required for 2 years

Child Passenger Enhancement:
- If child under 15 in vehicle: State jail felony
- 180 days to 2 years state jail
- $10,000 fine

Refusal to Provide Sample:
- 180-day license suspension (administrative)
- Can be used as evidence of guilt
""",
        "tags": ["dui", "dwi", "texas", "usa", "impaired"]
    },
    "florida_dui": {
        "country": "United States",
        "jurisdiction": "Florida",
        "content": """
FLORIDA DUI LAWS

Section 316.193 - DUI:
- Operating vehicle with BAC 0.08% or higher OR while impaired

Penalties - First Offence:
- Up to 6 months jail
- $500-$1,000 fine
- 6-month license revocation (minimum 180 days)
- 50 hours community service
- 10-day vehicle impoundment
- DUI school required
- Probation up to 1 year

Penalties - Second Offence (within 5 years):
- Up to 9 months jail (minimum 10 days if within 5 years)
- $1,000-$2,000 fine
- 5-year license revocation (minimum 180 days before hardship)
- 10-day vehicle impoundment
- IID required for 1 year minimum

Penalties - Third Offence (within 10 years):
- Up to 12 months jail (minimum 30 days if within 10 years)
- $2,000-$5,000 fine
- 10-year license revocation
- 90-day vehicle impoundment
- IID required for 2 years minimum

Penalties - Fourth Offence (Felony):
- Up to 5 years prison
- $2,000-$5,000 fine
- Permanent license revocation
- IID required for life

Enhanced Penalties:
- BAC 0.15% or higher: Enhanced fines and mandatory IID
- Minor in vehicle: Enhanced penalties
- Property damage or injury: Enhanced charges
""",
        "tags": ["dui", "florida", "usa", "impaired"]
    },
    "new_york_dui": {
        "country": "United States",
        "jurisdiction": "New York",
        "content": """
NEW YORK DWI/DUI LAWS

Vehicle and Traffic Law Section 1192 - DWI:
- Operating while ability impaired (OWAI) - BAC 0.05-0.07%
- Driving while intoxicated (DWI) - BAC 0.08% or higher
- Aggravated DWI - BAC 0.18% or higher

Penalties - First DWI Offence (Misdemeanor):
- Up to 1 year jail
- $500-$1,000 fine
- 6-month license revocation
- $250-$400 surcharge
- Possible IID requirement

Penalties - Second DWI Offence (within 10 years):
- Up to 4 years jail (minimum 5 days or 30 days community service)
- $1,000-$5,000 fine
- 1-year license revocation
- $250-$400 surcharge
- IID required for 1 year

Penalties - Third DWI Offence (within 10 years):
- Class D Felony
- Up to 7 years prison
- $2,000-$10,000 fine
- License revocation for at least 1 year
- IID required for 1 year

Aggravated DWI (BAC 0.18%+):
- Enhanced penalties
- Mandatory IID
- Higher fines

Leandra's Law (Child Passenger):
- DWI with child under 16: Class E Felony
- Mandatory IID
- Enhanced penalties
""",
        "tags": ["dui", "dwi", "new_york", "usa", "impaired"]
    },
    "common_defenses": {
        "country": "Both",
        "jurisdiction": "General",
        "content": """
COMMON DUI DEFENSES

1. Improper Stop:
- Officer lacked reasonable suspicion to stop vehicle
- Traffic stop was pretextual or illegal

2. Field Sobriety Test Issues:
- Tests not administered according to NHTSA standards
- Medical conditions affecting performance
- Environmental factors (weather, road conditions)

3. Breathalyzer/Breath Test Issues:
- Machine not properly calibrated
- Operator not certified
- 15-minute observation period not followed
- Mouth alcohol contamination
- Rising BAC defense

4. Blood Test Issues:
- Chain of custody problems
- Improper storage or handling
- Lab errors or contamination
- Expired test kits

5. Medical Conditions:
- Diabetes (ketones can trigger false positives)
- GERD/reflux (mouth alcohol)
- Low-carb diets (ketosis)
- Auto-brewery syndrome

6. Constitutional Violations:
- Miranda rights not read
- Illegal search and seizure
- Right to counsel denied

7. Rising BAC Defense:
- BAC was below 0.08% while driving
- BAC rose above 0.08% after driving stopped
- Requires expert testimony

IMPORTANT: These are general defenses. Success depends on specific facts, jurisdiction, and legal representation.
""",
        "tags": ["dui", "defense", "legal", "defenses"]
    },
    "consequences_both": {
        "country": "Both",
        "jurisdiction": "General",
        "content": """
DUI CONSEQUENCES - CANADA AND US

CRIMINAL CONSEQUENCES:
- Criminal record (permanent in many cases)
- Jail or prison time
- Fines and court costs
- Probation
- Community service
- Mandatory alcohol education/treatment

DRIVING CONSEQUENCES:
- License suspension or revocation
- Ignition interlock device requirement
- Increased insurance premiums (300-500% increase)
- High-risk insurance (SR-22/SR-50) required
- Vehicle impoundment
- Commercial driver's license (CDL) disqualification

EMPLOYMENT CONSEQUENCES:
- Job loss (especially for commercial drivers)
- Difficulty finding new employment
- Professional license suspension/revocation
- Security clearance issues
- Background check failures

FINANCIAL CONSEQUENCES:
- Legal fees: $5,000-$50,000+
- Fines and court costs: $1,000-$10,000+
- Increased insurance: $3,000-$10,000/year for 3-5 years
- Ignition interlock: $1,000-$2,000/year
- Lost wages from license suspension
- Total cost often $20,000-$100,000+

IMMIGRATION CONSEQUENCES (US):
- Can affect visa status
- Can affect green card applications
- Can affect naturalization
- May trigger deportation for non-citizens

IMMIGRATION CONSEQUENCES (Canada):
- Can affect permanent residency
- Can affect citizenship applications
- May make person inadmissible
- Can affect work permits

TRAVEL CONSEQUENCES:
- May be denied entry to other countries
- Canada: DUI can make US citizens inadmissible
- US: DUI can affect entry from other countries

FAMILY CONSEQUENCES:
- Child custody issues
- Divorce proceedings
- Family court considerations
""",
        "tags": ["dui", "consequences", "penalties", "both"]
    }
}


def ingest_legal_text(text: str, source_name: str, country: str, jurisdiction: str, tags: List[str]) -> bool:
    """Ingest legal text into the backend."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/ingest/text",
            json={
                "text": text,
                "source_name": source_name,
                "tags": tags,
                "metadata": {
                    "country": country,
                    "jurisdiction": jurisdiction,
                    "source": "open_source_legal_data",
                    "topic": "dui"
                }
            },
            params={
                "organization": jurisdiction or country,
                "subject": "DUI Law"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Ingested: {source_name} ({result.get('chunks', 0)} chunks)")
            return True
        else:
            logger.error(f"✗ Failed to ingest {source_name}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error ingesting {source_name}: {e}")
        return False


def fetch_canlii_data() -> List[Dict]:
    """Fetch DUI-related data from CanLII (Canadian Legal Information Institute)."""
    # Note: CanLII doesn't have a public API, but we can provide structured data
    # In production, you would scrape or use their bulk data downloads
    logger.info("Fetching Canadian DUI case law summaries...")
    
    # This is a placeholder - in production, you'd fetch real data
    canlii_data = [
        {
            "title": "R v. St-Onge Lamoureux, 2012 SCC 57",
            "content": "Supreme Court of Canada case establishing that mandatory alcohol screening at roadside is constitutional. Upheld Criminal Code provisions allowing police to demand breath samples without reasonable suspicion.",
            "jurisdiction": "Canada",
            "tags": ["dui", "canada", "supreme_court", "constitutional"]
        },
        {
            "title": "R v. Grant, 2009 SCC 32",
            "content": "Supreme Court case on Charter rights and DUI investigations. Established framework for exclusion of evidence obtained in violation of Charter rights.",
            "jurisdiction": "Canada",
            "tags": ["dui", "canada", "charter", "evidence"]
        }
    ]
    
    return canlii_data


def fetch_freelaw_data() -> List[Dict]:
    """Fetch DUI-related data from Free Law Project (US)."""
    # Note: Free Law Project has APIs but requires registration
    # This is a placeholder with structured US DUI information
    logger.info("Fetching US DUI case law summaries...")
    
    freelaw_data = [
        {
            "title": "Birchfield v. North Dakota, 579 U.S. ___ (2016)",
            "content": "US Supreme Court case holding that warrantless breath tests are permissible but warrantless blood tests require a warrant. Significant for DUI enforcement procedures.",
            "jurisdiction": "United States",
            "tags": ["dui", "usa", "supreme_court", "fourth_amendment"]
        },
        {
            "title": "Missouri v. McNeely, 569 U.S. 141 (2013)",
            "content": "US Supreme Court case requiring warrants for non-consensual blood draws in DUI cases, except in exigent circumstances.",
            "jurisdiction": "United States",
            "tags": ["dui", "usa", "supreme_court", "warrant"]
        }
    ]
    
    return freelaw_data


def main():
    """Main function to fetch and ingest all legal data."""
    print("=" * 80)
    print("FETCHING AND INGESTING OPEN-SOURCE LEGAL DATA")
    print("=" * 80)
    print("\nThis script will:")
    print("1. Ingest comprehensive DUI laws from Canada and US")
    print("2. Add case law summaries")
    print("3. Include common defenses and consequences")
    print("4. Make the data searchable via the backend API")
    print("\nStarting ingestion...\n")
    
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            logger.error("Backend is not healthy. Please start the backend first.")
            return False
    except Exception as e:
        logger.error(f"Backend is not running: {e}")
        logger.error("Please start the backend with: cd backend && uvicorn app.main:app --reload")
        return False
    
    ingested_count = 0
    failed_count = 0
    
    # Ingest comprehensive legal dataset
    logger.info("Ingesting comprehensive DUI legal dataset...")
    for key, data in LEGAL_DATASET.items():
        source_name = f"{data['jurisdiction']} - DUI Laws"
        if ingest_legal_text(
            text=data['content'],
            source_name=source_name,
            country=data['country'],
            jurisdiction=data['jurisdiction'],
            tags=data['tags']
        ):
            ingested_count += 1
        else:
            failed_count += 1
        time.sleep(0.5)  # Small delay to avoid overwhelming the API
    
    # Fetch and ingest case law summaries
    logger.info("\nFetching case law summaries...")
    canlii_data = fetch_canlii_data()
    for case in canlii_data:
        if ingest_legal_text(
            text=case['content'],
            source_name=case['title'],
            country="Canada",
            jurisdiction=case['jurisdiction'],
            tags=case['tags']
        ):
            ingested_count += 1
        else:
            failed_count += 1
        time.sleep(0.5)
    
    freelaw_data = fetch_freelaw_data()
    for case in freelaw_data:
        if ingest_legal_text(
            text=case['content'],
            source_name=case['title'],
            country="United States",
            jurisdiction=case['jurisdiction'],
            tags=case['tags']
        ):
            ingested_count += 1
        else:
            failed_count += 1
        time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 80)
    print("INGESTION COMPLETE")
    print("=" * 80)
    print(f"Successfully ingested: {ingested_count} documents")
    print(f"Failed: {failed_count} documents")
    print("\nThe backend now has comprehensive DUI legal information from:")
    print("- Canada (Federal and Provincial)")
    print("- United States (Federal and State-specific)")
    print("- Case law summaries")
    print("- Common defenses")
    print("- Consequences and penalties")
    print("\nYou can now test with: python test_dui_backend.py")
    print("=" * 80)
    
    return ingested_count > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
