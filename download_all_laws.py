"""Download ALL laws - criminal, traffic, divorce, civil, commercial, copyright, etc."""
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("all_laws_database")
DATA_DIR.mkdir(exist_ok=True)

# Comprehensive legal database
ALL_LAWS = {
    "constitutional": [],
    "criminal": [],
    "traffic": [],
    "commercial_vehicle": [],
    "family_law": [],
    "divorce": [],
    "civil_law": [],
    "contract": [],
    "tort": [],
    "property": [],
    "copyright": [],
    "content_owner": [],
    "trademark": [],
    "corporate": [],
    "employment": [],
    "tax": [],
    "bankruptcy": [],
    "environmental": [],
    "immigration": [],
    "health": [],
    "education": [],
    "consumer_protection": [],
    "privacy": [],
    "cyber_law": [],
    "antitrust": [],
    "international": [],
    "case_law": [],
    "regulations": []
}

# Add comprehensive laws
ALL_LAWS["divorce"].extend([
    {
        "title": "USA Divorce Laws - All States",
        "content": """USA DIVORCE LAWS - COMPREHENSIVE GUIDE

No-Fault Divorce (All 50 States):
- Irreconcilable differences
- Irretrievable breakdown
- Incompatibility
- Living separate and apart

Fault-Based Grounds:
- Adultery
- Abandonment (1+ years)
- Cruelty (physical or mental)
- Alcohol/drug abuse
- Criminal conviction
- Impotency
- Insanity

Residency Requirements by State:
- Alabama: 6 months
- Alaska: 30 days
- Arizona: 90 days
- Arkansas: 60 days
- California: 6 months
- Colorado: 90 days
- Connecticut: 12 months
- Delaware: 6 months
- Florida: 6 months
- Georgia: 6 months
- Hawaii: 6 months
- Idaho: 6 weeks
- Illinois: 90 days
- Indiana: 6 months
- Iowa: 1 year
- Kansas: 60 days
- Kentucky: 180 days
- Louisiana: 6 months
- Maine: 6 months
- Maryland: 1 year
- Massachusetts: 1 year
- Michigan: 180 days
- Minnesota: 180 days
- Mississippi: 6 months
- Missouri: 90 days
- Montana: 90 days
- Nebraska: 1 year
- Nevada: 6 weeks
- New Hampshire: 1 year
- New Jersey: 1 year
- New Mexico: 6 months
- New York: 1 year
- North Carolina: 6 months
- North Dakota: 6 months
- Ohio: 6 months
- Oklahoma: 6 months
- Oregon: 6 months
- Pennsylvania: 6 months
- Rhode Island: 1 year
- South Carolina: 1 year
- South Dakota: 1 year
- Tennessee: 6 months
- Texas: 6 months
- Utah: 3 months
- Vermont: 6 months
- Virginia: 6 months
- Washington: 90 days
- West Virginia: 1 year
- Wisconsin: 6 months
- Wyoming: 60 days

Property Division:
- Community Property States: AZ, CA, ID, LA, NV, NM, TX, WA, WI
  * Equal division of marital property
- Equitable Distribution States: All others
  * Fair but not necessarily equal division

Child Custody Factors:
- Best interests of child
- Child's age and health
- Parental fitness
- Stability and continuity
- Child's preferences (if mature enough)
- Geographic proximity
- Sibling relationships

Child Support Calculation:
- Income Shares Model (most states)
- Percentage of Income Model (some states)
- Melson Formula (DE, HI, MT)
- Based on: Both parents' income, number of children, custody arrangement

Spousal Support Types:
- Temporary: During divorce proceedings
- Rehabilitative: Short-term, for education/training
- Reimbursement: For sacrifices during marriage
- Permanent: Long-term or lifetime support
- Lump Sum: One-time payment

Common Questions:
- How long does divorce take?
- Do I need a lawyer?
- Can I get divorced without spouse's agreement?
- How is property divided?
- What is legal separation vs divorce?
- Can I change my name in divorce?
- What is mediation vs litigation?
- How does adultery affect divorce?
- Can I get alimony?
- How is child support calculated?""",
        "jurisdiction": "All States",
        "country": "USA",
        "category": "divorce",
        "tags": ["divorce", "family_law", "custody", "alimony"]
    },
    {
        "title": "Canada Divorce Act - Complete Guide",
        "content": """CANADA DIVORCE ACT - COMPREHENSIVE GUIDE

Grounds for Divorce:
- Breakdown of marriage (no-fault)
- Living separate and apart for one year (most common)
- Adultery
- Physical or mental cruelty

No-Fault Divorce:
- One-year separation required
- Mutual consent possible
- Unilateral possible after one year
- No need to prove fault

Residency Requirements:
- One spouse must be resident of Canada for at least one year
- Must be resident of province where filing
- Jurisdiction based on residence, not citizenship

Property Division by Province:
- Ontario: Equal division of net family property
- British Columbia: Equal division of family property
- Alberta: Equal division of matrimonial property
- Quebec: Partnership of acquests (civil law)
- Manitoba: Equal division of family assets
- Saskatchewan: Equal division of matrimonial property
- Nova Scotia: Equal division of matrimonial assets
- New Brunswick: Equal division of marital property
- Newfoundland: Equal division of matrimonial assets
- PEI: Equal division of matrimonial property
- NWT/Nunavut: Equal division of family property
- Yukon: Equal division of matrimonial property

Excluded Property:
- Property owned before marriage
- Inheritances (unless used for family)
- Gifts from third parties
- Property excluded by agreement
- Damages for personal injury

Child Custody:
- Best interests of child standard
- Maximum contact with both parents
- Joint custody increasingly common
- Sole custody when joint not in child's interest
- Factors: child's needs, parental capability, status quo

Child Support:
- Federal Child Support Guidelines
- Table amount based on income and number of children
- Special expenses: child care, health, education, extracurricular
- Extraordinary expenses: special needs, post-secondary education
- Shared custody: offset calculation
- Split custody: separate calculations

Spousal Support:
- Compensatory support: For economic disadvantages
- Needs-based support: For financial need
- Length depends on marriage duration
- Can be indefinite for long marriages
- Taxable to recipient, deductible to payor

Common Questions:
- How long do you have to be separated before divorce?
- How is property divided in Canadian divorce?
- What is the difference between common law and married?
- Can you get divorced without a lawyer?
- What is the process for uncontested divorce?
- How long does divorce take in Canada?
- Can same-sex couples divorce?
- What is the role of mediators?
- How does spousal support work?
- Can I change my name after divorce?""",
        "jurisdiction": "Federal/Provincial",
        "country": "Canada",
        "category": "divorce",
        "tags": ["divorce", "family_law", "canada", "custody"]
    }
])

