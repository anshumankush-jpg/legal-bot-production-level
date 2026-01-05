"""Create comprehensive dataset for ALL laws - criminal, traffic, divorce, civil, commercial, copyright, etc."""
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("collected_legal_data")

# Load existing dataset
try:
    with open(DATA_DIR / "complete_legal_dataset.json", 'r', encoding='utf-8') as f:
        dataset = json.load(f)
except FileNotFoundError:
    dataset = {}

# Initialize all categories
ALL_CATEGORIES = {
    "usa_federal_criminal": [],
    "usa_traffic_laws": [],
    "canada_federal_criminal": [],
    "canada_provincial_laws": [],
    "case_studies": [],
    "divorce_law": [],
    "family_law": [],
    "copyright_law": [],
    "content_owner_rules": [],
    "commercial_vehicle_regs": [],
    "civil_law": [],
    "contract_law": [],
    "tort_law": [],
    "property_law": [],
    "corporate_law": [],
    "employment_law": [],
    "tax_law": [],
    "bankruptcy_law": [],
    "environmental_law": [],
    "immigration_law": [],
    "health_law": [],
    "education_law": [],
    "consumer_protection": [],
    "privacy_law": [],
    "cyber_law": [],
    "antitrust_law": [],
    "international_law": [],
    "administrative_law": [],
    "constitutional_law": []
}

# Merge existing data
for category in ALL_CATEGORIES:
    if category in dataset:
        ALL_CATEGORIES[category] = dataset[category]

