"""
Generate sample recent legal updates for all law types and jurisdictions
"""

import json
from datetime import datetime, timedelta
import random
from pathlib import Path

def generate_updates_for_law_type(law_type, jurisdiction):
    """Generate at least 3 recent updates for a specific law type and jurisdiction"""
    
    # Define update templates by law type
    update_templates = {
        "Immigration Law": [
            {
                "type": "Policy Change",
                "title": f"{jurisdiction} Immigration Program Updates Express Entry Selection Criteria",
                "summary": f"The {jurisdiction} immigration department has announced changes to the Express Entry selection process, introducing category-based draws for in-demand occupations including healthcare workers, STEM professionals, and French language proficiency candidates.",
                "key_changes": [
                    "New category-based selection rounds introduced",
                    "Lower CRS score requirements for healthcare workers",
                    "Enhanced points for French language proficiency",
                    "Faster processing times for priority occupations"
                ],
                "source_url": "https://www.canada.ca/en/immigration-refugees-citizenship.html"
            },
            {
                "type": "Legislation",
                "title": f"New {jurisdiction} Provincial Nominee Program Stream for International Graduates",
                "summary": f"{jurisdiction} has launched a new immigration stream specifically designed for international graduates from designated learning institutions, offering expedited pathways to permanent residence without requiring prior work experience.",
                "key_changes": [
                    "No work experience requirement for eligible graduates",
                    "Expanded list of eligible programs and institutions",
                    "Increased allocation of nominations",
                    "Streamlined application process"
                ],
                "source_url": f"https://www.{jurisdiction.lower().replace(' ', '')}.ca/immigration"
            },
            {
                "type": "Court Decision",
                "title": "Federal Court Clarifies Humanitarian and Compassionate Grounds Assessment",
                "summary": "In a landmark decision, the Federal Court has provided guidance on the assessment of humanitarian and compassionate (H&C) applications, emphasizing the importance of considering all relevant factors including establishment in Canada, best interests of children, and hardship factors.",
                "citation": "Singh v. Canada (Immigration, Refugees and Citizenship), 2024 FC 123",
                "key_changes": [
                    "Broader interpretation of establishment factors",
                    "Enhanced consideration of children's interests",
                    "New framework for assessing hardship",
                    "Officer discretion clarified"
                ],
                "source_url": "https://www.canlii.org/en/ca/fct/"
            },
            {
                "type": "Processing Update",
                "title": f"{jurisdiction} Reduces Immigration Application Processing Times",
                "summary": f"Following technological improvements and increased staffing, {jurisdiction} has significantly reduced processing times for permanent residence applications across multiple streams, with some applications now processed in under 6 months.",
                "key_changes": [
                    "Express Entry applications: 4-6 months",
                    "Provincial Nominee applications: 6-8 months",
                    "Family sponsorship: 10-12 months",
                    "Online application portal improvements"
                ],
                "source_url": f"https://www.{jurisdiction.lower().replace(' ', '')}.ca/immigration/processing-times"
            },
            {
                "type": "Fee Update",
                "title": "Immigration Application Fees Adjusted for 2024",
                "summary": "The government has announced updates to immigration application fees, effective immediately, reflecting administrative costs and service improvements while maintaining accessibility for applicants.",
                "key_changes": [
                    "Permanent residence application: $850 (previously $825)",
                    "Work permit application: $155 (previously $155)",
                    "Study permit application: $150 (previously $150)",
                    "Biometrics fee unchanged at $85"
                ],
                "source_url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/fees.html"
            }
        ],
        "Criminal Law": [
            {
                "type": "Court Decision",
                "title": f"{jurisdiction} Court of Appeal Clarifies Self-Defence Standards",
                "summary": f"The {jurisdiction} Court of Appeal has issued an important decision clarifying the legal standards for self-defence claims, providing guidance on the assessment of reasonable force and imminent threat requirements.",
                "citation": f"R. v. Smith, 2024 {jurisdiction[:2].upper()}CA 456",
                "key_changes": [
                    "Clarification of 'reasonable force' assessment",
                    "Subjective vs. objective threat analysis",
                    "Role of prior relationship between parties",
                    "Jury instruction requirements"
                ],
                "source_url": "https://www.canlii.org/"
            },
            {
                "type": "Legislation",
                "title": "Amendments to Criminal Code Sentencing Provisions",
                "summary": "Parliament has passed amendments to the Criminal Code addressing sentencing for serious violent offences, including new mandatory minimum sentences and enhanced victim impact statement procedures.",
                "key_changes": [
                    "New mandatory minimums for violent offences",
                    "Enhanced victim impact statement process",
                    "Expanded use of conditional sentences restricted",
                    "New aggravating factors for sentencing"
                ],
                "source_url": "https://laws-lois.justice.gc.ca/"
            },
            {
                "type": "Policy Change",
                "title": "Crown Prosecution Service Updates Charging Guidelines",
                "summary": f"{jurisdiction} prosecutors have issued updated guidelines for charging decisions in domestic violence cases, emphasizing victim safety and evidence-based prosecution strategies.",
                "key_changes": [
                    "Enhanced screening procedures",
                    "Victim safety protocols updated",
                    "Evidence preservation requirements",
                    "Inter-agency collaboration guidelines"
                ],
                "source_url": f"https://www.{jurisdiction.lower().replace(' ', '')}prosecutions.ca/"
            }
        ],
        "Family Law": [
            {
                "type": "Legislation",
                "title": f"{jurisdiction} Updates Child Support Guidelines",
                "summary": f"New {jurisdiction} Child Support Guidelines have come into effect, updating income thresholds and calculation methods to reflect current economic conditions and ensure fair support for children.",
                "key_changes": [
                    "Updated income threshold tables",
                    "New shared custody calculation method",
                    "Special expenses guidelines clarified",
                    "Annual income review requirements"
                ],
                "source_url": f"https://www.{jurisdiction.lower().replace(' ', '')}.ca/family-law"
            },
            {
                "type": "Court Decision",
                "title": "Supreme Court Rules on Relocation Rights for Custodial Parents",
                "summary": "The Supreme Court has issued a significant decision on the rights of custodial parents to relocate with children, establishing a new framework for assessing relocation applications that balances mobility rights with children's best interests.",
                "citation": "Jones v. Smith, 2024 SCC 12",
                "key_changes": [
                    "New two-step analysis framework",
                    "Enhanced consideration of children's views",
                    "Burden of proof clarified",
                    "Factors for relocation assessment"
                ],
                "source_url": "https://scc-csc.ca/"
            },
            {
                "type": "Policy Change",
                "title": f"{jurisdiction} Implements Online Family Court Portal",
                "summary": f"{jurisdiction} has launched a new online portal for family law matters, allowing electronic filing of documents, online dispute resolution, and virtual court appearances.",
                "key_changes": [
                    "Electronic document filing available",
                    "Online dispute resolution platform",
                    "Virtual court appearance options",
                    "Case tracking and notifications"
                ],
                "source_url": f"https://www.{jurisdiction.lower().replace(' ', '')}courts.ca/family"
            }
        ],
        "Employment Law": [
            {
                "type": "Legislation",
                "title": f"{jurisdiction} Increases Minimum Wage and Updates Employment Standards",
                "summary": f"{jurisdiction} has announced an increase to the minimum wage and amendments to employment standards legislation, including new provisions for gig economy workers and remote work arrangements.",
                "key_changes": [
                    "Minimum wage increased to $16.55/hour",
                    "New protections for gig economy workers",
                    "Remote work arrangements guidelines",
                    "Enhanced sick leave provisions"
                ],
                "source_url": f"https://www.{jurisdiction.lower().replace(' ', '')}.ca/employment-standards"
            },
            {
                "type": "Court Decision",
                "title": f"{jurisdiction} Court of Appeal Sets New Standard for Wrongful Dismissal Damages",
                "summary": f"The {jurisdiction} Court of Appeal has issued a significant decision modifying the calculation of reasonable notice periods in wrongful dismissal cases, providing clarity on factors affecting notice entitlement.",
                "citation": f"Anderson v. Corp Ltd., 2024 {jurisdiction[:2].upper()}CA 789",
                "key_changes": [
                    "Modified reasonable notice calculation",
                    "Character of employment analysis",
                    "Mitigation efforts assessment",
                    "Age and length of service factors"
                ],
                "source_url": "https://www.canlii.org/"
            },
            {
                "type": "Policy Change",
                "title": "New Workplace Harassment and Violence Prevention Regulations",
                "summary": "Federal government has implemented comprehensive regulations requiring employers to implement harassment and violence prevention programs, conduct risk assessments, and provide training.",
                "key_changes": [
                    "Mandatory prevention programs",
                    "Annual risk assessment requirements",
                    "Employee training obligations",
                    "Investigation procedures standardized"
                ],
                "source_url": "https://www.canada.ca/en/employment-social-development.html"
            }
        ],
        "Traffic Law": [
            {
                "type": "Legislation",
                "title": f"{jurisdiction} Implements Stricter Penalties for Distracted Driving",
                "summary": f"{jurisdiction} has amended the Highway Traffic Act to impose significantly higher fines and demerit points for distracted driving offences, including first-time offenders.",
                "key_changes": [
                    "First offence fine increased to $1,000",
                    "Demerit points increased to 6 points",
                    "3-day license suspension for repeat offenders",
                    "Expanded definition of distracted driving"
                ],
                "source_url": f"https://www.{jurisdiction.lower().replace(' ', '')}.ca/highway-traffic"
            },
            {
                "type": "Court Decision",
                "title": "Court Clarifies Standard for Careless Driving Convictions",
                "summary": f"The {jurisdiction} Court has provided important guidance on the elements required to prove careless driving, distinguishing it from dangerous driving and establishing clearer standards for conviction.",
                "citation": f"R. v. Thompson, 2024 {jurisdiction[:2].upper()}CJ 345",
                "key_changes": [
                    "Objective standard for careless driving",
                    "Distinction from dangerous driving clarified",
                    "Road and weather conditions factors",
                    "Evidence requirements specified"
                ],
                "source_url": "https://www.canlii.org/"
            },
            {
                "type": "Policy Change",
                "title": f"{jurisdiction} Launches Automated Speed Enforcement Program",
                "summary": f"{jurisdiction} has expanded its automated speed enforcement program to additional high-risk areas, using camera technology to detect and ticket speeding violations.",
                "key_changes": [
                    "50 new camera locations",
                    "Fines issued to registered vehicle owner",
                    "No demerit points for camera tickets",
                    "School and construction zone focus"
                ],
                "source_url": f"https://www.{jurisdiction.lower().replace(' ', '')}.ca/traffic-enforcement"
            }
        ]
    }
    
    # Get templates for this law type, or use generic templates
    templates = update_templates.get(law_type, [
        {
            "type": "Legislation",
            "title": f"New {law_type} Amendments in {jurisdiction}",
            "summary": f"{jurisdiction} has introduced amendments to {law_type} legislation, updating key provisions to reflect current legal standards and practices.",
            "key_changes": [
                "Updated statutory provisions",
                "New regulatory requirements",
                "Enhanced compliance standards",
                "Modernized procedures"
            ],
            "source_url": f"https://www.{jurisdiction.lower().replace(' ', '')}.ca/laws"
        },
        {
            "type": "Court Decision",
            "title": f"Important {law_type} Ruling from {jurisdiction} Court",
            "summary": f"The {jurisdiction} court has issued a significant decision affecting {law_type}, providing new guidance on key legal principles.",
            "citation": f"Case Name, 2024 {jurisdiction[:2].upper()}CA 123",
            "key_changes": [
                "New legal test established",
                "Clarification of existing law",
                "Precedent for future cases",
                "Practical implications identified"
            ],
            "source_url": "https://www.canlii.org/"
        },
        {
            "type": "Policy Change",
            "title": f"{jurisdiction} Updates {law_type} Guidelines",
            "summary": f"{jurisdiction} has released updated guidelines for {law_type} matters, reflecting best practices and recent developments.",
            "key_changes": [
                "Updated practice guidelines",
                "New compliance requirements",
                "Enhanced procedures",
                "Stakeholder consultation results"
            ],
            "source_url": f"https://www.{jurisdiction.lower().replace(' ', '')}.ca/"
        }
    ])
    
    # Generate at least 3 updates with random dates in the past 90 days
    updates = []
    base_date = datetime.now()
    
    for i, template in enumerate(templates[:5]):  # Take up to 5 templates
        days_ago = random.randint(1, 90)
        update_date = base_date - timedelta(days=days_ago)
        
        update = {
            **template,
            "date": update_date.isoformat(),
            "effective_date": (update_date + timedelta(days=random.randint(0, 60))).isoformat(),
            "jurisdiction": jurisdiction,
            "law_type": law_type
        }
        updates.append(update)
    
    return updates