ALL_LAWS["copyright"].extend([
    {
        "title": "Copyright Law - USA & Canada - Content Owner Rights",
        "content": """COPYRIGHT LAW - CONTENT OWNER RIGHTS

USA Copyright (17 U.S.C.):
- Automatic protection upon creation
- No registration required
- Registration provides additional benefits
- Duration: Life + 70 years (or 95/120 for works for hire)

Exclusive Rights:
- Reproduction
- Distribution
- Public performance
- Public display
- Derivative works
- Digital transmission

Fair Use Factors:
- Purpose (commercial vs educational)
- Nature of work
- Amount used
- Market effect

DMCA (Digital Millennium Copyright Act):
- Safe harbor for ISPs
- Takedown notice procedures
- Counter-notification process
- Anti-circumvention provisions
- Content owner protection

Canada Copyright Act:
- Automatic protection
- Duration: Life + 50 years
- Fair dealing exceptions
- Notice and notice regime (not takedown)

Content Owner Rights:
- Control reproduction
- Control distribution
- Control public performance
- Control derivative works
- License or assign rights
- Sue for infringement

Common Questions:
- Do I need to register copyright?
- What is fair use/fair dealing?
- How do I protect my content?
- What is DMCA takedown?
- Can I use copyrighted material?
- What are the penalties for infringement?
- How do I license my work?
- What is public domain?
- Can I copyright my website?
- What is the difference between copyright and trademark?""",
        "jurisdiction": "Federal",
        "country": "Both",
        "category": "copyright",
        "tags": ["copyright", "content_owner", "dmca", "intellectual_property"]
    }
])