# ========== DIVORCE LAW ==========
ALL_CATEGORIES["divorce_law"].extend([
    {
        "title": "USA Divorce Laws - All 50 States Comprehensive Guide",
        "content": """USA DIVORCE LAWS - COMPREHENSIVE GUIDE FOR ALL 50 STATES

NO-FAULT DIVORCE (Available in All 50 States):
- Irreconcilable differences
- Irretrievable breakdown of marriage
- Incompatibility
- Living separate and apart
- No need to prove fault

FAULT-BASED DIVORCE GROUNDS (Varies by State):
- Adultery
- Abandonment (1-5 years depending on state)
- Cruelty (physical or mental)
- Mental cruelty
- Alcohol/drug abuse
- Criminal conviction
- Impotency
- Insanity
- Desertion
- Constructive desertion

RESIDENCY REQUIREMENTS BY STATE:
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

PROPERTY DIVISION:
Community Property States (Equal Division):
- Arizona, California, Idaho, Louisiana, Nevada, New Mexico, Texas, Washington, Wisconsin
- All marital property divided 50/50
- Separate property remains individual
- Includes: earnings, property acquired during marriage, community debts

Equitable Distribution States (Fair Division):
- All other states
- Court divides property fairly (not necessarily equally)
- Considers: marriage length, contributions, earning capacity, age, health
- Separate property generally excluded

CHILD CUSTODY:
Best Interests Factors:
- Child's age and health
- Parental fitness and capability
- Stability and continuity
- Child's preferences (if mature enough)
- Geographic proximity
- Sibling relationships
- History of abuse or neglect
- Parental cooperation ability

Custody Types:
- Sole custody: One parent has primary custody
- Joint custody: Both parents share decision-making
- Physical custody: Where child lives
- Legal custody: Decision-making authority
- Split custody: Different children with different parents

CHILD SUPPORT:
Calculation Methods:
- Income Shares Model (most states): Both parents' income considered
- Percentage of Income Model (few states): Percentage of obligor's income
- Melson Formula (Delaware, Hawaii, Montana): More complex calculation

Factors:
- Both parents' income
- Number of children
- Custody arrangement
- Health insurance costs
- Childcare expenses
- Educational expenses
- Special needs

SPOUSAL SUPPORT (ALIMONY):
Types:
- Temporary: During divorce proceedings
- Rehabilitative: Short-term, for education/training
- Reimbursement: For sacrifices during marriage
- Permanent: Long-term or lifetime support
- Lump Sum: One-time payment

Factors:
- Marriage length
- Age and health of both parties
- Earning capacity
- Standard of living during marriage
- Contributions to marriage
- Tax consequences

DIVORCE PROCESS:
1. File petition/complaint
2. Serve spouse with papers
3. Response period (20-30 days typically)
4. Discovery (exchange information)
5. Negotiation/mediation
6. Settlement or trial
7. Final judgment

Common Questions:
- How long does divorce take?
- Do I need a lawyer for divorce?
- Can I get divorced without my spouse's agreement?
- How is property divided in divorce?
- What is the difference between legal separation and divorce?
- Can I change my name in divorce?
- What is mediation vs litigation?
- How does adultery affect divorce?
- Can I get alimony?
- How is child support calculated?
- What is the difference between custody and visitation?
- Can I move with my child after divorce?
- How do I modify custody or support?
- What happens to retirement accounts in divorce?
- Can I get divorced if my spouse is in another country?
- What is collaborative divorce?
- What is uncontested divorce?
- How much does divorce cost?""",
        "jurisdiction": "All States",
        "country": "USA",
        "category": "divorce",
        "tags": ["divorce", "family_law", "custody", "alimony", "child_support", "property_division"]
    },
    {
        "title": "Canada Divorce Act - Comprehensive Guide",
        "content": """CANADA DIVORCE ACT - COMPREHENSIVE GUIDE

GROUNDS FOR DIVORCE:
1. Breakdown of Marriage (No-Fault):
   - Living separate and apart for one year (most common)
   - Mutual consent possible
   - Unilateral possible after one year

2. Fault-Based (Rarely Used):
   - Adultery
   - Physical or mental cruelty

SEPARATION REQUIREMENTS:
- Must be living separate and apart
- Can live in same house if separate lives
- One year minimum (no exceptions)
- Can resume cohabitation for up to 90 days without breaking separation

RESIDENCY REQUIREMENTS:
- One spouse must be resident of Canada for at least one year
- Must be resident of province where filing
- Jurisdiction based on residence, not citizenship

PROPERTY DIVISION BY PROVINCE:
Equal Division Provinces:
- Ontario: Family Law Act - equal division of net family property
- British Columbia: Family Law Act - equal division of family property
- Alberta: Matrimonial Property Act - equal division
- Manitoba: Marital Property Act - equal division
- Saskatchewan: Matrimonial Property Act - equal division
- Nova Scotia: Matrimonial Property Act - equal division
- New Brunswick: Marital Property Act - equal division
- Newfoundland: Matrimonial Property Act - equal division
- PEI: Matrimonial Property Act - equal division
- NWT/Nunavut/Yukon: Equal division

Quebec (Civil Law):
- Partnership of acquests
- Property acquired during marriage divided equally
- Separate property remains individual

EXCLUDED PROPERTY:
- Property owned before marriage
- Inheritances (unless used for family)
- Gifts from third parties
- Property excluded by agreement
- Damages for personal injury

CHILD CUSTODY:
Best Interests of Child:
- Child's needs and preferences
- Maximum contact with both parents
- Parental ability to care for child
- Stability and continuity
- Sibling relationships
- History of family violence

Custody Arrangements:
- Sole custody: One parent has primary custody
- Joint custody: Shared decision-making
- Shared custody: Equal or near-equal time
- Split custody: Different children with different parents

CHILD SUPPORT:
Federal Child Support Guidelines:
- Table amount based on number of children and income
- Special/extraordinary expenses added
- Shared custody: Set-off calculation
- Split custody: Different calculation
- Undue hardship: Can vary from guidelines

SPOUSAL SUPPORT:
Spousal Support Advisory Guidelines:
- Compensatory support: For sacrifices during marriage
- Needs-based support: For economic disadvantage
- Length depends on marriage duration
- Can be indefinite for long marriages
- Tax implications for both parties

DIVORCE PROCESS:
1. File application for divorce
2. Serve spouse with application
3. Response period (30 days)
4. Financial disclosure
5. Negotiation/mediation
6. Settlement or trial
7. Final order

Common Questions:
- How long do you have to be separated before divorce in Canada?
- How is property divided in Canadian divorce?
- What is the difference between common law and married?
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
- What happens to pensions in Canadian divorce?
- What is collaborative divorce in Canada?
- How much does divorce cost in Canada?""",
        "jurisdiction": "Federal/Provincial",
        "country": "Canada",
        "category": "divorce",
        "tags": ["divorce", "family_law", "canada", "custody", "support"]
    }
])

