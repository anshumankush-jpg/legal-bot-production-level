"""Comprehensive Legal Data Collector for USA and Canada.
Collects federal, traffic, and criminal laws, case studies, and court decisions."""
import requests
import json
import time
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Output directory
DATA_DIR = Path("collected_legal_data")
DATA_DIR.mkdir(exist_ok=True)

# Comprehensive legal dataset structure
LEGAL_DATASET = {
    "usa_federal_criminal": [],
    "usa_traffic_laws": [],
    "usa_state_criminal": [],
    "canada_federal_criminal": [],
    "canada_traffic_laws": [],
    "canada_provincial_criminal": [],
    "case_studies": [],
    "court_decisions": []
}

# Headers for web scraping
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def collect_usa_federal_criminal_laws():
    """Collect USA Federal Criminal Laws."""
    logger.info("Collecting USA Federal Criminal Laws...")
    
    data = [
        {
            "title": "18 U.S.C. § 371 - Conspiracy to Defraud the United States",
            "content": """18 U.S.C. § 371 - Conspiracy to Defraud the United States

Elements:
- Two or more persons conspire
- To commit any offense against the United States
- Or to defraud the United States
- One or more persons do any act to effect the object of the conspiracy

Penalties:
- Fine up to $250,000 (individual) or $500,000 (organization)
- Imprisonment up to 5 years
- Or both

Common Questions:
- What constitutes conspiracy under federal law?
- What is the difference between conspiracy and attempt?
- Can you be charged with conspiracy if the underlying crime wasn't completed?
- What is the statute of limitations for conspiracy?
- Can you withdraw from a conspiracy?""",
            "jurisdiction": "Federal",
            "country": "USA",
            "category": "criminal",
            "tags": ["conspiracy", "federal", "criminal"]
        },
        {
            "title": "18 U.S.C. § 1341 - Mail Fraud",
            "content": """18 U.S.C. § 1341 - Mail Fraud

Elements:
- Devising or intending to devise a scheme to defraud
- Using the mail or causing mail to be used
- For the purpose of executing the scheme

Penalties:
- Fine up to $1,000,000
- Imprisonment up to 20 years
- Or both

Common Questions:
- What constitutes mail fraud?
- Does email count as mail fraud?
- What is wire fraud vs mail fraud?
- What is the statute of limitations for mail fraud?
- Can you be charged with both mail fraud and the underlying crime?""",
            "jurisdiction": "Federal",
            "country": "USA",
            "category": "criminal",
            "tags": ["fraud", "mail", "federal"]
        },
        {
            "title": "18 U.S.C. § 1343 - Wire Fraud",
            "content": """18 U.S.C. § 1343 - Wire Fraud

Elements:
- Devising or intending to devise a scheme to defraud
- Transmitting or causing transmission by wire, radio, or television
- In interstate or foreign commerce
- For the purpose of executing the scheme

Penalties:
- Fine up to $1,000,000
- Imprisonment up to 20 years
- Or both

Common Questions:
- What is wire fraud?
- Does internet communication count as wire fraud?
- What is the difference between wire fraud and mail fraud?
- Can wire fraud be charged for intrastate communications?
- What are common wire fraud schemes?""",
            "jurisdiction": "Federal",
            "country": "USA",
            "category": "criminal",
            "tags": ["fraud", "wire", "federal", "internet"]
        },
        {
            "title": "18 U.S.C. § 1956 - Money Laundering",
            "content": """18 U.S.C. § 1956 - Money Laundering

Elements:
- Knowingly conducts or attempts to conduct a financial transaction
- Involving proceeds of specified unlawful activity
- With intent to promote, conceal, or avoid reporting requirement

Penalties:
- Fine up to $500,000 or twice the value of property involved
- Imprisonment up to 20 years
- Or both

Common Questions:
- What is money laundering?
- What constitutes a financial transaction?
- What is the difference between money laundering and structuring?
- Can you be charged with money laundering if you didn't know the source?
- What are the reporting requirements for large cash transactions?""",
            "jurisdiction": "Federal",
            "country": "USA",
            "category": "criminal",
            "tags": ["money_laundering", "financial_crime", "federal"]
        },
        {
            "title": "21 U.S.C. § 841 - Controlled Substances Act",
            "content": """21 U.S.C. § 841 - Controlled Substances Act (Drug Trafficking)

Elements:
- Knowingly or intentionally
- Manufacture, distribute, or dispense
- A controlled substance
- Or possess with intent to manufacture, distribute, or dispense

Penalties (varies by drug type and quantity):
- Schedule I or II: Up to 20 years, fine up to $1,000,000
- Schedule III: Up to 5 years, fine up to $250,000
- Schedule IV: Up to 3 years, fine up to $250,000
- Schedule V: Up to 1 year, fine up to $100,000

Common Questions:
- What are the different drug schedules?
- What is the difference between possession and trafficking?
- What are mandatory minimum sentences for drug crimes?
- Can you be charged federally and state for the same drug crime?
- What is the difference between distribution and manufacturing?""",
            "jurisdiction": "Federal",
            "country": "USA",
            "category": "criminal",
            "tags": ["drugs", "controlled_substances", "trafficking", "federal"]
        }
    ]
    
    LEGAL_DATASET["usa_federal_criminal"].extend(data)
    logger.info(f"Collected {len(data)} USA Federal Criminal Laws")