ALL_LAWS["commercial_vehicle"].extend([
    {
        "title": "Commercial Vehicle Regulations - Oversized Load & Safety Straps",
        "content": """COMMERCIAL VEHICLE REGULATIONS - OVERSIZED LOAD & SAFETY

USA FMCSR - Cargo Securement:
- All cargo must be secured
- Aggregate working load limit (WLL) requirements
- Minimum number of tiedowns based on cargo weight
- Safety straps must meet DOT standards
- Grade of straps matters (not just any straps)

Oversized Load Requirements:
- Permits required for loads exceeding standard dimensions
- Width over 8'6" requires permit
- Height over 13'6" requires permit
- Length varies by configuration
- Weight over 80,000 lbs requires permit

Safety Equipment Standards:
- DOT-approved cargo control devices
- Working load limit (WLL) must be marked
- Straps must be in good condition
- Proper attachment points required
- Edge protection required for sharp edges

Penalties for Violations:
- Fines: $1,000 - $10,000+
- Out-of-service orders
- CSA points against carrier
- Possible license suspension
- Vehicle impoundment

Canada NSC - Cargo Securement:
- Cargo must not shift or fall
- Tiedowns must meet WLL requirements
- Proper blocking and bracing
- Safety equipment must meet standards
- Inspection requirements

Oversized Load in Canada:
- Provincial permit system
- Dimension limits vary by province
- Escort vehicle requirements
- Route restrictions
- Time of day restrictions

Common Questions:
- What are the cargo securement rules?
- What is the difference between safety straps and regular straps?
- Do I need a permit for oversized load?
- What are the penalties for non-compliance?
- Can I be fined for using wrong straps?
- What is the working load limit?
- Do I need escort vehicles?
- What are the route restrictions?
- How do I get an oversized permit?
- What is CSA and how does it affect me?""",
        "jurisdiction": "Federal/Provincial",
        "country": "Both",
        "category": "commercial_vehicle",
        "tags": ["oversized_load", "safety_straps", "cargo_securement", "truck_driver"]
    }
])

# Save database
with open(DATA_DIR / "all_laws_complete.json", 'w', encoding='utf-8') as f:
    json.dump(ALL_LAWS, f, indent=2, ensure_ascii=False)

total = sum(len(v) for v in ALL_LAWS.values())
print(f"Created comprehensive law database with {total} documents")
print(f"Saved to: {DATA_DIR / 'all_laws_complete.json'}")

- Life + 50 years
- Joint works: Last author + 50 years
- Corporate: 50 years from publication

Fair Dealing Exceptions:
- Research
- Private study
- Education
- Parody/satire
- Criticism/review
- News reporting

Notice and Notice Regime:
- ISPs forward notices
- No automatic takedown
- Different from DMCA

Content Owner Rights:
- Reproduce
- Perform publicly
- Publish
- Make available online
- Translate/adapt

Common Questions:
- How long does copyright last in Canada?
- What is fair dealing?
- Do I need to register?
- What is notice and notice?
- Can educational institutions use copyrighted material?""",
            "jurisdiction": "Federal",
            "country": "Canada",
            "category": "copyright",
            "tags": ["copyright", "fair_dealing", "canada"]
        }
    ])

def add_commercial_vehicle():
    """Add commercial vehicle regulations."""
    ALL_LAWS["commercial_vehicle"].extend([
        {
            "title": "USA FMCSR - Commercial Vehicle Regulations",
            "content": """USA COMMERCIAL VEHICLE REGULATIONS