# ========== COPYRIGHT & CONTENT OWNER RULES ==========
ALL_CATEGORIES["copyright_law"].extend([
    {
        "title": "USA Copyright Law - 17 U.S.C. Complete Guide",
        "content": """USA COPYRIGHT LAW - 17 U.S.C. COMPREHENSIVE GUIDE

WHAT CAN BE COPYRIGHTED:
- Literary works (books, articles, blogs, websites)
- Musical works (songs, compositions, lyrics)
- Dramatic works (plays, scripts, screenplays)
- Pantomimes and choreographic works
- Pictorial, graphic, and sculptural works (photos, paintings, drawings)
- Motion pictures and audiovisual works (movies, videos, TV shows)
- Sound recordings (music recordings, podcasts)
- Architectural works
- Computer software and programs
- Databases and compilations

COPYRIGHT PROTECTION REQUIREMENTS:
- Original work of authorship
- Fixed in tangible medium of expression
- Minimal creativity required
- No registration required for protection
- Automatic upon creation

COPYRIGHT DURATION:
- Works created after 1978: Life of author + 70 years
- Joint works: Life of last surviving author + 70 years
- Works made for hire: 95 years from publication or 120 years from creation
- Anonymous/pseudonymous works: 95 years from publication or 120 years from creation
- Works created before 1978: Different rules apply

EXCLUSIVE RIGHTS OF COPYRIGHT OWNER:
- Reproduce the work
- Prepare derivative works
- Distribute copies to the public
- Perform the work publicly (for certain works)
- Display the work publicly (for certain works)
- Transmit the work digitally (for certain works)

FAIR USE DEFENSE:
Factors Considered:
1. Purpose and character of use (commercial vs educational)
2. Nature of copyrighted work
3. Amount and substantiality used
4. Effect on potential market

FAIR USE EXAMPLES:
- Criticism and comment
- News reporting
- Teaching and scholarship
- Research
- Parody

DIGITAL MILLENNIUM COPYRIGHT ACT (DMCA):
- Safe harbor for online service providers
- Takedown notice procedures
- Counter-notification process
- Anti-circumvention provisions
- Limitations on liability for ISPs

DMCA TAKEDOWN PROCESS:
1. Copyright owner sends takedown notice to ISP
2. ISP removes content
3. User can send counter-notification
4. Content restored after 10-14 days if no lawsuit
5. Both parties can pursue legal action

CONTENT OWNER RIGHTS:
- Right to control reproduction
- Right to control distribution
- Right to control public performance
- Right to control derivative works
- Right to license or assign rights
- Right to sue for infringement
- Right to collect royalties
- Right to takedown unauthorized content

COPYRIGHT INFRINGEMENT PENALTIES:
- Actual damages and profits
- Statutory damages: $750-$30,000 per work
- Willful infringement: Up to $150,000 per work
- Attorney fees and costs
- Injunctive relief
- Criminal penalties for willful infringement

Common Questions:
- Do I need to register copyright?
- What is fair use?
- How long does copyright last?
- What is the difference between copyright and trademark?
- Can I copyright my website?
- What is the DMCA takedown process?
- Can I use copyrighted material for education?
- What are the penalties for copyright infringement?
- How do I license my copyrighted work?
- What is public domain?
- Can I copyright an idea?
- What is the difference between copyright and patent?
- How do I respond to a DMCA takedown?
- Can I copyright a name or title?
- What is work made for hire?""",
        "jurisdiction": "Federal",
        "country": "USA",
        "category": "copyright",
        "tags": ["copyright", "dmca", "content_owner", "intellectual_property", "fair_use"]
    },
    {
        "title": "Canada Copyright Act - Complete Guide",
        "content": """CANADA COPYRIGHT ACT - COMPREHENSIVE GUIDE

WHAT CAN BE COPYRIGHTED:
- Literary works (books, articles, computer programs)
- Dramatic works (plays, scripts)
- Musical works (songs, compositions)
- Artistic works (paintings, drawings, sculptures, photographs)
- Computer programs
- Compilations of data
- Performer's performances
- Sound recordings
- Communication signals

COPYRIGHT PROTECTION REQUIREMENTS:
- Original work
- In any material form
- Within scope of Copyright Act
- No registration required for protection
- Automatic upon creation

COPYRIGHT DURATION:
- General rule: Life of author + 50 years
- Joint works: Life of last surviving author + 50 years
- Corporate works: 50 years from publication
- Photographs: Life of photographer + 50 years
- Sound recordings: 50 years from publication
- Performer's performances: 50 years from performance
- Crown copyright: 50 years from publication

RIGHTS OF COPYRIGHT OWNER:
- Reproduce work in any material form
- Perform work in public
- Publish unpublished work
- Rent copies to public
- Make work available online
- Translate, adapt, arrange work
- Authorize any of the above

FAIR DEALING EXCEPTIONS:
- Research
- Private study
- Education
- Parody/satire
- Criticism/review
- News reporting
- For administrative tribunals

NOTICE AND NOTICE REGIME:
- Instead of DMCA-style takedown
- Internet service providers must forward notices to subscribers
- No safe harbor liability for ISPs
- Different from USA DMCA system

CONTENT OWNER RIGHTS:
- Control reproduction
- Control distribution
- Control public performance
- Control derivative works
- License or assign rights
- Sue for infringement
- Collect royalties

COPYRIGHT INFRINGEMENT PENALTIES:
- Actual damages
- Statutory damages: $500-$20,000 per work
- Willful infringement: Up to $20,000 per work
- Attorney fees and costs
- Injunctive relief
- Criminal penalties for commercial infringement

MORAL RIGHTS:
- Right to attribution
- Right to integrity
- Cannot be assigned
- Can be waived
- Last for same duration as copyright

Common Questions:
- How long does copyright last in Canada?
- What is fair dealing in Canada?
- Do I need to register copyright in Canada?
- What is the difference between copyright and patent in Canada?
- Can I copyright my blog posts?
- What are the penalties for copyright infringement in Canada?
- How does the notice and notice system work?
- Can educational institutions use copyrighted materials?
- What is moral rights in Canadian copyright?
- How do I license my work in Canada?
- What is the difference between copyright and trademark in Canada?
- Can I use copyrighted material for education in Canada?
- How do I respond to a notice and notice?
- What is Crown copyright in Canada?""",
        "jurisdiction": "Federal",
        "country": "Canada",
        "category": "copyright",
        "tags": ["copyright", "fair_dealing", "intellectual_property", "canada", "content_owner"]
    }
])