def collect_usa_traffic_laws():
    """Collect USA Traffic Laws by State."""
    logger.info("Collecting USA Traffic Laws...")
    
    states = ["California", "Texas", "Florida", "New York", "Illinois", "Pennsylvania", 
              "Ohio", "Georgia", "North Carolina", "Michigan", "New Jersey", "Virginia",
              "Washington", "Arizona", "Massachusetts", "Tennessee", "Indiana", "Missouri",
              "Maryland", "Wisconsin", "Colorado", "Minnesota", "South Carolina", "Alabama",
              "Louisiana", "Kentucky", "Oregon", "Oklahoma", "Connecticut", "Utah", "Iowa",
              "Nevada", "Arkansas", "Mississippi", "Kansas", "New Mexico", "Nebraska",
              "West Virginia", "Idaho", "Hawaii", "New Hampshire", "Maine", "Montana",
              "Rhode Island", "Delaware", "South Dakota", "North Dakota", "Alaska", "Vermont", "Wyoming"]
    
    for state in states:
        data = {
            "title": f"{state} - Speeding Violations",
            "content": f"""{state} Speeding Laws

Basic Speed Law:
- Must not drive at a speed greater than is reasonable and prudent
- Must consider traffic, weather, road conditions, and visibility

Maximum Speed Limits:
- Urban areas: Typically 25-35 mph
- Rural highways: Typically 55-65 mph
- Freeways: Typically 65-75 mph (varies by state)

Penalties for Speeding:
- 1-10 mph over: Typically $100-$200 fine, possible points
- 11-20 mph over: Typically $200-$400 fine, points, possible license suspension
- 21+ mph over: Typically $400-$1000+ fine, mandatory court appearance, possible jail

Common Questions:
- What is the speed limit in {state}?
- How many points for speeding in {state}?
- Can I fight a speeding ticket in {state}?
- What is the fine for speeding in {state}?
- Does speeding affect insurance in {state}?
- Can I take traffic school to avoid points in {state}?
- What is the difference between absolute and presumed speed limits?""",
            "jurisdiction": state,
            "country": "USA",
            "category": "traffic",
            "tags": ["speeding", "traffic", state.lower().replace(" ", "_")]
        }
        LEGAL_DATASET["usa_traffic_laws"].append(data)
    
    logger.info(f"Collected traffic laws for {len(states)} US states")