Hours of Service:
- 11 hours driving within 14-hour window
- 30-minute break after 8 hours
- 34-hour restart
- 60/70-hour limit

CDL Requirements:
- Age 21+ for interstate
- Medical certificate
- Knowledge and skills tests
- Background check

Cargo Securement:
- All cargo properly secured
- Weight distribution limits
- Working load limits
- Different rules per cargo type

Oversize/Overweight:
- Permits required
- Escort vehicles
- Route restrictions
- Time restrictions

ELD Mandate:
- Electronic logging required
- GPS tracking
- Data transfer to FMCSA

Drug/Alcohol Testing:
- Pre-employment
- Random (50% annually)
- Post-accident
- Reasonable suspicion

Common Questions:
- What are HOS rules?
- How do I get CDL?
- What is ELD mandate?
- Cargo securement rules?
- Oversize permit process?
- Drug testing requirements?""",
            "jurisdiction": "Federal",
            "country": "USA",
            "category": "commercial_vehicle",
            "tags": ["truck_driver", "fmcsr", "commercial", "oversize"]
        },
        {
            "title": "Canada NSC - Commercial Vehicle Regulations",
            "content": """CANADA COMMERCIAL VEHICLE REGULATIONS

Hours of Service:
- 13 hours driving
- 14 hours work
- 70 hours weekly
- 8-hour off-duty required

Commercial License:
- Class 1-5 licenses
- Medical exam
- Knowledge and road tests

Cargo Securement:
- Must not shift or fall
- WLL requirements
- Blocking and bracing

Oversize Permits:
- Provincial permits
- Dimension limits vary
- Escort requirements

Electronic Logs:
- Mandatory for most
- Daily log requirements
- Data retention

Common Questions:
- What are HOS rules in Canada?
- How do I get commercial license?
- Cargo securement rules?
- Oversize permit process?""",
            "jurisdiction": "Federal",
            "country": "Canada",
            "category": "commercial_vehicle",
            "tags": ["truck_driver", "nsc", "commercial", "canada"]
        }
    ])

def main():
    """Main function to create comprehensive law database."""
    print("=" * 80)
    print("COMPREHENSIVE LAW DATABASE CREATOR")
    print("=" * 80)
    print("Creating database with ALL laws:")
    print("- Constitutional")
    print("- Criminal")
    print("- Traffic")
    print("- Commercial Vehicle")
    print("- Family Law (Divorce, Custody)")
    print("- Copyright & Content Owner")
    print("- Civil Law")
    print("- Corporate Law")
    print("- Employment Law")
    print("- Environmental Law")
    print("- Supreme Court Cases")
    print("=" * 80)

    # Add all law categories
    add_family_law()
    add_copyright_content_owner()
    add_commercial_vehicle()

    # Save database
    with open(DATA_DIR / "all_laws_complete.json", 'w', encoding='utf-8') as f:
        json.dump(ALL_LAWS, f, indent=2, ensure_ascii=False)

    # Statistics
    total = sum(len(items) for items in ALL_LAWS.values())
    print(f"\nTotal Legal Documents Created: {total}")
    for category, items in ALL_LAWS.items():
        if items:
            print(f"  {category}: {len(items)} documents")

    print(f"\nSaved to: {DATA_DIR / 'all_laws_complete.json'}")
    print("=" * 80)

if __name__ == "__main__":
    main()

- 30-minute break after 8 hours
- 34-hour restart
- 60/70-hour limit

CDL Requirements:
- Age 21+ interstate
- Medical certificate
- Knowledge and skills tests
- Background check

Vehicle Maintenance:
- Brake systems
- Steering/suspension
- Tires (tread depth)
- Lighting/electrical
- Emergency equipment

Cargo Securement:
- All cargo secured
- Weight distribution
- Working load limits
- Different cargo types

Size/Weight Limits:
- Width: 8'6"
- Height: 13'6"
- Length: varies
- Weight: 80,000 lbs

Oversize Permits:
- Single trip/annual
- Escort vehicles
- Route restrictions
- Time restrictions

ELD Mandate:
- Electronic logging
- GPS tracking
- Data transfer

Drug/Alcohol Testing:
- Pre-employment
- Random (50% annually)
- Post-accident
- Reasonable suspicion

Common Questions:
- HOS rules?
- How to get CDL?
- ELD mandate?
- Drive more than 11 hours?
- Cargo securement rules?
- Oversize permit?
- Drug testing?
- Phone while driving?
- What is CSA?
- Dispute violation?""",
    "jurisdiction": "Federal",
    "country": "USA",
    "tags": ["fmcsr", "truck_driver", "cdl", "commercial"]
})

