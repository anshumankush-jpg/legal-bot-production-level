"""Expand legal dataset with comprehensive laws for USA and Canada."""
import json
from pathlib import Path

DATA_DIR = Path("collected_legal_data")

# Load existing dataset
with open(DATA_DIR / "complete_legal_dataset.json", 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# Add more comprehensive USA Federal Criminal Laws
additional_usa_federal = [
    {
        "title": "18 U.S.C. § 922 - Firearms Offenses",
        "content": """18 U.S.C. § 922 - Unlawful Acts (Firearms)

Elements:
- Ship, transport, or receive firearms in interstate commerce
- By a person prohibited from possessing firearms
- OR in violation of various federal firearms regulations

Prohibited Persons Include:
- Convicted felons
- Fugitives from justice
- Unlawful users of controlled substances
- Persons adjudicated as mentally defective
- Illegal aliens
- Persons dishonorably discharged from military

Penalties:
- Fine up to $250,000
- Imprisonment up to 10 years
- Or both

Common Questions:
- Who is prohibited from owning firearms?
- What is the difference between federal and state gun laws?
- Can you transport firearms across state lines?
- What is a straw purchase of a firearm?
- What are the penalties for illegal gun possession?""",
        "jurisdiction": "Federal",
        "country": "USA",
        "category": "criminal",
        "tags": ["firearms", "guns", "federal", "criminal"]
    },
    {
        "title": "18 U.S.C. § 2113 - Bank Robbery",
        "content": """18 U.S.C. § 2113 - Bank Robbery and Incidental Crimes

Elements:
- By force, violence, or intimidation
- Takes or attempts to take
- From person or presence of another
- Property or money belonging to a bank, credit union, or savings and loan

Penalties:
- Bank robbery: Up to 20 years imprisonment
- Bank robbery with dangerous weapon: Up to 25 years
- Bank robbery resulting in death: Up to life imprisonment or death

Common Questions:
- What constitutes bank robbery?
- What is the difference between robbery and theft?
- Can you be charged federally for robbing a bank?
- What are the penalties for bank robbery?
- What is the difference between armed and unarmed bank robbery?""",
        "jurisdiction": "Federal",
        "country": "USA",
        "category": "criminal",
        "tags": ["robbery", "bank", "federal", "criminal"]
    },
    {
        "title": "18 U.S.C. § 242 - Deprivation of Rights Under Color of Law",
        "content": """18 U.S.C. § 242 - Deprivation of Rights Under Color of Law

Elements:
- Under color of any law, statute, ordinance, regulation, or custom
- Willfully subjects any person
- To the deprivation of any rights, privileges, or immunities
- Secured or protected by the Constitution or laws of the United States

Penalties:
- Basic violation: Fine, imprisonment up to 1 year, or both
- Bodily injury: Fine, imprisonment up to 10 years, or both
- Death or sexual abuse: Fine, imprisonment for any term of years or life, or death

Common Questions:
- What is a civil rights violation?
- Can police be charged under this statute?
- What is "under color of law"?
- What are examples of deprivation of rights?
- What is the difference between Section 242 and Section 1983?""",
        "jurisdiction": "Federal",
        "country": "USA",
        "category": "criminal",
        "tags": ["civil_rights", "police", "federal", "criminal"]
    }
]

# Add more Canada Criminal Laws
additional_canada_criminal = [
    {
        "title": "Criminal Code Section 267 - Assault with Weapon",
        "content": """Criminal Code Section 267 - Assault with Weapon or Causing Bodily Harm

Elements:
- Commits assault
- While carrying, using, or threatening to use a weapon or imitation weapon
- OR causes bodily harm to the complainant

Penalties:
- Summary conviction: Up to 18 months imprisonment, $5,000 fine
- Indictable offence: Up to 10 years imprisonment

Common Questions:
- What is assault with a weapon?
- What constitutes a weapon under Canadian law?
- What is the difference between assault and assault causing bodily harm?
- Can fists be considered a weapon?
- What are the penalties for assault with a weapon?""",
        "jurisdiction": "Federal",
        "country": "Canada",
        "category": "criminal",
        "tags": ["assault", "weapon", "criminal_code", "canada"]
    },
    {
        "title": "Criminal Code Section 279 - Kidnapping",
        "content": """Criminal Code Section 279 - Kidnapping

Elements:
- Unlawfully confines, imprisons, or forcibly seizes
- Another person
- Without lawful authority

Penalties:
- Summary conviction: Up to 18 months imprisonment
- Indictable offence: Up to life imprisonment

Common Questions:
- What is kidnapping in Canada?
- What is the difference between kidnapping and unlawful confinement?
- Can a parent be charged with kidnapping their own child?
- What are the penalties for kidnapping?
- What is the difference between kidnapping and abduction?""",
        "jurisdiction": "Federal",
        "country": "Canada",
        "category": "criminal",
        "tags": ["kidnapping", "criminal_code", "canada"]
    }
]

# Add more case studies
additional_case_studies = [
    {
        "title": "Missouri v. McNeely, 569 U.S. 141 (2013) - DUI Blood Test",
        "content": """CASE STUDY: Missouri v. McNeely, 569 U.S. 141 (2013)

Facts:
- Mr. McNeely was stopped for speeding and suspected DUI
- He refused a breath test
- Police took him to a hospital and drew blood without a warrant
- He argued the warrantless blood draw violated his Fourth Amendment rights

Legal Issue:
- Whether the natural metabolization of alcohol in the bloodstream creates a per se exigency justifying warrantless blood tests

Court Decision:
- Supreme Court held that the natural dissipation of alcohol does not create a per se exigency
- Police must obtain a warrant for blood tests unless true exigent circumstances exist
- Each case must be evaluated on its specific facts

Significance:
- Established that warrantless blood tests require actual exigent circumstances
- Cannot rely solely on natural dissipation of alcohol as exigency
- Set precedent requiring warrants for most blood draws in DUI cases

Case Reference:
- Citation: 569 U.S. 141 (2013)
- Court: Supreme Court of the United States
- Date: April 17, 2013
- Available at: Supreme Court website, Justia, Oyez
- Jurisdiction: United States (Federal)

Common Questions:
- When can police draw blood without a warrant?
- What are exigent circumstances for blood tests?
- Can you refuse a blood test in the US?
- What is the difference between breath and blood tests?""",
        "jurisdiction": "Federal",
        "country": "USA",
        "category": "case_study",
        "tags": ["dui", "fourth_amendment", "blood_test", "supreme_court", "usa"],
        "case_reference": "569 U.S. 141 (2013)",
        "court": "Supreme Court of the United States"
    }
]

# Add to dataset
dataset["usa_federal_criminal"].extend(additional_usa_federal)
dataset["canada_federal_criminal"].extend(additional_canada_criminal)
dataset["case_studies"].extend(additional_case_studies)

# Save updated dataset
with open(DATA_DIR / "complete_legal_dataset.json", 'w', encoding='utf-8') as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

print(f"Expanded dataset:")
print(f"  - USA Federal Criminal: {len(dataset['usa_federal_criminal'])} items")
print(f"  - Canada Federal Criminal: {len(dataset['canada_federal_criminal'])} items")
print(f"  - Case Studies: {len(dataset['case_studies'])} items")
print(f"\nDataset saved to: {DATA_DIR / 'complete_legal_dataset.json'}")