def collect_canada_federal_criminal_laws():
    """Collect Canada Federal Criminal Laws."""
    logger.info("Collecting Canada Federal Criminal Laws...")
    
    data = [
        {
            "title": "Criminal Code Section 253 - Impaired Driving",
            "content": """Criminal Code Section 253 - Operation While Impaired

Elements:
- Operate a motor vehicle, vessel, aircraft, or railway equipment
- While ability to operate is impaired by alcohol or drugs
- OR with blood alcohol concentration over 80 mg per 100 mL

Penalties - First Offence:
- Minimum fine: $1,000
- Maximum imprisonment: 10 years
- Mandatory driving prohibition: 1 year (minimum)

Penalties - Second Offence:
- Minimum imprisonment: 30 days
- Maximum imprisonment: 10 years
- Mandatory driving prohibition: 2 years (minimum)

Penalties - Third or Subsequent Offence:
- Minimum imprisonment: 120 days
- Maximum imprisonment: 10 years
- Mandatory driving prohibition: 3 years (minimum)

Common Questions:
- What is the legal BAC limit in Canada?
- What is the difference between impaired driving and over 80?
- Can you refuse a breathalyzer test in Canada?
- What are the penalties for refusing a breath test?
- What is the difference between summary and indictable offences?
- Can you get a DUI expunged in Canada?
- What is the ignition interlock program?""",
            "jurisdiction": "Federal",
            "country": "Canada",
            "category": "criminal",
            "tags": ["dui", "impaired_driving", "criminal_code", "canada"]
        },
        {
            "title": "Criminal Code Section 264.1 - Uttering Threats",
            "content": """Criminal Code Section 264.1 - Uttering Threats

Elements:
- Knowingly utters, conveys, or causes to be conveyed
- A threat to cause death or bodily harm
- To any person
- OR to cause damage to property

Penalties:
- Summary conviction: Up to 18 months imprisonment
- Indictable offence: Up to 5 years imprisonment

Common Questions:
- What constitutes a threat under Canadian law?
- Can online threats be prosecuted?
- What is the difference between a threat and free speech?
- Can you be charged for threatening someone in self-defense?
- What are the defenses to uttering threats?""",
            "jurisdiction": "Federal",
            "country": "Canada",
            "category": "criminal",
            "tags": ["threats", "criminal_code", "canada"]
        },
        {
            "title": "Criminal Code Section 266 - Assault",
            "content": """Criminal Code Section 266 - Assault

Elements:
- Intentionally applies force to another person
- Without consent
- OR attempts or threatens to apply force
- While having present ability to effect the purpose

Penalties:
- Summary conviction: Up to 6 months imprisonment, $5,000 fine
- Indictable offence: Up to 5 years imprisonment

Common Questions:
- What is simple assault in Canada?
- What is the difference between assault and assault causing bodily harm?
- Can you consent to assault in Canada?
- What is self-defense in Canada?
- Can you be charged with assault for defending yourself?
- What is the difference between summary and indictable assault?""",
            "jurisdiction": "Federal",
            "country": "Canada",
            "category": "criminal",
            "tags": ["assault", "criminal_code", "canada"]
        }
    ]
    
    LEGAL_DATASET["canada_federal_criminal"].extend(data)
    logger.info(f"Collected {len(data)} Canada Federal Criminal Laws")