ALL_CATEGORIES["content_owner_rules"].extend([
    {
        "title": "Content Owner Rules - DMCA and Copyright Protection",
        "content": """CONTENT OWNER RULES - DMCA AND COPYRIGHT PROTECTION

DIGITAL MILLENNIUM COPYRIGHT ACT (DMCA):
- Provides safe harbor for online service providers
- Allows content owners to request takedown of infringing content
- Protects ISPs from liability when following procedures
- Anti-circumvention provisions protect DRM

DMCA TAKEDOWN NOTICE REQUIREMENTS:
- Identify copyrighted work
- Identify infringing material
- Contact information
- Good faith statement
- Statement of accuracy
- Signature

COUNTER-NOTIFICATION PROCESS:
- User can dispute takedown
- Must include statement of good faith
- ISP restores content after 10-14 days
- Copyright owner can file lawsuit

CONTENT OWNER PROTECTIONS:
- Right to control distribution
- Right to license content
- Right to sue for infringement
- Right to collect royalties
- Right to takedown unauthorized content
- Right to protect against circumvention

ONLINE CONTENT PROTECTION:
- YouTube Content ID system
- Facebook Rights Manager
- Instagram copyright protection
- Twitter copyright policy
- TikTok content protection

LICENSING OPTIONS:
- Exclusive license
- Non-exclusive license
- Creative Commons licenses
- Public domain dedication
- Fair use/fair dealing

Common Questions:
- How do I protect my content online?
- What is the DMCA takedown process?
- How do I respond to a DMCA takedown?
- What are my rights as a content owner?
- How do I license my content?
- What is Content ID?
- Can I use Creative Commons?
- What is fair use vs licensing?""",
        "jurisdiction": "Federal",
        "country": "USA",
        "category": "content_owner",
        "tags": ["content_owner", "dmca", "copyright", "online_protection"]
    }
])