ALL_LAWS["commercial_vehicle"].append({
    "title": "Canada NSC - Commercial Vehicle Regulations",
    "content": """CANADA NATIONAL SAFETY CODE

Hours of Service:
- 13 hours driving
- 14 hours work
- 70 hours weekly
- 8-hour off-duty
- 24-hour reset

Commercial License:
- Class 1-5
- Medical exam
- Knowledge/road tests
- Age requirements

Vehicle Safety:
- CVSA standards
- Brake systems
- Steering/suspension
- Tires/wheels
- Lighting
- Emergency equipment

Cargo Securement:
- No shift or fall
- WLL requirements
- Blocking/bracing
- Commodity-specific

Size/Weight:
- Width: 2.6m
- Height: 4.15m
- Length: varies
- Weight: varies

Oversize Permits:
- Provincial system
- Dimension limits
- Escort requirements
- Seasonal restrictions

Electronic Logging:
- Mandatory
- Daily logs
- Exception reporting
- Data retention

Drug/Alcohol:
- Pre-employment
- Random
- Post-incident
- Reasonable cause

Common Questions:
- HOS in Canada?
- Commercial license?
- NSC inspection?
- Drive more than 13 hours?
- Cargo securement?
- Oversize permit?
- Drug testing?
- ELD in Canada?
- What is CVSA?
- Dispute violation?""",
    "jurisdiction": "Federal",
    "country": "Canada",
    "tags": ["nsc", "truck_driver", "commercial", "canada"]
})

# Save database
with open(DATA_DIR / "all_laws.json", 'w', encoding='utf-8') as f:
    json.dump(ALL_LAWS, f, indent=2, ensure_ascii=False)

total = sum(len(v) for v in ALL_LAWS.values())
print(f"Created comprehensive legal database with {total} documents")
print(f"Categories: {len([k for k, v in ALL_LAWS.items() if v])}")
print(f"Saved to: {DATA_DIR / 'all_laws.json'}")

Cargo Securement Standards (49 CFR Part 393):
- All cargo must be secured
- Aggregate working load limit (WLL) requirements
- Minimum number of tiedowns based on cargo weight
- Safety straps must meet DOT standards
- Non-safety straps are violation

Safety Equipment Requirements:
- DOT-approved cargo securement devices
- Working load limit (WLL) marked on devices
- Proper tensioning and inspection
- Different requirements for different cargo types

Oversize Permit Requirements:
- Single trip or annual permits
- Route restrictions
- Time of day restrictions
- Escort vehicle requirements for wide loads
- Pilot car requirements

Penalties for Violations:
- Fines: $1,000 - $10,000+
- Out-of-service orders
- Vehicle impoundment
- CDL points/suspensions
- Carrier sanctions