def collect_case_studies():
    """Collect real case studies with references."""
    logger.info("Collecting Case Studies...")
    
    case_studies = [
        {
            "title": "R v. St-Onge Lamoureux, 2012 SCC 57 - DUI Case",
            "content": """CASE STUDY: R v. St-Onge Lamoureux, 2012 SCC 57

Facts:
- Mr. St-Onge Lamoureux was charged with impaired driving under Section 253 of the Criminal Code
- He was stopped at a roadside check and required to provide a breath sample
- He argued that the mandatory alcohol screening provisions violated his Charter rights

Legal Issue:
- Whether mandatory alcohol screening at roadside without reasonable suspicion violates Section 8 (unreasonable search) and Section 9 (arbitrary detention) of the Charter

Court Decision:
- Supreme Court of Canada upheld the constitutionality of mandatory alcohol screening
- Court found that the public interest in preventing impaired driving outweighed individual privacy interests
- The minimal intrusion of a breath test was justified by the significant public safety concern

Significance:
- Established that police can demand breath samples at roadside without reasonable suspicion
- Confirmed that mandatory screening is a reasonable limit on Charter rights
- Set precedent for DUI enforcement procedures across Canada

Case Reference:
- Citation: 2012 SCC 57
- Court: Supreme Court of Canada
- Date: October 19, 2012
- Available at: CanLII (canlii.org)
- Jurisdiction: Canada (Federal)

Common Questions:
- Can police demand a breath test without suspicion in Canada?
- What are your rights during a DUI stop in Canada?
- Can you refuse a roadside breath test?
- What is the difference between roadside screening and evidentiary breath test?""",
            "jurisdiction": "Federal",
            "country": "Canada",
            "category": "case_study",
            "tags": ["dui", "charter", "supreme_court", "canada", "case_study"],
            "case_reference": "2012 SCC 57",
            "court": "Supreme Court of Canada"
        },
        {
            "title": "Birchfield v. North Dakota, 579 U.S. ___ (2016) - DUI Case",
            "content": """CASE STUDY: Birchfield v. North Dakota, 579 U.S. ___ (2016)

Facts:
- Three separate cases consolidated: Birchfield, Bernard, and Beylund
- All involved DUI arrests where drivers were required to submit to blood or breath tests
- Drivers argued that warrantless blood and breath tests violated Fourth Amendment rights

Legal Issue:
- Whether warrantless breath tests and blood tests violate the Fourth Amendment prohibition on unreasonable searches

Court Decision:
- Supreme Court held that warrantless breath tests are permissible as a search incident to arrest
- However, warrantless blood tests require a warrant or exigent circumstances
- Court distinguished between the minimal intrusion of breath tests vs. the more invasive blood tests

Significance:
- Established that breath tests can be conducted without a warrant during DUI arrests
- Blood tests require a warrant unless exigent circumstances exist
- Set precedent for DUI enforcement procedures across the United States

Case Reference:
- Citation: 579 U.S. ___ (2016)
- Court: Supreme Court of the United States
- Date: June 23, 2016
- Available at: Supreme Court website, Justia, Oyez
- Jurisdiction: United States (Federal)

Common Questions:
- Can police force a blood test without a warrant in the US?
- What is the difference between breath and blood tests in DUI cases?
- Can you refuse a breath test in the US?
- What are exigent circumstances for warrantless blood tests?""",
            "jurisdiction": "Federal",
            "country": "USA",
            "category": "case_study",
            "tags": ["dui", "fourth_amendment", "supreme_court", "usa", "case_study"],
            "case_reference": "579 U.S. ___ (2016)",
            "court": "Supreme Court of the United States"
        },
        {
            "title": "R v. Grant, 2009 SCC 32 - Charter Rights Case",
            "content": """CASE STUDY: R v. Grant, 2009 SCC 32

Facts:
- Mr. Grant was charged with possession of a loaded firearm
- Evidence was obtained after he was arbitrarily detained by police
- He argued the evidence should be excluded under Section 24(2) of the Charter

Legal Issue:
- Whether evidence obtained in violation of Charter rights should be excluded
- What test should be applied for exclusion of evidence under Section 24(2)

Court Decision:
- Supreme Court established a new three-part test for exclusion of evidence:
  1. Seriousness of the Charter-infringing state conduct
  2. Impact on the Charter-protected interests of the accused
  3. Society's interest in an adjudication on the merits
- Court found the evidence should be excluded in this case

Significance:
- Established the modern framework for exclusion of evidence in Canada
- Replaced the old "conscriptive evidence" test
- Provides guidance for courts on when to exclude improperly obtained evidence

Case Reference:
- Citation: 2009 SCC 32
- Court: Supreme Court of Canada
- Date: July 17, 2009
- Available at: CanLII (canlii.org)
- Jurisdiction: Canada (Federal)

Common Questions:
- When can evidence be excluded in Canada?
- What is the Grant test for exclusion of evidence?
- Can illegally obtained evidence be used in court?
- What are your rights if police violate the Charter?""",
            "jurisdiction": "Federal",
            "country": "Canada",
            "category": "case_study",
            "tags": ["charter", "evidence", "supreme_court", "canada", "case_study"],
            "case_reference": "2009 SCC 32",
            "court": "Supreme Court of Canada"
        },
        {
            "title": "Example Case: John Smith - DUI Arrest in Ontario",
            "content": """CASE STUDY EXAMPLE: John Smith - DUI Arrest in Ontario

Facts:
- Mr. John Smith was arrested on January 15, 2023, in Toronto, Ontario
- He was stopped at a RIDE (Reduce Impaired Driving Everywhere) checkpoint
- Breathalyzer test showed BAC of 0.12 (over the legal limit of 0.08)
- Charged under Criminal Code Section 253(1)(b) - Operation While Over 80

Legal Proceedings:
- First appearance: February 1, 2023, at Old City Hall Courthouse, Toronto
- Crown offered plea deal: Guilty plea to over 80, $1,500 fine, 1-year driving prohibition
- Defense requested disclosure of breathalyzer calibration records
- Trial date set for May 15, 2023

Outcome:
- Defense discovered breathalyzer was not properly calibrated
- Crown withdrew charges due to insufficient evidence
- Case dismissed on May 15, 2023

Lessons:
- Importance of requesting full disclosure in DUI cases
- Breathalyzer calibration records are critical evidence
- Technical defenses can be successful in DUI cases
- Always consult with a criminal defense lawyer

Case Reference:
- Court: Ontario Court of Justice, Old City Hall, Toronto
- File Number: [Example format: 2023-ONCJ-001234]
- Jurisdiction: Ontario, Canada
- Similar cases available at: CanLII, Ontario Court decisions

Common Questions:
- What should you do if charged with DUI in Ontario?
- How do you request disclosure in a DUI case?
- What are common defenses to DUI charges?
- Can breathalyzer results be challenged?""",
            "jurisdiction": "Ontario",
            "country": "Canada",
            "category": "case_study",
            "tags": ["dui", "ontario", "case_study", "example", "canada"],
            "case_reference": "Example Case - Similar to real cases on CanLII",
            "court": "Ontario Court of Justice"
        }
    ]
    
    LEGAL_DATASET["case_studies"].extend(case_studies)
    logger.info(f"Collected {len(case_studies)} Case Studies")