# ========== COMMERCIAL VEHICLE REGULATIONS ==========
ALL_CATEGORIES["commercial_vehicle_regs"].extend([
    {
        "title": "USA FMCSR - Oversized Load and Cargo Securement Regulations",
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
- Straps must be in good condition (no cuts, fraying, etc.)

CARGO SECUREMENT RULES:
- Aggregate WLL must equal at least 50% of cargo weight
- Direct tie-downs: Must be at least 50% of cargo weight
- Friction tie-downs: Must be at least 50% of cargo weight
- Minimum number of tiedowns based on cargo length
- Proper blocking and bracing required

ESCORT VEHICLE REQUIREMENTS:
- Required for wide loads (over 12 feet in most states)
- Pilot car requirements for very wide loads (over 14-16 feet)
- Warning signs and flags required
- Route restrictions apply
- Time of day restrictions may apply

ROUTE RESTRICTIONS:
- Cannot use certain roads/bridges
- Height restrictions
- Weight restrictions
- Width restrictions
- Low clearance bridges
- Construction zones

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
- Vehicle impoundment

COMMERCIAL DRIVER'S LICENSE (CDL):
- Required for vehicles over 26,001 lbs
- Class A, B, C licenses
- Medical certificate required
- Knowledge and skills tests
- Background check required

HOURS OF SERVICE (HOS):
- 11 hours driving within 14-hour window
- 30-minute break after 8 hours
- 34-hour restart
- 60/70-hour limit

Common Questions:
- What are the cargo securement rules?
- What is the difference between safety straps and regular straps?
- Do I need a permit for oversized load?
- What are the penalties for using non-safety straps?
- What are the working load limit requirements?
- When do I need escort vehicles?
- What are the route restrictions?
- How do I get an oversized permit?
- What is CSA and how does it affect me?
- Can I appeal a violation?
- What are the HOS rules?
- How do I get a CDL?
- What is the ELD mandate?
- Can I drive more than 11 hours?
- What are the drug testing requirements?""",
        "jurisdiction": "Federal/State",
        "country": "USA",
        "category": "commercial_vehicle",
        "tags": ["oversized_load", "safety_straps", "cargo_securement", "truck_driver", "fmcsr", "commercial_vehicle"]
    },
    {
        "title": "Canada NSC - Oversized Load and Cargo Securement Regulations",
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
- Seasonal restrictions in some areas

ROUTE RESTRICTIONS:
- Cannot use certain roads/bridges
- Height restrictions
- Weight restrictions
- Width restrictions
- Low clearance areas

PENALTIES FOR VIOLATIONS:
- Non-safety straps: $500-$5,000 fine
- Missing permits: $1,000-$10,000 fine
- Overweight: $1,000-$10,000+ fine
- Improper securement: $500-$5,000 fine
- Missing escort: $500-$2,500 fine
- Route violations: $500-$2,500 fine
- Out-of-service orders
- Possible license suspension
- Vehicle impoundment

COMMERCIAL LICENSE:
- Class 1-5 licenses
- Medical examination required
- Knowledge and road tests
- Age requirements vary

HOURS OF SERVICE:
- 13 hours driving
- 14 hours work
- 70 hours weekly
- 8-hour off-duty required

Common Questions:
- What are the cargo securement rules in Canada?
- What is the difference between safety straps and regular straps?
- Do I need a permit for oversized load in Canada?
- What are the penalties for using non-safety straps?
- What are the working load limit requirements?
- When do I need escort vehicles in Canada?
- What are the route restrictions?
- How do I get an oversized permit in Canada?
- Can I appeal a violation in Canada?
- What are the HOS rules in Canada?
- How do I get a commercial license in Canada?""",
        "jurisdiction": "Provincial",
        "country": "Canada",
        "category": "commercial_vehicle",
        "tags": ["oversized_load", "safety_straps", "cargo_securement", "truck_driver", "nsc", "canada"]
    }
])

