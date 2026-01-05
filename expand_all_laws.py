"""Expand legal dataset with ALL types of laws."""
import json
from pathlib import Path

# Load existing dataset
DATA_DIR = Path("collected_legal_data")
with open(DATA_DIR / "complete_legal_dataset.json", 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# Add new categories
if "divorce_law" not in dataset:
    dataset["divorce_law"] = []

if "copyright_law" not in dataset:
    dataset["copyright_law"] = []

if "commercial_vehicle_regs" not in dataset:
    dataset["commercial_vehicle_regs"] = []

# Add divorce laws
dataset["divorce_law"].extend([
    {
        "title": "USA Divorce Laws - All States",
        "content": """USA DIVORCE LAWS - COMPREHENSIVE GUIDE

No-Fault Divorce (All 50 States):
- Irreconcilable differences
- Irretrievable breakdown of marriage
- Living separate and apart

Fault-Based Grounds:
- Adultery
- Abandonment (1+ years)
- Cruelty/physical abuse
- Mental cruelty
- Alcohol/drug abuse
- Criminal conviction
- Impotency
- Insanity

Residency Requirements by State:
- California: 6 months
- New York: 1 year
- Texas: 6 months
- Florida: 6 months
- Illinois: 90 days
- Pennsylvania: 6 months
- Ohio: 6 months
- Georgia: 6 months
- North Carolina: 6 months
- Michigan: 6 months
- Most states: 6 months to 1 year

Property Division:
- Community Property States: AZ, CA, ID, LA, NV, NM, TX, WA, WI
  * Equal division of marital property
- Equitable Distribution States: All others
  * Fair but not necessarily equal division

Child Custody:
- Best interests of child standard
- Joint custody preferred
- Factors: age, health, stability, parental fitness, child's preference

Child Support:
- State-specific guidelines
- Income shares model (most states)
- Can be modified

Spousal Support:
- Rehabilitative: Short-term
- Reimbursement: For sacrifices
- Permanent: Long-term support

Common Questions:
- How long does divorce take?
- Do I need a lawyer?
- Can I get divorced without spouse's agreement?
- How is property divided?
- What is legal separation vs divorce?
- Can I change my name?
- What is mediation?
- How does adultery affect divorce?""",
        "jurisdiction": "All States",
        "country": "USA",
        "category": "divorce",
        "tags": ["divorce", "family_law", "custody", "alimony"]
    },
    {
        "title": "Canada Divorce Laws",
        "content": """CANADA DIVORCE LAWS

Grounds for Divorce:
- Breakdown of marriage (no-fault)
- Living separate and apart for 1 year (most common)
- Adultery
- Physical/mental cruelty

Property Division:
- Equal division in most provinces
- Ontario, BC, Alberta: Equal division
- Quebec: Civil law system
- Excludes: pre-marriage property, inheritances, gifts

Child Custody:
- Best interests of child
- Maximum contact with both parents
- Joint custody common

Child Support:
- Federal Child Support Guidelines
- Table amount based on income and number of children
- Special/extraordinary expenses

Spousal Support:
- Need and ability to pay
- Compensatory vs needs-based
- Tax implications

Common Questions:
- How long separated before divorce?
- How is property divided?
- Common law vs married?
- Do I need a lawyer?
- How long does divorce take?""",
        "jurisdiction": "Federal/Provincial",
        "country": "Canada",
        "category": "divorce",
        "tags": ["divorce", "family_law", "canada"]
    }
])

# Add copyright/content owner laws
dataset["copyright_law"].extend([
    {
        "title": "USA Copyright Law - 17 U.S.C.",
        "content": """USA COPYRIGHT LAW - COMPREHENSIVE

What Can Be Copyrighted:
- Literary works (books, articles, blogs)
- Musical works (songs, compositions)
- Dramatic works (plays, scripts)
- Pictorial/graphic works (photos, art)
- Motion pictures (movies, videos)
- Sound recordings
- Computer software
- Architectural works
- Databases

Copyright Protection:
- Automatic upon creation
- No registration required
- Registration provides benefits
- Duration: Life + 70 years (or 95/120 for works for hire)

Exclusive Rights:
- Reproduce
- Prepare derivative works
- Distribute
- Perform publicly
- Display publicly
- Transmit digitally

Fair Use Factors:
- Purpose and character
- Nature of work
- Amount used
- Market effect

DMCA (Digital Millennium Copyright Act):
- Safe harbor for ISPs
- Takedown notice procedures
- Counter-notification process
- Anti-circumvention provisions
- Content owner protections

Content Owner Rights:
- Right to control distribution
- Right to license
- Right to sue for infringement
- Right to takedown unauthorized content
- Right to collect royalties

Common Questions:
- Do I need to register copyright?
- What is fair use?
- How long does copyright last?
- What is DMCA takedown?
- Can I copyright my website?
- What are penalties for infringement?
- How do I license my work?
- What is public domain?""",
        "jurisdiction": "Federal",
        "country": "USA",
        "category": "copyright",
        "tags": ["copyright", "dmca", "content_owner", "intellectual_property"]
    },
    {
        "title": "Canada Copyright Act",
        "content": """CANADA COPYRIGHT ACT

What Can Be Copyrighted:
- Literary, dramatic, musical works
- Artistic works
- Computer programs
- Sound recordings
- Performer's performances

Copyright Duration:
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

# Add commercial vehicle regulations (for truck driver question)
dataset["commercial_vehicle_regs"].extend([
    {
        "title": "USA FMCSR - Oversized Load and Cargo Securement",
        "content": """FEDERAL MOTOR CARRIER SAFETY REGULATIONS - OVERSIZED LOAD & CARGO SECUREMENT

OVERSIZE/OVERWEIGHT LOAD REQUIREMENTS:
- Permits required for loads exceeding standard dimensions
- Standard limits: 8'6" width, 13'6" height, 53' length
- Weight limits: 80,000 lbs gross vehicle weight
- Single trip or annual permits available
- State-specific requirements vary

CARGO SECUREMENT STANDARDS (49 CFR Part 393):
- All cargo must be properly secured
- Aggregate working load limit (WLL) requirements
- Minimum number of tiedowns based on cargo weight
- Safety straps must meet DOT standards
- NON-SAFETY STRAPS ARE A VIOLATION

SAFETY EQUIPMENT REQUIREMENTS:
- DOT-approved cargo securement devices required
- Working load limit (WLL) must be marked on devices
- Proper tensioning and inspection required
- Different requirements for different cargo types
- Edge protection required for sharp edges

SAFETY STRAPS vs REGULAR STRAPS:
- Safety straps: DOT-approved, marked with WLL, meet FMCSR standards
- Regular straps: Not approved, no WLL marking, violation if used
- Must use proper grade straps for cargo weight
- Inspection required before each trip

ESCORT VEHICLE REQUIREMENTS:
- Required for wide loads (over 12 feet in most states)
- Pilot car requirements for very wide loads
- Warning signs and flags required
- Route restrictions apply

PENALTIES FOR VIOLATIONS:
- Non-safety straps: $500-$5,000 fine
- Missing permits: $1,000-$10,000 fine
- Overweight: $1,000-$10,000+ fine
- Improper securement: $500-$5,000 fine
- Missing escort: $500-$2,500 fine
- Route violations: $500-$2,500 fine
- Out-of-service orders
- CSA points against carrier
- Possible CDL suspension

COMMON QUESTIONS:
- What are the cargo securement rules?
- What is the difference between safety straps and regular straps?
- Do I need a permit for oversized load?
- What are the penalties for using non-safety straps?
- What are the working load limit requirements?
- When do I need escort vehicles?
- What are the route restrictions?
- How do I get an oversized permit?
- What is CSA and how does it affect me?
- Can I appeal a violation?""",
        "jurisdiction": "Federal/State",
        "country": "USA",
        "category": "commercial_vehicle",
        "tags": ["oversized_load", "safety_straps", "cargo_securement", "truck_driver", "fmcsr", "commercial_vehicle"]
    },
    {
        "title": "Canada NSC - Oversized Load and Cargo Securement",
        "content": """CANADA NATIONAL SAFETY CODE - OVERSIZED LOAD & CARGO SECUREMENT

OVERSIZE/OVERWEIGHT REQUIREMENTS:
- Provincial permits required
- Dimension limits vary by province
- Width: 2.6 meters (8'6") standard
- Height: 4.15 meters (13'7") standard
- Weight: Varies by axle configuration

CARGO SECUREMENT STANDARDS (NSC Standard 10):
- Cargo must not shift or fall
- Tiedowns must meet working load limit (WLL) requirements
- Proper blocking and bracing required
- Safety equipment must meet standards
- NON-SAFETY STRAPS ARE A VIOLATION

SAFETY EQUIPMENT:
- Approved cargo securement devices
- WLL marked on devices
- Proper tensioning required
- Inspection before each trip
- Edge protection for sharp edges

SAFETY STRAPS REQUIREMENTS:
- Must be approved for commercial use
- Must have WLL marking
- Must meet NSC standards
- Regular straps not acceptable
- Proper grade for cargo weight

ESCORT VEHICLE REQUIREMENTS:
- Required for wide loads (varies by province)
- Pilot car requirements
- Warning signs and flags
- Route designation required

PENALTIES FOR VIOLATIONS:
- Non-safety straps: $500-$5,000 fine
- Missing permits: $1,000-$10,000 fine
- Overweight: $1,000-$10,000+ fine
- Improper securement: $500-$5,000 fine
- Missing escort: $500-$2,500 fine
- Route violations: $500-$2,500 fine
- Out-of-service orders
- Possible license suspension

COMMON QUESTIONS:
- What are the cargo securement rules in Canada?
- What is the difference between safety straps and regular straps?
- Do I need a permit for oversized load in Canada?
- What are the penalties for using non-safety straps?
- What are the working load limit requirements?
- When do I need escort vehicles in Canada?
- What are the route restrictions?
- How do I get an oversized permit in Canada?
- Can I appeal a violation in Canada?""",
        "jurisdiction": "Provincial",
        "country": "Canada",
        "category": "commercial_vehicle",
        "tags": ["oversized_load", "safety_straps", "cargo_securement", "truck_driver", "nsc", "canada"]
    }
])

# Save expanded dataset
with open(DATA_DIR / "complete_legal_dataset.json", 'w', encoding='utf-8') as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

total = sum(len(v) for v in dataset.values())
print(f"Expanded dataset: {total} total items")
print(f"Added: Divorce laws, Copyright laws, Commercial vehicle regulations")
print(f"Saved to: {DATA_DIR / 'complete_legal_dataset.json'}")