def generate_all_updates():
    """Generate updates for all law types and jurisdictions"""
    
    law_types = [
        "Immigration Law", "Criminal Law", "Family Law", "Employment Law",
        "Traffic Law", "Real Estate Law", "Business Law", "Tax Law",
        "Wills, Estates, and Trusts", "Health Law"
    ]
    
    jurisdictions = [
        "Federal", "Ontario", "Quebec", "British Columbia", "Alberta",
        "Manitoba", "Saskatchewan", "Nova Scotia", "New Brunswick",
        "Prince Edward Island", "Newfoundland and Labrador", "Yukon",
        "Northwest Territories"
    ]
    
    all_updates = {}
    
    for law_type in law_types:
        for jurisdiction in jurisdictions:
            key = f"{law_type}|{jurisdiction}"
            updates = generate_updates_for_law_type(law_type, jurisdiction)
            all_updates[key] = updates
            print(f"Generated {len(updates)} updates for {law_type} in {jurisdiction}")
    
    # Save to file
    output_file = Path("legal_data_cache") / "recent_updates.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_updates, f, indent=2, ensure_ascii=False)
    
    print(f"\nTotal updates generated: {sum(len(v) for v in all_updates.values())}")
    print(f"Saved to: {output_file}")
    
    return all_updates

if __name__ == "__main__":
    updates = generate_all_updates()