# ========== CIVIL LAW ==========
ALL_CATEGORIES["civil_law"].extend([
    {
        "title": "USA Civil Law Overview",
        "content": """USA CIVIL LAW - COMPREHENSIVE OVERVIEW

TORT LAW:
- Negligence: Duty, breach, causation, damages
- Intentional torts: Assault, battery, false imprisonment, defamation
- Strict liability: Product liability, abnormally dangerous activities
- Nuisance: Private and public nuisance
- Defamation: Libel and slander

CONTRACT LAW:
- Formation: Offer, acceptance, consideration
- Breach of contract: Material vs minor breach
- Remedies: Damages, specific performance, rescission
- Statute of limitations: Varies by state (typically 3-6 years)
- Defenses: Fraud, duress, mistake, illegality

PROPERTY LAW:
- Real property: Land and buildings
- Personal property: Movable items
- Landlord-tenant law
- Zoning and land use
- Eminent domain
- Adverse possession

FAMILY LAW:
- Divorce and separation
- Child custody and support
- Spousal support
- Property division
- Adoption
- Guardianship

ESTATE LAW:
- Wills and trusts
- Probate process
- Estate administration
- Power of attorney
- Living wills

Common Questions:
- What is negligence?
- How do I sue for breach of contract?
- What are my tenant rights?
- How does product liability work?
- What is defamation?
- How do I write a will?
- What is probate?
- How does small claims court work?""",
        "jurisdiction": "State",
        "country": "USA",
        "category": "civil",
        "tags": ["civil_law", "tort", "contract", "property"]
    },
    {
        "title": "Canada Civil Law Overview",
        "content": """CANADA CIVIL LAW - COMPREHENSIVE OVERVIEW

TORT LAW:
- Negligence: Duty of care, standard of care, causation
- Intentional torts: Assault, battery, false imprisonment
- Strict liability: Product liability
- Nuisance: Private and public nuisance
- Defamation: Libel and slander

CONTRACT LAW:
- Formation: Offer, acceptance, consideration
- Breach of contract
- Remedies: Damages, specific performance
- Statute of limitations: Typically 2-6 years
- Defenses: Fraud, duress, mistake

PROPERTY LAW:
- Real property: Land and buildings
- Personal property: Movable items
- Landlord-tenant law
- Zoning and land use
- Expropriation

FAMILY LAW:
- Divorce and separation
- Child custody and support
- Spousal support
- Property division
- Adoption

ESTATE LAW:
- Wills and estates
- Probate process
- Estate administration
- Power of attorney

Common Questions:
- What is negligence in Canada?
- How do I sue for breach of contract?
- What are my tenant rights in Canada?
- How does product liability work in Canada?
- What is defamation in Canada?""",
        "jurisdiction": "Provincial",
        "country": "Canada",
        "category": "civil",
        "tags": ["civil_law", "tort", "contract", "canada"]
    }
])

# ========== CONTRACT LAW ==========
ALL_CATEGORIES["contract_law"].extend([
    {
        "title": "USA Contract Law",
        "content": """USA CONTRACT LAW

CONTRACT FORMATION:
- Offer: Clear, definite terms
- Acceptance: Unconditional agreement
- Consideration: Something of value exchanged
- Capacity: Legal ability to contract
- Legality: Purpose must be legal

TYPES OF CONTRACTS:
- Express: Written or oral
- Implied: From conduct
- Unilateral: One promise for act
- Bilateral: Exchange of promises
- Executed: Fully performed
- Executory: Not yet performed

BREACH OF CONTRACT:
- Material breach: Substantial failure
- Minor breach: Partial failure
- Anticipatory breach: Before performance due
- Remedies: Damages, specific performance, rescission

STATUTE OF LIMITATIONS:
- Written contracts: 3-6 years (varies by state)
- Oral contracts: 2-4 years (varies by state)
- UCC contracts: 4 years

Common Questions:
- What makes a contract valid?
- Can oral contracts be enforced?
- What is breach of contract?
- What are the remedies for breach?
- What is the statute of limitations?""",
        "jurisdiction": "State",
        "country": "USA",
        "category": "contract",
        "tags": ["contract", "civil_law", "business"]
    }
])