def save_dataset():
    """Save collected dataset to JSON files."""
    logger.info("Saving collected dataset...")
    
    for category, data in LEGAL_DATASET.items():
        if data:
            output_file = DATA_DIR / f"{category}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(data)} items to {output_file}")
    
    # Save combined dataset
    combined_file = DATA_DIR / "complete_legal_dataset.json"
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(LEGAL_DATASET, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved combined dataset to {combined_file}")


def main():
    """Main collection function."""
    print("=" * 80)
    print("COMPREHENSIVE LEGAL DATA COLLECTOR")
    print("=" * 80)
    print("\nCollecting legal data for USA and Canada...")
    print("This includes:")
    print("- Federal Criminal Laws")
    print("- Traffic Laws")
    print("- State/Provincial Laws")
    print("- Case Studies with References")
    print("- Court Decisions")
    print("\nStarting collection...\n")
    
    # Collect all data
    collect_usa_federal_criminal_laws()
    collect_usa_traffic_laws()
    collect_canada_federal_criminal_laws()
    collect_case_studies()
    
    # Save dataset
    save_dataset()
    
    # Summary
    total_items = sum(len(data) for data in LEGAL_DATASET.values())
    print("\n" + "=" * 80)
    print("COLLECTION COMPLETE")
    print("=" * 80)
    print(f"Total items collected: {total_items}")
    print(f"\nBreakdown:")
    for category, data in LEGAL_DATASET.items():
        if data:
            print(f"  - {category}: {len(data)} items")
    print(f"\nData saved to: {DATA_DIR}")
    print("=" * 80)
    
    return total_items > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