Common Questions:
- What are the cargo securement rules?
- What is the difference between safety and non-safety straps?
- Do I need a permit for oversized load?
- What are the penalties for non-compliance?
- Can I appeal a violation?
- What are escort vehicle requirements?
- How do I get an oversize permit?
- What are the WLL requirements?""",
        "jurisdiction": "Federal",
        "country": "USA",
        "category": "commercial_vehicle",
        "tags": ["oversized_load", "safety_straps", "fmcsr", "truck_driver", "commercial"]
    }
])

# Save database
with open(DATA_DIR / "all_laws.json", 'w', encoding='utf-8') as f:
    json.dump(ALL_LAWS, f, indent=2, ensure_ascii=False)

total = sum(len(v) for v in ALL_LAWS.values())
print(f"Created comprehensive legal database with {total} items")
print(f"Saved to: {DATA_DIR / 'all_laws.json'}")

- Can you get divorced without a lawyer in Canada?
- What is the process for uncontested divorce?
- How long does divorce take in Canada?
- Can same-sex couples divorce in Canada?
- What is the role of mediators in Canadian divorce?
- How does spousal support work in Canada?
- Can I change my name after divorce in Canada?
- How is child support calculated in Canada?
- What is the difference between custody and access?
- Can I move with my child after divorce in Canada?
- How do I modify custody or support in Canada?
- What happens to pensions in Canadian divorce?""",
        "jurisdiction": "Federal/Provincial",
        "country": "Canada",
        "category": "divorce",
        "tags": ["divorce", "family_law", "canada", "custody", "support"]
    }
])

# Add commercial vehicle regulations
ALL_LAWS["commercial_vehicle"].extend([
    {
        "title": "Oversized Load Regulations - USA",
        "content": """OVERSIZED LOAD REGULATIONS - UNITED STATES

FEDERAL SIZE LIMITS (Without Permit):
- Width: 8'6" (102 inches)
- Height: 13'6" (162 inches)
- Length: 53' trailer, 65' doubles
- Weight: 80,000 lbs gross vehicle weight

OVERSIZE PERMIT REQUIREMENTS:
- Single trip permits: For one-time moves
- Annual permits: For regular oversized loads
- Superload permits: For extremely heavy loads
- Escort requirements: For wide loads (over 12' or 14')

SAFETY REQUIREMENTS:
- Proper cargo securement (FMCSR Part 393)
- DOT-approved safety straps (not regular straps)
- Minimum working load limit (WLL) requirements
- Proper blocking and bracing
- Warning flags and lights
- Pilot/escort vehicles for wide loads

CARGO SECUREMENT STANDARDS:
- Aggregate working load limit must equal 50% of cargo weight
- Direct tie-downs: Must be at least 50% of cargo weight
- Friction tie-downs: Must be at least 50% of cargo weight
- Edge protection required for sharp edges
- Proper tensioning of straps

VIOLATIONS AND PENALTIES:
- Non-safety straps: $500-$5,000 fine
- Missing permits: $1,000-$10,000 fine
- Overweight: $1,000-$10,000+ fine
- Improper securement: $500-$5,000 fine
- Missing escort: $500-$2,500 fine
- Route violations: $500-$2,500 fine

Common Questions:
- What are the size limits for oversized loads?
- Do I need a permit for oversized loads?
- What are the safety strap requirements?
- What is the difference between safety straps and regular straps?
- When do I need escort vehicles?
- What are the penalties for oversized load violations?
- How do I get an oversized load permit?
- What are the route restrictions for oversized loads?
- Can I travel at night with oversized loads?
- What is the difference between oversize and overweight?""",
        "jurisdiction": "Federal/State",
        "country": "USA",
        "category": "commercial_vehicle",
        "tags": ["oversized_load", "truck_driver", "commercial_vehicle", "safety_straps"]
    },
    {
        "title": "Oversized Load Regulations - Canada",
        "content": """OVERSIZED LOAD REGULATIONS - CANADA

PROVINCIAL SIZE LIMITS (Without Permit):
- Width: 2.6 meters (8'6")
- Height: 4.15 meters (13'7")
- Length: Varies by configuration
- Weight: Varies by axle configuration

OVERSIZE PERMIT REQUIREMENTS:
- Provincial permits required
- Single trip or annual permits
- Dimension limits vary by province
- Escort requirements for wide loads
- Seasonal restrictions in some areas

SAFETY REQUIREMENTS:
- Proper cargo securement (NSC Standard 10)
- Approved safety straps meeting WLL requirements
- Proper blocking and bracing
- Warning flags and lights
- Pilot/escort vehicles for wide loads
- Route designation required

CARGO SECUREMENT STANDARDS:
- Aggregate working load limit requirements
- Direct tie-downs: Minimum 50% of cargo weight
- Friction tie-downs: Minimum 50% of cargo weight
- Edge protection for sharp edges
- Proper tensioning and inspection

VIOLATIONS AND PENALTIES:
- Non-safety straps: $500-$5,000 fine
- Missing permits: $1,000-$10,000 fine
- Overweight: $1,000-$10,000+ fine
- Improper securement: $500-$5,000 fine
- Missing escort: $500-$2,500 fine
- Route violations: $500-$2,500 fine

Common Questions:
- What are the size limits for oversized loads in Canada?
- Do I need a permit for oversized loads in Canada?
- What are the safety strap requirements in Canada?
- What is the difference between safety straps and regular straps?
- When do I need escort vehicles in Canada?
- What are the penalties for oversized load violations in Canada?
- How do I get an oversized load permit in Canada?
- What are the route restrictions for oversized loads in Canada?
- Can I travel at night with oversized loads in Canada?
- What is the difference between oversize and overweight in Canada?""",
        "jurisdiction": "Provincial",
        "country": "Canada",
        "category": "commercial_vehicle",
        "tags": ["oversized_load", "truck_driver", "commercial_vehicle", "canada"]
    }
])