# ========== PROPERTY LAW ==========
ALL_CATEGORIES["property_law"].extend([
    {
        "title": "USA Property Law",
        "content": """USA PROPERTY LAW

REAL PROPERTY:
- Land and buildings
- Fixtures
- Air rights
- Mineral rights
- Water rights

PERSONAL PROPERTY:
- Tangible: Physical items
- Intangible: Stocks, bonds, intellectual property

LANDLORD-TENANT:
- Lease agreements
- Security deposits
- Eviction process
- Tenant rights
- Landlord obligations

ZONING:
- Residential
- Commercial
- Industrial
- Agricultural
- Mixed use

Common Questions:
- What is the difference between real and personal property?
- What are my tenant rights?
- How does eviction work?
- What is zoning?
- What is adverse possession?""",
        "jurisdiction": "State/Local",
        "country": "USA",
        "category": "property",
        "tags": ["property", "real_estate", "landlord_tenant"]
    }
])

# ========== CORPORATE LAW ==========
ALL_CATEGORIES["corporate_law"].extend([
    {
        "title": "USA Corporate Law",
        "content": """USA CORPORATE LAW

BUSINESS ENTITIES:
- Corporation: C-Corp, S-Corp
- LLC: Limited Liability Company
- Partnership: General, Limited, LLP
- Sole Proprietorship

CORPORATE FORMATION:
- Articles of incorporation
- Bylaws
- Board of directors
- Shareholders
- Officers

CORPORATE GOVERNANCE:
- Fiduciary duties
- Business judgment rule
- Shareholder rights
- Director liability

SECURITIES LAW:
- SEC regulations
- Registration requirements
- Disclosure requirements
- Insider trading

Common Questions:
- How do I form a corporation?
- What is the difference between LLC and corporation?
- What are fiduciary duties?
- What is securities law?
- How do I issue stock?""",
        "jurisdiction": "Federal/State",
        "country": "USA",
        "category": "corporate",
        "tags": ["corporate", "business", "securities"]
    }
])

# ========== EMPLOYMENT LAW ==========
ALL_CATEGORIES["employment_law"].extend([
    {
        "title": "USA Employment Law",
        "content": """USA EMPLOYMENT LAW

EMPLOYMENT RELATIONSHIP:
- At-will employment (most states)
- Employment contracts
- Collective bargaining agreements
- Independent contractors vs employees

WAGE AND HOUR:
- Minimum wage (federal and state)
- Overtime (1.5x after 40 hours)
- Break requirements
- Meal periods

DISCRIMINATION:
- Title VII: Race, color, religion, sex, national origin
- Age Discrimination in Employment Act
- Americans with Disabilities Act
- Equal Pay Act

WORKPLACE SAFETY:
- OSHA regulations
- Workers' compensation
- Workplace injuries

Common Questions:
- What is at-will employment?
- What is the minimum wage?
- What are overtime requirements?
- What is workplace discrimination?
- What are my rights as an employee?""",
        "jurisdiction": "Federal/State",
        "country": "USA",
        "category": "employment",
        "tags": ["employment", "labor", "workplace"]
    }
])

# ========== ENVIRONMENTAL LAW ==========
ALL_CATEGORIES["environmental_law"].extend([
    {
        "title": "USA Environmental Law",
        "content": """USA ENVIRONMENTAL LAW

MAJOR STATUTES:
- Clean Air Act
- Clean Water Act
- Resource Conservation and Recovery Act
- Comprehensive Environmental Response, Compensation, and Liability Act (CERCLA/Superfund)
- Endangered Species Act

EPA REGULATIONS:
- Air quality standards
- Water quality standards
- Hazardous waste management
- Toxic substances control

ENFORCEMENT:
- Civil penalties
- Criminal penalties
- Citizen suits
- Administrative enforcement

Common Questions:
- What are EPA regulations?
- What is CERCLA/Superfund?
- What are the penalties for environmental violations?
- What is the Clean Air Act?
- What is the Clean Water Act?""",
        "jurisdiction": "Federal/State",
        "country": "USA",
        "category": "environmental",
        "tags": ["environmental", "epa", "regulations"]
    }
])

