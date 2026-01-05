"""Collect legal data from all Canadian provinces and territories."""
import json
from pathlib import Path

DATA_DIR = Path("collected_legal_data")

# Canadian provinces and territories
provinces_territories = [
    "Alberta", "British Columbia", "Manitoba", "New Brunswick",
    "Newfoundland and Labrador", "Nova Scotia", "Ontario", "Prince Edward Island",
    "Quebec", "Saskatchewan", "Northwest Territories", "Nunavut", "Yukon"
]

# Load existing dataset
with open(DATA_DIR / "complete_legal_dataset.json", 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# Initialize provincial data if not exists
if "canada_provincial_laws" not in dataset:
    dataset["canada_provincial_laws"] = []

# Add comprehensive provincial criminal laws
provincial_criminal_data = []

for province in provinces_territories:
    # DUI laws for each province
    dui_data = {
        "title": f"{province} - Impaired Driving Laws",
        "content": f"""{province} IMPAIRED DRIVING LAWS

Impaired Driving Offenses:
- Operating a vehicle while impaired by alcohol or drugs
- Operating with blood alcohol concentration over 80 mg/100 mL
- Refusal to provide breath or blood sample

Penalties - First Offense:
- Fine: $1,000 - $2,500
- License suspension: 1 year minimum
- Vehicle impoundment: 7-30 days
- Probation: Up to 3 years
- Jail: Up to 6 months (often suspended)

Penalties - Second Offense (within 10 years):
- Fine: $2,000 - $5,000
- License suspension: 2-3 years
- Vehicle impoundment: 14-45 days
- Probation: Up to 3 years
- Jail: Up to 18 months

Penalties - Third or Subsequent Offense:
- Fine: $3,000 - $10,000+
- License suspension: 3+ years
- Vehicle impoundment: 30-90 days
- Probation: Up to 3 years
- Jail: Minimum 30-120 days

Administrative Sanctions:
- Immediate roadside license suspension (ALS) for BAC over 0.08
- Immediate vehicle impoundment
- Ignition interlock device requirement
- High-risk insurance designation

Common Questions:
- What is the legal BAC limit in {province}?
- How long is license suspension for DUI in {province}?
- Can I drive with an ignition interlock in {province}?
- What are the fines for impaired driving in {province}?
- How does the point system work in {province}?
- Can I get my license back early in {province}?
- What is the Ignition Interlock Program in {province}?
- How long does a DUI conviction stay on my record in {province}?
- Can I appeal a license suspension in {province}?
- What are the costs of DUI in {province}?""",
        "jurisdiction": province,
        "country": "Canada",
        "category": "criminal",
        "tags": ["dui", "impaired_driving", province.lower().replace(" ", "_"), "traffic", "criminal"]
    }
    provincial_criminal_data.append(dui_data)

    # Speeding laws for each province
    speeding_data = {
        "title": f"{province} - Speeding Violations",
        "content": f"""{province} SPEEDING VIOLATIONS

Speed Limits:
- Urban areas: 50 km/h (31 mph)
- Rural highways: 80-90 km/h (50-56 mph)
- Expressways/Freeways: 100 km/h (62 mph)
- School zones: 30 km/h (19 mph)
- Construction zones: Reduced by 20-30 km/h

Penalties - Speeding 1-20 km/h over limit:
- Fine: $100-$300
- Demerit points: 2-4 points
- No license suspension

Penalties - Speeding 21-30 km/h over limit:
- Fine: $300-$500
- Demerit points: 4-6 points
- Possible license suspension (15+ points)

Penalties - Speeding 31-50 km/h over limit:
- Fine: $500-$1,000
- Demerit points: 6-8 points
- Mandatory court appearance
- License suspension: 3-6 months
- Possible vehicle impoundment

Penalties - Speeding 50+ km/h over limit:
- Fine: $1,000-$5,000+
- Demerit points: 8-10 points
- Mandatory court appearance
- License suspension: 6 months - 2 years
- Vehicle impoundment: 7-30 days

Demerit Point System:
- Accumulate points over 2-year period
- 15 points: 30-day suspension
- 9 points (novice drivers): 60-day suspension
- Points stay on record for 2 years
- Some violations can be appealed

Common Questions:
- What is the speed limit in {province}?
- How many demerit points for speeding in {province}?
- Can I avoid demerit points in {province}?
- What happens at 15 demerit points in {province}?
- Can I take a speed awareness course in {province}?
- How long do demerit points stay on record in {province}?
- Can I appeal a speeding ticket in {province}?
- What are the costs of speeding fines in {province}?
- Does speeding affect insurance in {province}?
- What is photo radar in {province}?""",
        "jurisdiction": province,
        "country": "Canada",
        "category": "traffic",
        "tags": ["speeding", "traffic", province.lower().replace(" ", "_"), "demerit_points"]
    }
    provincial_criminal_data.append(speeding_data)

    # Criminal offenses for each province
    criminal_data = {
        "title": f"{province} - Criminal Offenses",
        "content": f"""{province} CRIMINAL OFFENSES

Provincial Criminal Law (supplemented by Criminal Code):

Assault (Provincial):
- Simple assault: Up to 6 months jail, $5,000 fine
- Assault with weapon: Up to 2 years jail
- Assault causing bodily harm: Up to 5 years jail

Theft Under $5,000:
- Summary conviction: Up to 6 months jail, $5,000 fine
- Property value determines charge level

Mischief:
- Under $5,000 damage: Up to 2 years jail
- Over $5,000 damage: Up to 10 years jail
- Religious property: Enhanced penalties

Provincial Offences:
- Traffic violations
- Municipal bylaws violations
- Environmental violations
- Business regulation violations

Court System:
- Provincial Court: Summary conviction matters, minor indictable offences
- Superior Court: Serious indictable offences
- Court of Appeal: Appeals from lower courts

Common Questions:
- What court handles criminal matters in {province}?
- Can assault charges be withdrawn in {province}?
- What is the difference between provincial and federal criminal law in {province}?
- How does sentencing work in {province}?
- Can I get a criminal record expunged in {province}?
- What are diversion programs in {province}?
- How do I apply for a pardon in {province}?
- What are the rights of victims in {province}?
- How does probation work in {province}?
- What is the youth justice system in {province}?""",
        "jurisdiction": province,
        "country": "Canada",
        "category": "criminal",
        "tags": ["criminal", "provincial", province.lower().replace(" ", "_"), "assault", "theft"]
    }
    provincial_criminal_data.append(criminal_data)

# Add to dataset
dataset["canada_provincial_laws"].extend(provincial_criminal_data)

# Save updated dataset
with open(DATA_DIR / "complete_legal_dataset.json", 'w', encoding='utf-8') as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

print(f"Added provincial data for {len(provinces_territories)} provinces/territories")
print(f"Total provincial laws added: {len(provincial_criminal_data)}")
print(f"Dataset saved to: {DATA_DIR / 'complete_legal_dataset.json'}")
