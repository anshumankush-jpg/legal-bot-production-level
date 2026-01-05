"""Ingest DUI legal data directly into Artillery vector store."""
import requests
import json
import sys
import time
import logging
from pathlib import Path
import tempfile
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"

# Comprehensive DUI legal information
LEGAL_DATASET = {
    "canada_dui_laws": {
        "country": "Canada",
        "jurisdiction": "Federal",
        "content": """CANADIAN DUI LAWS - CRIMINAL CODE OF CANADA

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
- Increased insurance costs"""
    },
    "ontario_dui": {
        "country": "Canada",
        "jurisdiction": "Ontario",
        "content": """ONTARIO DUI LAWS AND PENALTIES

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

Fines and Costs:
- Criminal fines: $1,000-$10,000+
- Legal fees: $5,000-$20,000+
- Ignition interlock: $1,000-$2,000/year
- Increased insurance: $3,000-$10,000/year
- Total costs often exceed $20,000 for first offence"""
    },
    "us_dui_federal": {
        "country": "United States",
        "jurisdiction": "Federal",
        "content": """UNITED STATES DUI LAWS - FEDERAL OVERVIEW

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
- Some states allow plea bargains"""
    },
    "california_dui": {
        "country": "United States",
        "jurisdiction": "California",
        "content": """CALIFORNIA DUI LAWS

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
- Causing death: Vehicular manslaughter charges"""
    },
    "texas_dui": {
        "country": "United States",
        "jurisdiction": "Texas",
        "content": """TEXAS DUI/DWI LAWS

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
- Can be used as evidence of guilt"""
    },
    "florida_dui": {
        "country": "United States",
        "jurisdiction": "Florida",
        "content": """FLORIDA DUI LAWS

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
- Property damage or injury: Enhanced charges"""
    },
    "common_defenses": {
        "country": "Both",
        "jurisdiction": "General",
        "content": """COMMON DUI DEFENSES

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

IMPORTANT: These are general defenses. Success depends on specific facts, jurisdiction, and legal representation."""
    }
}


def upload_text_as_file(text: str, filename: str) -> bool:
    """Upload text content as a file to Artillery endpoint."""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(text)
            tmp_path = tmp_file.name
        
        try:
            # Upload file
            with open(tmp_path, 'rb') as f:
                files = {'file': (filename, f, 'text/plain')}
                data = {
                    'user_id': 'system',
                    'offence_number': None
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/api/artillery/upload",
                    files=files,
                    data=data,
                    timeout=120
                )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Uploaded: {filename} ({result.get('chunks_indexed', 0)} chunks)")
                return True
            else:
                logger.error(f"✗ Failed to upload {filename}: {response.status_code} - {response.text}")
                return False
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        logger.error(f"✗ Error uploading {filename}: {e}")
        return False


def main():
    """Main function to ingest DUI data into Artillery."""
    print("=" * 80)
    print("INGESTING DUI LEGAL DATA INTO ARTILLERY SYSTEM")
    print("=" * 80)
    print("\nThis will upload comprehensive DUI laws to the Artillery vector store")
    print("which is used by the /api/artillery/chat endpoint.\n")
    
    # Check backend
    try:
        response = requests.get(f"{API_BASE_URL}/api/artillery/health", timeout=5)
        if response.status_code != 200:
            logger.error("Artillery backend is not healthy")
            return False
    except Exception as e:
        logger.error(f"Backend is not running: {e}")
        return False
    
    uploaded_count = 0
    failed_count = 0
    
    # Upload each legal document
    for key, data in LEGAL_DATASET.items():
        filename = f"{data['jurisdiction']}_DUI_Laws.txt"
        if upload_text_as_file(data['content'], filename):
            uploaded_count += 1
        else:
            failed_count += 1
        time.sleep(1)  # Small delay
    
    print("\n" + "=" * 80)
    print("INGESTION COMPLETE")
    print("=" * 80)
    print(f"Successfully uploaded: {uploaded_count} documents")
    print(f"Failed: {failed_count} documents")
    print("\nThe Artillery system now has comprehensive DUI legal information!")
    print("Test with: python test_dui_backend.py")
    print("=" * 80)
    
    return uploaded_count > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