# ========== IMMIGRATION LAW ==========
ALL_CATEGORIES["immigration_law"].extend([
    {
        "title": "USA Immigration Law",
        "content": """USA IMMIGRATION LAW

VISAS:
- Non-immigrant visas: Tourist, work, student
- Immigrant visas: Permanent residence
- Family-based immigration
- Employment-based immigration

NATURALIZATION:
- Requirements: 5 years residence (3 if married to citizen)
- English language requirement
- Civics test
- Good moral character

DEPORTATION:
- Grounds for removal
- Removal proceedings
- Defenses: Cancellation of removal, asylum
- Appeals process

Common Questions:
- How do I get a green card?
- What is naturalization?
- What are the requirements for citizenship?
- Can I be deported?
- What is asylum?""",
        "jurisdiction": "Federal",
        "country": "USA",
        "category": "immigration",
        "tags": ["immigration", "visa", "citizenship"]
    }
])

# ========== CONSTITUTIONAL LAW ==========
ALL_CATEGORIES["constitutional_law"].extend([
    {
        "title": "USA Constitutional Law",
        "content": """USA CONSTITUTIONAL LAW

BILL OF RIGHTS:
- First Amendment: Speech, religion, press, assembly, petition
- Second Amendment: Right to bear arms
- Fourth Amendment: Search and seizure
- Fifth Amendment: Due process, self-incrimination, double jeopardy
- Sixth Amendment: Right to counsel, speedy trial, jury
- Eighth Amendment: Cruel and unusual punishment

DUE PROCESS:
- Procedural due process
- Substantive due process
- Equal protection

SEPARATION OF POWERS:
- Executive branch
- Legislative branch
- Judicial branch

FEDERALISM:
- Federal vs state powers
- Supremacy clause
- Commerce clause

Common Questions:
- What are my First Amendment rights?
- What is due process?
- What is equal protection?
- What is the Commerce Clause?
- What is judicial review?""",
        "jurisdiction": "Federal",
        "country": "USA",
        "category": "constitutional",
        "tags": ["constitutional", "bill_of_rights", "due_process"]
    },
    {
        "title": "Canada Constitutional Law - Charter of Rights",
        "content": """CANADA CONSTITUTIONAL LAW - CHARTER OF RIGHTS AND FREEDOMS

FUNDAMENTAL FREEDOMS (Section 2):
- Freedom of conscience and religion
- Freedom of thought, belief, opinion, expression
- Freedom of peaceful assembly
- Freedom of association

LEGAL RIGHTS (Sections 7-14):
- Section 7: Life, liberty, security of person
- Section 8: Search and seizure
- Section 9: Arbitrary detention
- Section 10: Arrest and detention
- Section 11: Criminal proceedings
- Section 12: Cruel and unusual treatment
- Section 13: Self-incrimination
- Section 14: Interpreter

EQUALITY RIGHTS (Section 15):
- Equal protection and benefit
- No discrimination based on: race, national/ethnic origin, color, religion, sex, age, mental/physical disability

SECTION 1 - REASONABLE LIMITS:
- Rights can be limited if demonstrably justified
- Oakes test: Pressing and substantial objective, proportionality

SECTION 24 - REMEDIES:
- Exclusion of evidence
- Stay of proceedings
- Other remedies

Common Questions:
- What are Charter rights?
- What is Section 1 of the Charter?
- What is Section 8 (search and seizure)?
- What is Section 11 (criminal proceedings)?
- What is the Oakes test?
- How do I challenge a Charter violation?
- What are the remedies for Charter violations?""",
        "jurisdiction": "Federal",
        "country": "Canada",
        "category": "constitutional",
        "tags": ["constitutional", "charter", "canada", "rights"]
    }
])

# Save complete dataset
with open(DATA_DIR / "complete_legal_dataset.json", 'w', encoding='utf-8') as f:
    json.dump(ALL_CATEGORIES, f, indent=2, ensure_ascii=False)

# Statistics
total = sum(len(items) for items in ALL_CATEGORIES.values())
categories_with_data = sum(1 for items in ALL_CATEGORIES.values() if items)

print("=" * 80)
print("COMPREHENSIVE LEGAL DATASET CREATED")
print("=" * 80)
print(f"Total Legal Documents: {total}")
print(f"Categories with Data: {categories_with_data}")
print("\nCategory Breakdown:")
for category, items in ALL_CATEGORIES.items():
    if items:
        print(f"  {category}: {len(items)} documents")
print(f"\nSaved to: {DATA_DIR / 'complete_legal_dataset.json'}")
print("=" * 80)