# Add copyright and content owner rules
ALL_LAWS["copyright"].extend([
    {
        "title": "Copyright and Content Owner Rules - USA",
        "content": """COPYRIGHT AND CONTENT OWNER RULES - UNITED STATES

COPYRIGHT PROTECTION:
- Automatic upon creation
- No registration required
- Registration provides additional benefits
- Duration: Life + 70 years (or 95/120 for works for hire)

DIGITAL MILLENNIUM COPYRIGHT ACT (DMCA):
- Safe harbor for online service providers
- Takedown notice procedures
- Counter-notification process
- Anti-circumvention provisions
- Limitations on liability

DMCA TAKEDOWN PROCESS:
1. Copyright owner sends takedown notice
2. Service provider removes content
3. User can send counter-notification
4. Content restored after 10-14 days if no lawsuit
5. Both parties can pursue legal action

CONTENT OWNER RIGHTS:
- Reproduction right
- Distribution right
- Public performance right
- Public display right
- Derivative works right
- Digital transmission right

FAIR USE EXCEPTIONS:
- Purpose and character of use
- Nature of copyrighted work
- Amount used
- Market effect

Common Questions:
- What is copyright protection?
- How do I protect my content?
- What is the DMCA takedown process?
- Can I use copyrighted material?
- What is fair use?
- How do I respond to a DMCA takedown?
- What are the penalties for copyright infringement?
- How do I license my copyrighted work?
- What is the difference between copyright and trademark?
- Can I copyright my website?""",
        "jurisdiction": "Federal",
        "country": "USA",
        "category": "copyright",
        "tags": ["copyright", "dmca", "content_owner", "intellectual_property"]
    }
])

# Save all laws
def save_all_laws():
    """Save comprehensive legal database."""
    with open(DATA_DIR / "all_laws_complete.json", 'w', encoding='utf-8') as f:
        json.dump(ALL_LAWS, f, indent=2, ensure_ascii=False)

    total = sum(len(items) for items in ALL_LAWS.values())
    print(f"Saved {total} legal documents to {DATA_DIR / 'all_laws_complete.json'}")

if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE LAW DATABASE CREATOR")
    print("=" * 80)
    print("Creating database with:")
    print("- Divorce laws (USA & Canada)")
    print("- Commercial vehicle regulations")
    print("- Copyright and content owner rules")
    print("- Traffic laws")
    print("- Criminal laws")
    print("- Civil laws")
    print("=" * 80)

    save_all_laws()

    total = sum(len(items) for items in ALL_LAWS.values())
    print(f"\nTotal legal documents: {total}")
    print(f"Saved to: {DATA_DIR}")
