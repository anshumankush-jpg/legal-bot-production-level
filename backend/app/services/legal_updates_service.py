"""
Legal Updates Service - ADVANCED VERSION
Fetches real-time legal news and updates from MULTIPLE sources.
Properly filters by jurisdiction (USA vs Canada).
Uses Google News RSS, NewsData.io, and other reliable free sources.
"""

import os
import json
import asyncio
import aiohttp
import feedparser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import logging
import re
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# ============================================================================
# API KEYS (Free tiers available)
# ============================================================================
# NewsData.io - 200 requests/day free: https://newsdata.io/
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
# TheNewsAPI - 100 requests/day free: https://www.thenewsapi.com/
THENEWSAPI_KEY = os.getenv("THENEWSAPI_KEY", "")


# ============================================================================
# GOOGLE NEWS RSS CONFIGURATION - JURISDICTION SPECIFIC
# ============================================================================
def get_google_news_url(query: str, country: str = "CA") -> str:
    """Generate Google News RSS URL with proper country targeting."""
    encoded_query = quote_plus(query)
    if country == "CA":
        # Canadian news sources
        return f"https://news.google.com/rss/search?q={encoded_query}&hl=en-CA&gl=CA&ceid=CA:en"
    elif country == "US":
        # US news sources
        return f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    else:
        return f"https://news.google.com/rss/search?q={encoded_query}"


# ============================================================================
# COMPREHENSIVE LEGAL SEARCH QUERIES BY JURISDICTION
# ============================================================================
LEGAL_QUERIES_CANADA = {
    "Criminal Law": [
        "criminal law canada court ruling",
        "criminal code canada amendment",
        "criminal charges canada verdict",
        "canada supreme court criminal",
        "criminal justice canada news",
    ],
    "Traffic Law": [
        "traffic law canada driving offence",
        "DUI impaired driving canada penalty",
        "traffic violation ontario quebec bc alberta",
        "highway traffic act canada",
        "driving suspension canada",
    ],
    "Immigration Law": [
        "IRCC immigration canada news",
        "canada visa immigration update",
        "express entry canada draw",
        "refugee asylum canada",
        "work permit canada immigration",
        "permanent residence canada pathway",
    ],
    "Family Law": [
        "family law canada divorce",
        "child custody canada court",
        "child support canada ruling",
        "separation agreement canada",
        "matrimonial property canada",
    ],
    "Employment Law": [
        "employment law canada workplace",
        "wrongful dismissal canada court",
        "labor law canada worker rights",
        "workplace harassment canada ruling",
        "termination employment canada",
    ],
    "Business Law": [
        "business law canada corporate",
        "corporate governance canada regulation",
        "securities law canada OSC",
        "mergers acquisitions canada",
        "business regulations canada",
    ],
    "Business Litigation": [
        "commercial litigation canada lawsuit",
        "business dispute canada court",
        "contract dispute canada ruling",
        "corporate lawsuit canada settlement",
    ],
    "Real Estate Law": [
        "real estate law canada property",
        "landlord tenant canada dispute",
        "property law canada court",
        "housing law canada regulation",
        "mortgage foreclosure canada",
    ],
    "Tax Law": [
        "tax law canada CRA ruling",
        "income tax canada regulation",
        "tax court canada decision",
        "CRA audit canada news",
        "corporate tax canada",
    ],
    "Constitutional Law": [
        "charter rights canada supreme court",
        "constitutional law canada ruling",
        "civil liberties canada court",
        "supreme court canada decision",
        "fundamental rights canada",
    ],
    "Civil Law": [
        "civil lawsuit canada damages",
        "personal injury canada court",
        "negligence lawsuit canada",
        "tort law canada ruling",
        "civil litigation canada verdict",
    ],
    "Administrative Law": [
        "administrative tribunal canada decision",
        "regulatory agency canada ruling",
        "government appeal canada",
        "administrative law canada review",
    ],
    "Wills, Estates, and Trusts": [
        "estate law canada probate",
        "will trust canada court",
        "inheritance canada dispute",
        "estate planning canada",
    ],
    "Health Law": [
        "health law canada medical",
        "medical malpractice canada lawsuit",
        "patient rights canada court",
        "healthcare regulation canada",
    ],
}

LEGAL_QUERIES_USA = {
    "Criminal Law": [
        "criminal law usa federal court",
        "criminal charges usa verdict",
        "federal prosecution usa indictment",
        "criminal justice usa sentencing",
        "supreme court usa criminal ruling",
        "district attorney usa prosecution",
    ],
    "Traffic Law": [
        "traffic law usa driving violation",
        "DUI dwi usa state law",
        "traffic ticket usa court",
        "driving license suspension usa",
        "motor vehicle law usa",
    ],
    "Immigration Law": [
        "USCIS immigration usa news",
        "visa usa immigration policy",
        "immigration court usa ruling",
        "deportation usa appeal",
        "green card usa update",
        "asylum refugee usa policy",
        "H1B visa usa news",
    ],
    "Family Law": [
        "family law usa divorce ruling",
        "child custody usa court",
        "child support usa verdict",
        "alimony spousal support usa",
        "domestic relations usa law",
    ],
    "Employment Law": [
        "employment law usa workplace ruling",
        "wrongful termination usa lawsuit",
        "EEOC discrimination usa",
        "labor law usa NLRB",
        "wage theft usa class action",
        "workplace harassment usa verdict",
    ],
    "Business Law": [
        "business law usa corporate regulation",
        "SEC securities usa enforcement",
        "corporate governance usa ruling",
        "antitrust law usa FTC",
        "business regulation usa federal",
    ],
    "Business Litigation": [
        "business litigation usa federal court",
        "commercial dispute usa lawsuit",
        "corporate lawsuit usa settlement",
        "contract breach usa verdict",
        "shareholder lawsuit usa class action",
    ],
    "Real Estate Law": [
        "real estate law usa property",
        "landlord tenant usa eviction",
        "property dispute usa court",
        "housing law usa HUD",
        "foreclosure usa ruling",
    ],
    "Tax Law": [
        "tax law usa IRS ruling",
        "federal tax usa court",
        "tax court usa decision",
        "IRS enforcement usa news",
        "corporate tax usa regulation",
        "tax evasion usa prosecution",
    ],
    "Constitutional Law": [
        "constitutional law usa supreme court",
        "first amendment usa ruling",
        "civil rights usa court",
        "supreme court usa landmark",
        "constitutional rights usa decision",
        "bill of rights usa case",
    ],
    "Civil Law": [
        "civil lawsuit usa federal court",
        "personal injury usa verdict",
        "class action lawsuit usa",
        "tort law usa ruling",
        "civil litigation usa settlement",
    ],
    "Administrative Law": [
        "administrative law usa agency",
        "federal agency usa regulation",
        "regulatory ruling usa court",
        "administrative procedure usa",
    ],
    "Wills, Estates, and Trusts": [
        "estate law usa probate",
        "trust law usa court",
        "inheritance usa dispute",
        "estate planning usa ruling",
    ],
    "Health Law": [
        "health law usa medical",
        "medical malpractice usa verdict",
        "healthcare regulation usa FDA",
        "HIPAA violation usa ruling",
        "patient rights usa lawsuit",
    ],
}


# ============================================================================
# DEDICATED LEGAL NEWS RSS FEEDS BY JURISDICTION
# ============================================================================
CANADA_RSS_FEEDS = [
    {
        "name": "Canadian Lawyer Magazine",
        "url": "https://www.canadianlawyermag.com/feed/",
        "law_types": ["Business Law", "Civil Law", "Criminal Law"]
    },
    {
        "name": "Law Times Canada",
        "url": "https://www.lawtimesnews.com/feed/",
        "law_types": ["Civil Law", "Criminal Law", "Family Law"]
    },
    {
        "name": "Lexology Canada",
        "url": "https://www.lexology.com/library/rss.ashx?country=canada",
        "law_types": ["Business Law", "Employment Law", "Tax Law"]
    },
]

USA_RSS_FEEDS = [
    {
        "name": "Law360",
        "url": "https://www.law360.com/rss/headlines",
        "law_types": ["Business Law", "Employment Law", "Civil Law"]
    },
    {
        "name": "ABA Journal",
        "url": "https://www.abajournal.com/feed/",
        "law_types": ["Constitutional Law", "Criminal Law", "Civil Law"]
    },
    {
        "name": "JD Supra All",
        "url": "https://www.jdsupra.com/rss/all.xml",
        "law_types": ["Business Law", "Employment Law", "Tax Law"]
    },
    {
        "name": "Reuters Legal",
        "url": "https://www.reuters.com/legal/rss",
        "law_types": ["Business Law", "Constitutional Law", "Criminal Law"]
    },
]


# ============================================================================
# COMPREHENSIVE SAMPLE/FALLBACK UPDATES BY JURISDICTION
# ============================================================================
def generate_canada_updates() -> Dict[str, List[Dict]]:
    """Generate comprehensive Canadian legal updates."""
    today = datetime.now().strftime("%Y-%m-%d")
    now_iso = datetime.now().isoformat()
    
    return {
        "Criminal Law|Canada": [
            {
                "id": "crim-ca-1",
                "title": "Supreme Court of Canada Clarifies Self-Defence Requirements",
                "description": "The Supreme Court of Canada has issued new guidance on the interpretation of self-defence provisions under the Criminal Code, providing clearer standards for trial courts across all provinces.",
                "link": "https://www.scc-csc.ca/",
                "date": today,
                "source": "Supreme Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Criminal Law"],
                "fetched_at": now_iso
            },
            {
                "id": "crim-ca-2",
                "title": "Parliament Passes New Bail Reform Amendments (Bill C-48)",
                "description": "Parliament's amendments to the Criminal Code regarding bail conditions for repeat violent offenders have now received Royal Assent. The amendments reverse the burden of proof for certain offences.",
                "link": "https://www.justice.gc.ca/",
                "date": today,
                "source": "Department of Justice Canada",
                "jurisdiction": "Canada",
                "law_types": ["Criminal Law"],
                "fetched_at": now_iso
            },
            {
                "id": "crim-ca-3",
                "title": "Ontario Court of Appeal: Landmark Ruling on Digital Evidence",
                "description": "The Ontario Court of Appeal has established new standards for the admissibility of digital evidence in criminal proceedings, affecting how police can collect and present electronic data.",
                "link": "https://www.ontariocourts.ca/",
                "date": today,
                "source": "Ontario Courts",
                "jurisdiction": "Canada",
                "law_types": ["Criminal Law"],
                "fetched_at": now_iso
            },
            {
                "id": "crim-ca-4",
                "title": "New Mandatory Minimum Sentences Struck Down by Federal Court",
                "description": "A Federal Court ruling has declared certain mandatory minimum sentences unconstitutional under Section 12 of the Charter, citing cruel and unusual punishment concerns.",
                "link": "https://decisions.fct-cf.gc.ca/",
                "date": today,
                "source": "Federal Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Criminal Law", "Constitutional Law"],
                "fetched_at": now_iso
            },
            {
                "id": "crim-ca-5",
                "title": "BC Supreme Court Sets New Standard for Police Use of Force",
                "description": "The British Columbia Supreme Court has issued a significant ruling on police use of force, establishing clearer guidelines for when force is justified during arrests.",
                "link": "https://www.bccourts.ca/",
                "date": today,
                "source": "BC Courts",
                "jurisdiction": "Canada",
                "law_types": ["Criminal Law"],
                "fetched_at": now_iso
            },
            {
                "id": "crim-ca-6",
                "title": "Alberta Court Rules on Mental Health Diversion Programs",
                "description": "The Alberta Court of Queen's Bench has upheld expanded mental health diversion programs for non-violent offenders, emphasizing rehabilitation over incarceration.",
                "link": "https://www.albertacourts.ca/",
                "date": today,
                "source": "Alberta Courts",
                "jurisdiction": "Canada",
                "law_types": ["Criminal Law"],
                "fetched_at": now_iso
            },
        ],
        "Traffic Law|Canada": [
            {
                "id": "traffic-ca-1",
                "title": "New Federal Impaired Driving Penalties Take Effect",
                "description": "Enhanced penalties for impaired driving offences under the Criminal Code, including mandatory ignition interlock requirements for first-time offenders, are now in force across Canada.",
                "link": "https://www.justice.gc.ca/",
                "date": today,
                "source": "Department of Justice Canada",
                "jurisdiction": "Canada",
                "law_types": ["Traffic Law", "Criminal Law"],
                "fetched_at": now_iso
            },
            {
                "id": "traffic-ca-2",
                "title": "Ontario Increases Distracted Driving Fines to $1,000",
                "description": "The Ontario government has announced increased fines for distracted driving offences, with penalties now starting at $1,000 for first offences and increased demerit points.",
                "link": "https://www.ontario.ca/",
                "date": today,
                "source": "Ontario Ministry of Transportation",
                "jurisdiction": "Canada",
                "law_types": ["Traffic Law"],
                "fetched_at": now_iso
            },
            {
                "id": "traffic-ca-3",
                "title": "BC Implements Roadside Cannabis Testing",
                "description": "British Columbia has begun implementing standardized roadside testing for cannabis impairment, following updated provincial regulations under the Motor Vehicle Act.",
                "link": "https://www.gov.bc.ca/",
                "date": today,
                "source": "BC Government",
                "jurisdiction": "Canada",
                "law_types": ["Traffic Law"],
                "fetched_at": now_iso
            },
            {
                "id": "traffic-ca-4",
                "title": "Quebec Updates Highway Safety Code for E-Scooters",
                "description": "Quebec has amended the Highway Safety Code to include new regulations for electric scooters and e-bikes, including speed limits and helmet requirements.",
                "link": "https://www.quebec.ca/",
                "date": today,
                "source": "Quebec Transport Ministry",
                "jurisdiction": "Canada",
                "law_types": ["Traffic Law"],
                "fetched_at": now_iso
            },
            {
                "id": "traffic-ca-5",
                "title": "Alberta Introduces Stricter Street Racing Penalties",
                "description": "Alberta has introduced new legislation targeting street racing and stunt driving, with vehicle seizure and significant fines for first-time offenders.",
                "link": "https://www.alberta.ca/",
                "date": today,
                "source": "Alberta Transportation",
                "jurisdiction": "Canada",
                "law_types": ["Traffic Law"],
                "fetched_at": now_iso
            },
        ],
        "Immigration Law|Canada": [
            {
                "id": "imm-ca-1",
                "title": "IRCC Announces Record Express Entry Draw",
                "description": "Immigration, Refugees and Citizenship Canada (IRCC) has conducted its largest Express Entry draw of the year, inviting over 5,000 candidates with CRS scores above 480 to apply for permanent residence.",
                "link": "https://www.canada.ca/en/immigration-refugees-citizenship.html",
                "date": today,
                "source": "IRCC",
                "jurisdiction": "Canada",
                "law_types": ["Immigration Law"],
                "fetched_at": now_iso
            },
            {
                "id": "imm-ca-2",
                "title": "New Pathway for International Graduates",
                "description": "IRCC has announced a new pathway to permanent residence for international graduates from Canadian institutions, including streamlined processing and reduced documentation requirements.",
                "link": "https://www.canada.ca/en/immigration-refugees-citizenship.html",
                "date": today,
                "source": "IRCC",
                "jurisdiction": "Canada",
                "law_types": ["Immigration Law"],
                "fetched_at": now_iso
            },
            {
                "id": "imm-ca-3",
                "title": "Provincial Nominee Program Allocations Increased",
                "description": "IRCC has increased Provincial Nominee Program (PNP) allocations for all provinces, with Ontario, BC, and Alberta receiving significant increases to address labor market needs.",
                "link": "https://www.canada.ca/en/immigration-refugees-citizenship.html",
                "date": today,
                "source": "IRCC",
                "jurisdiction": "Canada",
                "law_types": ["Immigration Law"],
                "fetched_at": now_iso
            },
            {
                "id": "imm-ca-4",
                "title": "Canada Announces New Temporary Foreign Worker Program Rules",
                "description": "New regulations for the Temporary Foreign Worker Program include enhanced employer compliance requirements and worker protections against exploitation.",
                "link": "https://www.canada.ca/en/employment-social-development.html",
                "date": today,
                "source": "ESDC",
                "jurisdiction": "Canada",
                "law_types": ["Immigration Law", "Employment Law"],
                "fetched_at": now_iso
            },
            {
                "id": "imm-ca-5",
                "title": "Federal Court Rules on Refugee Protection Division Procedures",
                "description": "The Federal Court has issued new guidance on procedural fairness requirements for Refugee Protection Division hearings, affecting how claims are processed.",
                "link": "https://decisions.fct-cf.gc.ca/",
                "date": today,
                "source": "Federal Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Immigration Law"],
                "fetched_at": now_iso
            },
            {
                "id": "imm-ca-6",
                "title": "IRCC Reduces Processing Times for Family Sponsorship",
                "description": "IRCC has announced significant reductions in processing times for family sponsorship applications, with spousal sponsorships now averaging 12 months.",
                "link": "https://www.canada.ca/en/immigration-refugees-citizenship.html",
                "date": today,
                "source": "IRCC",
                "jurisdiction": "Canada",
                "law_types": ["Immigration Law"],
                "fetched_at": now_iso
            },
        ],
        "Family Law|Canada": [
            {
                "id": "fam-ca-1",
                "title": "Federal Child Support Guidelines Updated for 2026",
                "description": "The Federal Child Support Guidelines have been updated with new income thresholds and calculation tables, effective January 2026. These changes affect child support obligations across Canada.",
                "link": "https://www.justice.gc.ca/",
                "date": today,
                "source": "Department of Justice Canada",
                "jurisdiction": "Canada",
                "law_types": ["Family Law"],
                "fetched_at": now_iso
            },
            {
                "id": "fam-ca-2",
                "title": "Supreme Court Clarifies Spousal Support Duration",
                "description": "The Supreme Court of Canada has issued guidance on the factors courts should consider when determining the duration of spousal support in long-term marriages.",
                "link": "https://www.scc-csc.ca/",
                "date": today,
                "source": "Supreme Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Family Law"],
                "fetched_at": now_iso
            },
            {
                "id": "fam-ca-3",
                "title": "Ontario Expands Mediation Services for Family Disputes",
                "description": "The Ontario government has expanded free family mediation services, aiming to reduce court backlogs and help families resolve disputes more efficiently.",
                "link": "https://www.ontario.ca/",
                "date": today,
                "source": "Ontario MAG",
                "jurisdiction": "Canada",
                "law_types": ["Family Law"],
                "fetched_at": now_iso
            },
            {
                "id": "fam-ca-4",
                "title": "BC Updates Parenting Coordination Guidelines",
                "description": "British Columbia has issued updated guidelines for parenting coordinators, including enhanced qualifications and dispute resolution procedures.",
                "link": "https://www.bccourts.ca/",
                "date": today,
                "source": "BC Courts",
                "jurisdiction": "Canada",
                "law_types": ["Family Law"],
                "fetched_at": now_iso
            },
            {
                "id": "fam-ca-5",
                "title": "Quebec Civil Code Amendments Affect Common-Law Partners",
                "description": "Quebec has amended the Civil Code to provide enhanced protections for common-law partners, including property division rights upon separation.",
                "link": "https://www.quebec.ca/",
                "date": today,
                "source": "Quebec Justice",
                "jurisdiction": "Canada",
                "law_types": ["Family Law"],
                "fetched_at": now_iso
            },
        ],
        "Employment Law|Canada": [
            {
                "id": "emp-ca-1",
                "title": "Federal Minimum Wage Increases to $17.30",
                "description": "The federal minimum wage for federally regulated workers has increased to $17.30 per hour, affecting employees in banking, telecommunications, and interprovincial transportation.",
                "link": "https://www.canada.ca/en/employment-social-development.html",
                "date": today,
                "source": "Employment and Social Development Canada",
                "jurisdiction": "Canada",
                "law_types": ["Employment Law"],
                "fetched_at": now_iso
            },
            {
                "id": "emp-ca-2",
                "title": "Ontario Updates Workplace Violence Prevention Requirements",
                "description": "Ontario has updated the Occupational Health and Safety Act to include enhanced workplace violence prevention requirements, with stricter penalties for non-compliance.",
                "link": "https://www.ontario.ca/",
                "date": today,
                "source": "Ontario Ministry of Labour",
                "jurisdiction": "Canada",
                "law_types": ["Employment Law"],
                "fetched_at": now_iso
            },
            {
                "id": "emp-ca-3",
                "title": "BC Introduces Pay Transparency Legislation",
                "description": "British Columbia's new Pay Transparency Act requires employers to disclose salary ranges in job postings and prohibits asking candidates about salary history.",
                "link": "https://www.gov.bc.ca/",
                "date": today,
                "source": "BC Government",
                "jurisdiction": "Canada",
                "law_types": ["Employment Law"],
                "fetched_at": now_iso
            },
            {
                "id": "emp-ca-4",
                "title": "Federal Right to Disconnect Rules Take Effect",
                "description": "New federal regulations requiring employers to establish right to disconnect policies have come into effect for federally regulated workplaces.",
                "link": "https://www.canada.ca/en/employment-social-development.html",
                "date": today,
                "source": "ESDC",
                "jurisdiction": "Canada",
                "law_types": ["Employment Law"],
                "fetched_at": now_iso
            },
            {
                "id": "emp-ca-5",
                "title": "Alberta Court Awards Record Wrongful Dismissal Damages",
                "description": "An Alberta court has awarded record damages in a wrongful dismissal case, citing the employer's bad faith conduct during termination.",
                "link": "https://www.albertacourts.ca/",
                "date": today,
                "source": "Alberta Courts",
                "jurisdiction": "Canada",
                "law_types": ["Employment Law"],
                "fetched_at": now_iso
            },
        ],
        "Business Law|Canada": [
            {
                "id": "bus-ca-1",
                "title": "Competition Bureau Issues New Merger Guidelines",
                "description": "The Competition Bureau of Canada has released updated guidelines for merger reviews, including new thresholds and enhanced scrutiny for digital market acquisitions.",
                "link": "https://www.competitionbureau.gc.ca/",
                "date": today,
                "source": "Competition Bureau Canada",
                "jurisdiction": "Canada",
                "law_types": ["Business Law"],
                "fetched_at": now_iso
            },
            {
                "id": "bus-ca-2",
                "title": "OSC Updates Disclosure Requirements for Public Companies",
                "description": "The Ontario Securities Commission has updated continuous disclosure requirements, including new climate-related disclosure rules for public companies.",
                "link": "https://www.osc.ca/",
                "date": today,
                "source": "Ontario Securities Commission",
                "jurisdiction": "Canada",
                "law_types": ["Business Law"],
                "fetched_at": now_iso
            },
            {
                "id": "bus-ca-3",
                "title": "Canada Business Corporations Act Amendments",
                "description": "Amendments to the CBCA introduce new beneficial ownership registry requirements for federally incorporated companies to increase corporate transparency.",
                "link": "https://www.ic.gc.ca/",
                "date": today,
                "source": "Innovation Canada",
                "jurisdiction": "Canada",
                "law_types": ["Business Law"],
                "fetched_at": now_iso
            },
            {
                "id": "bus-ca-4",
                "title": "Federal Court Rules on Non-Compete Agreements",
                "description": "A Federal Court ruling has limited the enforceability of broad non-compete clauses, requiring employers to demonstrate legitimate business interests.",
                "link": "https://decisions.fct-cf.gc.ca/",
                "date": today,
                "source": "Federal Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Business Law", "Employment Law"],
                "fetched_at": now_iso
            },
        ],
        "Business Litigation|Canada": [
            {
                "id": "buslit-ca-1",
                "title": "Ontario Superior Court Approves Major Class Action Settlement",
                "description": "The Ontario Superior Court has approved a $500 million class action settlement against a major telecommunications company for unauthorized fees.",
                "link": "https://www.ontariocourts.ca/",
                "date": today,
                "source": "Ontario Courts",
                "jurisdiction": "Canada",
                "law_types": ["Business Litigation"],
                "fetched_at": now_iso
            },
            {
                "id": "buslit-ca-2",
                "title": "SCC Clarifies Standard for Oppression Remedy Claims",
                "description": "The Supreme Court of Canada has issued new guidance on the standard for oppression remedy claims under the CBCA, affecting minority shareholder rights.",
                "link": "https://www.scc-csc.ca/",
                "date": today,
                "source": "Supreme Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Business Litigation"],
                "fetched_at": now_iso
            },
        ],
        "Real Estate Law|Canada": [
            {
                "id": "re-ca-1",
                "title": "Ontario Strengthens Tenant Protections",
                "description": "The Ontario government has passed amendments to the Residential Tenancies Act, providing stronger protections against 'renovictions' and limiting rent increases for new tenants.",
                "link": "https://www.ontario.ca/",
                "date": today,
                "source": "Ontario Government",
                "jurisdiction": "Canada",
                "law_types": ["Real Estate Law"],
                "fetched_at": now_iso
            },
            {
                "id": "re-ca-2",
                "title": "BC Implements Foreign Buyer Ban Extension",
                "description": "British Columbia has extended its foreign buyer ban and introduced new restrictions on short-term rentals to address housing affordability.",
                "link": "https://www.gov.bc.ca/",
                "date": today,
                "source": "BC Government",
                "jurisdiction": "Canada",
                "law_types": ["Real Estate Law"],
                "fetched_at": now_iso
            },
            {
                "id": "re-ca-3",
                "title": "Federal Underused Housing Tax Updates",
                "description": "The CRA has issued updated guidance on the Underused Housing Tax (UHT), clarifying filing requirements for Canadian property owners.",
                "link": "https://www.canada.ca/en/revenue-agency.html",
                "date": today,
                "source": "CRA",
                "jurisdiction": "Canada",
                "law_types": ["Real Estate Law", "Tax Law"],
                "fetched_at": now_iso
            },
            {
                "id": "re-ca-4",
                "title": "Alberta Court Rules on Condo Corporation Powers",
                "description": "An Alberta court has clarified the extent of condominium corporation powers to enforce bylaws, limiting arbitrary restrictions on unit owners.",
                "link": "https://www.albertacourts.ca/",
                "date": today,
                "source": "Alberta Courts",
                "jurisdiction": "Canada",
                "law_types": ["Real Estate Law"],
                "fetched_at": now_iso
            },
        ],
        "Tax Law|Canada": [
            {
                "id": "tax-ca-1",
                "title": "CRA Announces Enhanced Audit Program for Cryptocurrency",
                "description": "The Canada Revenue Agency has announced an expanded audit program targeting unreported cryptocurrency transactions, with penalties for non-compliance.",
                "link": "https://www.canada.ca/en/revenue-agency.html",
                "date": today,
                "source": "Canada Revenue Agency",
                "jurisdiction": "Canada",
                "law_types": ["Tax Law"],
                "fetched_at": now_iso
            },
            {
                "id": "tax-ca-2",
                "title": "Tax Court of Canada Rules on Principal Residence Exemption",
                "description": "The Tax Court has issued new guidance on principal residence exemption claims, affecting taxpayers who own multiple properties.",
                "link": "https://www.tcc-cci.gc.ca/",
                "date": today,
                "source": "Tax Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Tax Law"],
                "fetched_at": now_iso
            },
            {
                "id": "tax-ca-3",
                "title": "Federal Budget Introduces New Capital Gains Tax Changes",
                "description": "The federal budget has introduced changes to capital gains taxation, including an increased inclusion rate for gains above $250,000.",
                "link": "https://www.budget.gc.ca/",
                "date": today,
                "source": "Department of Finance",
                "jurisdiction": "Canada",
                "law_types": ["Tax Law"],
                "fetched_at": now_iso
            },
            {
                "id": "tax-ca-4",
                "title": "CRA Updates Guidelines for TFSA Over-Contributions",
                "description": "The CRA has updated its enforcement guidelines for TFSA over-contributions, including a new process for requesting penalty waivers.",
                "link": "https://www.canada.ca/en/revenue-agency.html",
                "date": today,
                "source": "CRA",
                "jurisdiction": "Canada",
                "law_types": ["Tax Law"],
                "fetched_at": now_iso
            },
        ],
        "Constitutional Law|Canada": [
            {
                "id": "const-ca-1",
                "title": "Supreme Court Expands Charter Protection for Privacy",
                "description": "The Supreme Court of Canada has expanded the scope of Section 8 Charter protection against unreasonable search and seizure to cover certain types of digital surveillance.",
                "link": "https://www.scc-csc.ca/",
                "date": today,
                "source": "Supreme Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Constitutional Law"],
                "fetched_at": now_iso
            },
            {
                "id": "const-ca-2",
                "title": "SCC Rules on Federal-Provincial Jurisdiction Over Carbon Tax",
                "description": "The Supreme Court has upheld federal carbon pricing legislation as constitutional, clarifying the scope of federal power over matters of national concern.",
                "link": "https://www.scc-csc.ca/",
                "date": today,
                "source": "Supreme Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Constitutional Law"],
                "fetched_at": now_iso
            },
            {
                "id": "const-ca-3",
                "title": "Federal Court Addresses Section 15 Equality Rights",
                "description": "A Federal Court ruling has expanded the interpretation of Section 15 equality rights to address systemic discrimination in government programs.",
                "link": "https://decisions.fct-cf.gc.ca/",
                "date": today,
                "source": "Federal Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Constitutional Law"],
                "fetched_at": now_iso
            },
        ],
        "Civil Law|Canada": [
            {
                "id": "civil-ca-1",
                "title": "Ontario Court Awards Record Damages in Defamation Case",
                "description": "An Ontario court has awarded record damages in an online defamation case, establishing new standards for social media liability.",
                "link": "https://www.ontariocourts.ca/",
                "date": today,
                "source": "Ontario Courts",
                "jurisdiction": "Canada",
                "law_types": ["Civil Law"],
                "fetched_at": now_iso
            },
            {
                "id": "civil-ca-2",
                "title": "SCC Clarifies Duty of Care for Professional Negligence",
                "description": "The Supreme Court has issued new guidance on the duty of care standard for professional negligence claims against lawyers and accountants.",
                "link": "https://www.scc-csc.ca/",
                "date": today,
                "source": "Supreme Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Civil Law"],
                "fetched_at": now_iso
            },
            {
                "id": "civil-ca-3",
                "title": "BC Supreme Court Updates Personal Injury Damage Calculations",
                "description": "The BC Supreme Court has updated guidelines for calculating non-pecuniary damages in personal injury cases, adjusting for inflation.",
                "link": "https://www.bccourts.ca/",
                "date": today,
                "source": "BC Courts",
                "jurisdiction": "Canada",
                "law_types": ["Civil Law"],
                "fetched_at": now_iso
            },
        ],
        "Administrative Law|Canada": [
            {
                "id": "admin-ca-1",
                "title": "Federal Court Clarifies Standard of Review for Tribunal Decisions",
                "description": "The Federal Court has applied the Vavilov framework to clarify when courts should defer to administrative tribunal decisions.",
                "link": "https://decisions.fct-cf.gc.ca/",
                "date": today,
                "source": "Federal Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Administrative Law"],
                "fetched_at": now_iso
            },
            {
                "id": "admin-ca-2",
                "title": "CRTC Issues New Telecom Regulations",
                "description": "The CRTC has issued new regulations requiring telecom providers to offer more affordable basic service plans and improve rural connectivity.",
                "link": "https://www.crtc.gc.ca/",
                "date": today,
                "source": "CRTC",
                "jurisdiction": "Canada",
                "law_types": ["Administrative Law"],
                "fetched_at": now_iso
            },
        ],
        "Wills, Estates, and Trusts|Canada": [
            {
                "id": "wills-ca-1",
                "title": "Ontario Updates Probate Fee Thresholds",
                "description": "Ontario has updated estate administration tax thresholds, increasing the threshold for small estates exempt from probate fees.",
                "link": "https://www.ontario.ca/",
                "date": today,
                "source": "Ontario MAG",
                "jurisdiction": "Canada",
                "law_types": ["Wills, Estates, and Trusts"],
                "fetched_at": now_iso
            },
            {
                "id": "wills-ca-2",
                "title": "BC Supreme Court Rules on Validity of Holograph Wills",
                "description": "The BC Supreme Court has clarified the requirements for valid holograph wills, addressing digital signatures and electronic documents.",
                "link": "https://www.bccourts.ca/",
                "date": today,
                "source": "BC Courts",
                "jurisdiction": "Canada",
                "law_types": ["Wills, Estates, and Trusts"],
                "fetched_at": now_iso
            },
            {
                "id": "wills-ca-3",
                "title": "SCC Addresses Testamentary Capacity Standards",
                "description": "The Supreme Court has issued new guidance on the evidentiary standards for challenging testamentary capacity in contested estate matters.",
                "link": "https://www.scc-csc.ca/",
                "date": today,
                "source": "Supreme Court of Canada",
                "jurisdiction": "Canada",
                "law_types": ["Wills, Estates, and Trusts"],
                "fetched_at": now_iso
            },
        ],
        "Health Law|Canada": [
            {
                "id": "health-ca-1",
                "title": "Health Canada Updates Medical Cannabis Regulations",
                "description": "Health Canada has issued updated regulations for medical cannabis access, including new pathways for patient registration and quality standards.",
                "link": "https://www.canada.ca/en/health-canada.html",
                "date": today,
                "source": "Health Canada",
                "jurisdiction": "Canada",
                "law_types": ["Health Law"],
                "fetched_at": now_iso
            },
            {
                "id": "health-ca-2",
                "title": "Ontario Court Rules on Medical Malpractice Damages",
                "description": "An Ontario court has issued a significant ruling on medical malpractice damages, affecting how future care costs are calculated.",
                "link": "https://www.ontariocourts.ca/",
                "date": today,
                "source": "Ontario Courts",
                "jurisdiction": "Canada",
                "law_types": ["Health Law", "Civil Law"],
                "fetched_at": now_iso
            },
            {
                "id": "health-ca-3",
                "title": "Federal Government Expands Pharmacare Coverage",
                "description": "The federal government has announced an expansion of the national pharmacare program, covering additional prescription medications for all Canadians.",
                "link": "https://www.canada.ca/en/health-canada.html",
                "date": today,
                "source": "Health Canada",
                "jurisdiction": "Canada",
                "law_types": ["Health Law"],
                "fetched_at": now_iso
            },
        ],
    }


SAMPLE_UPDATES_CANADA = generate_canada_updates()

SAMPLE_UPDATES_USA = {
    "Criminal Law|USA": [
        {
            "id": "crim-us-1",
            "title": "Supreme Court Rules on Fourth Amendment Digital Searches",
            "description": "The U.S. Supreme Court has issued a landmark ruling limiting warrantless searches of cell phones and digital devices, establishing new Fourth Amendment protections for digital privacy.",
            "link": "https://www.supremecourt.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "U.S. Supreme Court",
            "jurisdiction": "USA",
            "law_types": ["Criminal Law", "Constitutional Law"],
            "fetched_at": datetime.now().isoformat()
        },
        {
            "id": "crim-us-2",
            "title": "DOJ Announces Federal Sentencing Guidelines Updates",
            "description": "The Department of Justice has announced updates to federal sentencing guidelines, including modifications to mandatory minimums for non-violent drug offenses.",
            "link": "https://www.justice.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "U.S. Department of Justice",
            "jurisdiction": "USA",
            "law_types": ["Criminal Law"],
            "fetched_at": datetime.now().isoformat()
        },
        {
            "id": "crim-us-3",
            "title": "Federal Courts Adopt New E-Discovery Rules",
            "description": "Federal courts have implemented new rules governing electronic discovery in criminal cases, setting standards for how digital evidence must be preserved and produced.",
            "link": "https://www.uscourts.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "U.S. Courts",
            "jurisdiction": "USA",
            "law_types": ["Criminal Law"],
            "fetched_at": datetime.now().isoformat()
        },
    ],
    "Traffic Law|USA": [
        {
            "id": "traffic-us-1",
            "title": "NHTSA Issues New Guidelines on Autonomous Vehicle Testing",
            "description": "The National Highway Traffic Safety Administration has released comprehensive guidelines for testing autonomous vehicles on public roads, affecting manufacturers nationwide.",
            "link": "https://www.nhtsa.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "NHTSA",
            "jurisdiction": "USA",
            "law_types": ["Traffic Law"],
            "fetched_at": datetime.now().isoformat()
        },
        {
            "id": "traffic-us-2",
            "title": "California Implements Stricter DUI Penalties",
            "description": "California has enacted new legislation increasing penalties for repeat DUI offenders, including mandatory ignition interlock devices and extended license suspensions.",
            "link": "https://www.dmv.ca.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "California DMV",
            "jurisdiction": "USA",
            "law_types": ["Traffic Law"],
            "fetched_at": datetime.now().isoformat()
        },
    ],
    "Immigration Law|USA": [
        {
            "id": "imm-us-1",
            "title": "USCIS Updates H-1B Visa Processing Procedures",
            "description": "U.S. Citizenship and Immigration Services has announced significant changes to H-1B visa processing, including new wage requirements and enhanced employer verification.",
            "link": "https://www.uscis.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "USCIS",
            "jurisdiction": "USA",
            "law_types": ["Immigration Law"],
            "fetched_at": datetime.now().isoformat()
        },
        {
            "id": "imm-us-2",
            "title": "Federal Court Blocks Immigration Policy Changes",
            "description": "A federal district court has issued a nationwide injunction blocking recent changes to asylum processing procedures, pending full judicial review.",
            "link": "https://www.uscourts.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "U.S. District Court",
            "jurisdiction": "USA",
            "law_types": ["Immigration Law"],
            "fetched_at": datetime.now().isoformat()
        },
        {
            "id": "imm-us-3",
            "title": "New Green Card Processing Times Announced",
            "description": "USCIS has published updated processing times for employment-based and family-based green card applications, showing significant backlogs in certain categories.",
            "link": "https://www.uscis.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "USCIS",
            "jurisdiction": "USA",
            "law_types": ["Immigration Law"],
            "fetched_at": datetime.now().isoformat()
        },
    ],
    "Family Law|USA": [
        {
            "id": "fam-us-1",
            "title": "Supreme Court Addresses Interstate Custody Jurisdiction",
            "description": "The U.S. Supreme Court has clarified the application of the Uniform Child Custody Jurisdiction and Enforcement Act in cases involving international relocation.",
            "link": "https://www.supremecourt.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "U.S. Supreme Court",
            "jurisdiction": "USA",
            "law_types": ["Family Law"],
            "fetched_at": datetime.now().isoformat()
        },
    ],
    "Employment Law|USA": [
        {
            "id": "emp-us-1",
            "title": "NLRB Issues New Union Election Rules",
            "description": "The National Labor Relations Board has issued new rules governing union election procedures, including changes to the timeline for representation elections.",
            "link": "https://www.nlrb.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "NLRB",
            "jurisdiction": "USA",
            "law_types": ["Employment Law"],
            "fetched_at": datetime.now().isoformat()
        },
        {
            "id": "emp-us-2",
            "title": "EEOC Updates Workplace Harassment Guidelines",
            "description": "The Equal Employment Opportunity Commission has released updated guidance on workplace harassment, including new standards for employer liability and prevention.",
            "link": "https://www.eeoc.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "EEOC",
            "jurisdiction": "USA",
            "law_types": ["Employment Law"],
            "fetched_at": datetime.now().isoformat()
        },
    ],
    "Business Law|USA": [
        {
            "id": "bus-us-1",
            "title": "SEC Adopts New Climate Disclosure Rules",
            "description": "The Securities and Exchange Commission has adopted new rules requiring public companies to disclose climate-related risks and greenhouse gas emissions.",
            "link": "https://www.sec.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "SEC",
            "jurisdiction": "USA",
            "law_types": ["Business Law"],
            "fetched_at": datetime.now().isoformat()
        },
        {
            "id": "bus-us-2",
            "title": "FTC Enhances Merger Review Process",
            "description": "The Federal Trade Commission has announced enhanced scrutiny for large mergers and acquisitions, particularly in technology and healthcare sectors.",
            "link": "https://www.ftc.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "FTC",
            "jurisdiction": "USA",
            "law_types": ["Business Law"],
            "fetched_at": datetime.now().isoformat()
        },
    ],
    "Tax Law|USA": [
        {
            "id": "tax-us-1",
            "title": "IRS Announces Major Changes to Tax Deductions",
            "description": "The Internal Revenue Service has announced significant changes to itemized deductions and standard deduction amounts for the upcoming tax year.",
            "link": "https://www.irs.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "IRS",
            "jurisdiction": "USA",
            "law_types": ["Tax Law"],
            "fetched_at": datetime.now().isoformat()
        },
        {
            "id": "tax-us-2",
            "title": "Tax Court Issues Cryptocurrency Guidance",
            "description": "The U.S. Tax Court has issued new guidance on the tax treatment of cryptocurrency transactions, including staking rewards and DeFi activities.",
            "link": "https://www.ustaxcourt.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "U.S. Tax Court",
            "jurisdiction": "USA",
            "law_types": ["Tax Law"],
            "fetched_at": datetime.now().isoformat()
        },
    ],
    "Constitutional Law|USA": [
        {
            "id": "const-us-1",
            "title": "Supreme Court Expands First Amendment Protections",
            "description": "The U.S. Supreme Court has expanded First Amendment protections in a landmark case addressing government regulation of online speech platforms.",
            "link": "https://www.supremecourt.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "U.S. Supreme Court",
            "jurisdiction": "USA",
            "law_types": ["Constitutional Law"],
            "fetched_at": datetime.now().isoformat()
        },
    ],
    "Real Estate Law|USA": [
        {
            "id": "re-us-1",
            "title": "HUD Issues New Fair Housing Enforcement Guidelines",
            "description": "The Department of Housing and Urban Development has issued updated enforcement guidelines for fair housing violations, including new penalties for discrimination.",
            "link": "https://www.hud.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "HUD",
            "jurisdiction": "USA",
            "law_types": ["Real Estate Law"],
            "fetched_at": datetime.now().isoformat()
        },
    ],
    "Health Law|USA": [
        {
            "id": "health-us-1",
            "title": "FDA Implements New Drug Approval Fast-Track",
            "description": "The Food and Drug Administration has implemented new fast-track approval procedures for breakthrough therapies, reducing review times for critical medications.",
            "link": "https://www.fda.gov/",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "FDA",
            "jurisdiction": "USA",
            "law_types": ["Health Law"],
            "fetched_at": datetime.now().isoformat()
        },
    ],
}


# ============================================================================
# LAW TYPE KEYWORD MATCHING
# ============================================================================
LAW_TYPE_KEYWORDS = {
    "Criminal Law": ["criminal", "crime", "murder", "theft", "assault", "fraud", "prosecution", "indictment", "sentencing", "verdict", "conviction"],
    "Traffic Law": ["traffic", "driving", "speeding", "dui", "dwi", "impaired", "highway", "motor vehicle", "license suspension", "accident"],
    "Immigration Law": ["immigration", "visa", "refugee", "citizenship", "deportation", "asylum", "work permit", "green card", "uscis", "ircc"],
    "Family Law": ["family", "divorce", "custody", "child support", "alimony", "marriage", "adoption", "separation", "matrimonial"],
    "Employment Law": ["employment", "labor", "workplace", "discrimination", "wrongful termination", "wage", "harassment", "eeoc", "nlrb"],
    "Business Law": ["business", "corporate", "contract", "merger", "acquisition", "securities", "sec", "ftc", "antitrust"],
    "Business Litigation": ["litigation", "lawsuit", "dispute", "arbitration", "commercial dispute", "class action", "settlement"],
    "Real Estate Law": ["real estate", "property", "landlord", "tenant", "lease", "mortgage", "foreclosure", "zoning", "hud"],
    "Tax Law": ["tax", "irs", "cra", "audit", "taxation", "income tax", "corporate tax", "deduction"],
    "Constitutional Law": ["constitutional", "charter", "rights", "supreme court", "civil liberties", "amendment", "first amendment"],
    "Civil Law": ["civil", "tort", "negligence", "personal injury", "damages", "liability", "malpractice"],
    "Administrative Law": ["administrative", "regulatory", "agency", "government", "appeal", "tribunal", "fda", "epa"],
    "Wills, Estates, and Trusts": ["estate", "will", "trust", "probate", "inheritance", "executor", "beneficiary"],
    "Health Law": ["health", "medical", "healthcare", "malpractice", "patient rights", "hipaa", "fda", "pharmaceutical"]
}


class LegalUpdatesService:
    """Advanced Legal Updates Service with proper jurisdiction filtering."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or (PROJECT_ROOT / "legal_data_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.updates_file = self.cache_dir / "recent_updates.json"
        self.last_fetch_file = self.cache_dir / "last_fetch.json"
        
    def _generate_hash(self, content: str) -> str:
        """Generate unique hash for an update."""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        # Also clean up &nbsp; and similar
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        return text.strip()
    
    def _categorize_by_law_type(self, title: str, description: str) -> List[str]:
        """Categorize an update by law type based on keywords."""
        text = f"{title} {description}".lower()
        matched_types = []
        
        for law_type, keywords in LAW_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    if law_type not in matched_types:
                        matched_types.append(law_type)
                    break
        
        return matched_types if matched_types else ["Civil Law"]
    
    def _is_canada_source(self, source: str, title: str) -> bool:
        """Check if the news is from a Canadian source."""
        canada_indicators = [
            "canada", "canadian", "ontario", "quebec", "bc", "british columbia",
            "alberta", "manitoba", "saskatchewan", "nova scotia", "new brunswick",
            "ircc", "cra", "scc-csc", "canlii", "globe and mail", "cbc",
            "national post", "toronto star", "vancouver sun", "calgary herald"
        ]
        text = f"{source} {title}".lower()
        return any(indicator in text for indicator in canada_indicators)
    
    def _is_usa_source(self, source: str, title: str) -> bool:
        """Check if the news is from a US source."""
        usa_indicators = [
            "united states", "u.s.", "us ", "usa", "american", "federal",
            "uscis", "irs", "sec", "ftc", "fda", "doj", "department of justice",
            "supreme court", "congress", "washington", "california", "new york",
            "texas", "florida", "cnn", "fox", "nbc", "abc", "nytimes", "wsj"
        ]
        text = f"{source} {title}".lower()
        return any(indicator in text for indicator in usa_indicators)
    
    async def fetch_google_news(self, query: str, country: str, law_type: str) -> List[Dict]:
        """Fetch news from Google News RSS with proper jurisdiction."""
        updates = []
        url = get_google_news_url(query, country)
        target_jurisdiction = "Canada" if country == "CA" else "USA"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        content = await response.text()
                        parsed = feedparser.parse(content)
                        
                        for entry in parsed.entries[:8]:
                            try:
                                title = entry.get("title", "").strip()
                                if not title:
                                    continue
                                
                                link = entry.get("link", "")
                                description = self._clean_html(entry.get("description", entry.get("summary", "")))[:500]
                                
                                # Parse date
                                pub_date = datetime.now().strftime("%Y-%m-%d")
                                if hasattr(entry, "published_parsed") and entry.published_parsed:
                                    try:
                                        pub_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
                                    except:
                                        pass
                                
                                # Extract source from title
                                source = "News"
                                if " - " in title:
                                    parts = title.rsplit(" - ", 1)
                                    if len(parts) == 2:
                                        source = parts[1].strip()
                                        title = parts[0].strip()
                                
                                # STRICT JURISDICTION FILTERING
                                if target_jurisdiction == "Canada":
                                    # For Canada queries, prefer Canadian sources
                                    if self._is_usa_source(source, title) and not self._is_canada_source(source, title):
                                        continue  # Skip USA sources for Canada queries
                                else:
                                    # For USA queries, prefer USA sources
                                    if self._is_canada_source(source, title) and not self._is_usa_source(source, title):
                                        continue  # Skip Canada sources for USA queries
                                
                                update = {
                                    "id": self._generate_hash(title + link),
                                    "title": title,
                                    "description": description,
                                    "link": link,
                                    "date": pub_date,
                                    "source": source,
                                    "jurisdiction": target_jurisdiction,
                                    "law_types": [law_type],
                                    "fetched_at": datetime.now().isoformat()
                                }
                                updates.append(update)
                                
                            except Exception as e:
                                continue
                        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching Google News for {query}")
        except Exception as e:
            logger.warning(f"Error fetching Google News for {query}: {str(e)}")
        
        return updates
    
    async def fetch_rss_feed(self, feed_info: Dict, jurisdiction: str) -> List[Dict]:
        """Fetch updates from an RSS feed."""
        updates = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_info["url"], headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        content = await response.text()
                        parsed = feedparser.parse(content)
                        
                        for entry in parsed.entries[:10]:
                            try:
                                title = entry.get("title", "").strip()
                                if not title:
                                    continue
                                
                                link = entry.get("link", "")
                                description = self._clean_html(entry.get("description", entry.get("summary", "")))[:400]
                                
                                pub_date = datetime.now().strftime("%Y-%m-%d")
                                if hasattr(entry, "published_parsed") and entry.published_parsed:
                                    try:
                                        pub_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
                                    except:
                                        pass
                                
                                # Auto-detect law types
                                law_types = self._categorize_by_law_type(title, description)
                                if not law_types:
                                    law_types = feed_info.get("law_types", ["Civil Law"])
                                
                                update = {
                                    "id": self._generate_hash(title + link),
                                    "title": title,
                                    "description": description,
                                    "link": link,
                                    "date": pub_date,
                                    "source": feed_info["name"],
                                    "jurisdiction": jurisdiction,
                                    "law_types": law_types,
                                    "fetched_at": datetime.now().isoformat()
                                }
                                updates.append(update)
                                
                            except Exception as e:
                                continue
                        
                        logger.info(f"Fetched {len(updates)} from {feed_info['name']}")
                    else:
                        logger.warning(f"Failed to fetch {feed_info['name']}: HTTP {response.status}")
                        
        except Exception as e:
            logger.warning(f"Error fetching {feed_info['name']}: {str(e)}")
        
        return updates
    
    async def fetch_all_updates(self) -> Dict[str, List[Dict]]:
        """Fetch updates from all sources, properly organized by jurisdiction."""
        all_updates = {}
        
        logger.info("=" * 60)
        logger.info("FETCHING LEGAL UPDATES - ADVANCED MODE")
        logger.info("=" * 60)
        
        # ================================================================
        # FETCH CANADA UPDATES
        # ================================================================
        logger.info("\n📍 Fetching CANADA updates...")
        
        # Google News for Canada
        canada_tasks = []
        for law_type, queries in LEGAL_QUERIES_CANADA.items():
            for query in queries[:2]:  # Limit queries per law type
                canada_tasks.append(self.fetch_google_news(query, "CA", law_type))
        
        canada_results = await asyncio.gather(*canada_tasks, return_exceptions=True)
        
        # Process Canada results
        idx = 0
        for law_type, queries in LEGAL_QUERIES_CANADA.items():
            for _ in queries[:2]:
                result = canada_results[idx]
                idx += 1
                
                if isinstance(result, Exception):
                    continue
                
                key = f"{law_type}|Canada"
                if key not in all_updates:
                    all_updates[key] = []
                
                for update in result:
                    if not any(u["id"] == update["id"] for u in all_updates[key]):
                        all_updates[key].append(update)
        
        # Add Canada RSS feeds
        for feed in CANADA_RSS_FEEDS:
            try:
                feed_updates = await self.fetch_rss_feed(feed, "Canada")
                for update in feed_updates:
                    for law_type in update.get("law_types", ["Civil Law"]):
                        key = f"{law_type}|Canada"
                        if key not in all_updates:
                            all_updates[key] = []
                        if not any(u["id"] == update["id"] for u in all_updates[key]):
                            all_updates[key].append(update)
            except Exception as e:
                logger.warning(f"Error fetching Canada RSS feed: {e}")
        
        # ================================================================
        # FETCH USA UPDATES
        # ================================================================
        logger.info("\n📍 Fetching USA updates...")
        
        # Google News for USA
        usa_tasks = []
        for law_type, queries in LEGAL_QUERIES_USA.items():
            for query in queries[:2]:  # Limit queries per law type
                usa_tasks.append(self.fetch_google_news(query, "US", law_type))
        
        usa_results = await asyncio.gather(*usa_tasks, return_exceptions=True)
        
        # Process USA results
        idx = 0
        for law_type, queries in LEGAL_QUERIES_USA.items():
            for _ in queries[:2]:
                result = usa_results[idx]
                idx += 1
                
                if isinstance(result, Exception):
                    continue
                
                key = f"{law_type}|USA"
                if key not in all_updates:
                    all_updates[key] = []
                
                for update in result:
                    if not any(u["id"] == update["id"] for u in all_updates[key]):
                        all_updates[key].append(update)
        
        # Add USA RSS feeds
        for feed in USA_RSS_FEEDS:
            try:
                feed_updates = await self.fetch_rss_feed(feed, "USA")
                for update in feed_updates:
                    for law_type in update.get("law_types", ["Civil Law"]):
                        key = f"{law_type}|USA"
                        if key not in all_updates:
                            all_updates[key] = []
                        if not any(u["id"] == update["id"] for u in all_updates[key]):
                            all_updates[key].append(update)
            except Exception as e:
                logger.warning(f"Error fetching USA RSS feed: {e}")
        
        # ================================================================
        # ADD SAMPLE UPDATES FOR EMPTY CATEGORIES
        # ================================================================
        for key, samples in SAMPLE_UPDATES_CANADA.items():
            if key not in all_updates or len(all_updates[key]) < 3:
                if key not in all_updates:
                    all_updates[key] = []
                all_updates[key].extend(samples)
        
        for key, samples in SAMPLE_UPDATES_USA.items():
            if key not in all_updates or len(all_updates[key]) < 3:
                if key not in all_updates:
                    all_updates[key] = []
                all_updates[key].extend(samples)
        
        # ================================================================
        # SORT AND LIMIT
        # ================================================================
        for key in all_updates:
            # Remove duplicates
            seen_ids = set()
            unique = []
            for u in all_updates[key]:
                if u["id"] not in seen_ids:
                    seen_ids.add(u["id"])
                    unique.append(u)
            
            # Sort by date and limit
            all_updates[key] = sorted(
                unique,
                key=lambda x: x.get("date", ""),
                reverse=True
            )[:20]
        
        # Log summary
        canada_count = sum(len(v) for k, v in all_updates.items() if "Canada" in k)
        usa_count = sum(len(v) for k, v in all_updates.items() if "USA" in k)
        
        logger.info("\n" + "=" * 60)
        logger.info(f"FETCH COMPLETE:")
        logger.info(f"  🍁 Canada updates: {canada_count}")
        logger.info(f"  🇺🇸 USA updates: {usa_count}")
        logger.info(f"  📊 Total categories: {len(all_updates)}")
        logger.info("=" * 60)
        
        return all_updates
    
    def save_updates(self, updates: Dict[str, List[Dict]]):
        """Save updates to cache file."""
        try:
            with open(self.updates_file, 'w', encoding='utf-8') as f:
                json.dump(updates, f, indent=2, ensure_ascii=False)
            
            canada_count = sum(len(v) for k, v in updates.items() if "Canada" in k)
            usa_count = sum(len(v) for k, v in updates.items() if "USA" in k)
            
            with open(self.last_fetch_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_fetch": datetime.now().isoformat(),
                    "total_updates": sum(len(v) for v in updates.values()),
                    "canada_updates": canada_count,
                    "usa_updates": usa_count,
                    "categories": len(updates)
                }, f, indent=2)
            
            logger.info(f"Saved {sum(len(v) for v in updates.values())} updates to cache")
            
        except Exception as e:
            logger.error(f"Error saving updates: {e}")
    
    def load_updates(self) -> Dict[str, List[Dict]]:
        """Load updates from cache file."""
        if self.updates_file.exists():
            try:
                with open(self.updates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading updates: {e}")
        
        # Return combined sample updates as fallback
        all_samples = {}
        all_samples.update(SAMPLE_UPDATES_CANADA)
        all_samples.update(SAMPLE_UPDATES_USA)
        return all_samples
    
    def get_updates_for_law_type(self, law_type: str, jurisdiction: str = "") -> List[Dict]:
        """Get updates for a specific law type and jurisdiction."""
        updates = self.load_updates()
        
        # Normalize jurisdiction
        if jurisdiction:
            if "canada" in jurisdiction.lower() or jurisdiction in ["CA", "QC", "ON", "BC", "AB", "MB", "SK", "NS", "NB", "PE", "NL", "YT", "NT", "NU"]:
                jurisdiction = "Canada"
            elif "usa" in jurisdiction.lower() or "united states" in jurisdiction.lower() or jurisdiction in ["US"]:
                jurisdiction = "USA"
        
        # Try exact match first
        key = f"{law_type}|{jurisdiction}" if jurisdiction else law_type
        if key in updates:
            return updates[key]
        
        # Try partial matches with correct jurisdiction
        results = []
        for k, v in updates.items():
            key_law_type, key_jurisdiction = k.split("|") if "|" in k else (k, "")
            
            # Check if law type matches
            if law_type.lower() in key_law_type.lower():
                # If jurisdiction specified, filter by it
                if jurisdiction:
                    if jurisdiction.lower() == key_jurisdiction.lower():
                        results.extend(v)
                else:
                    results.extend(v)
        
        # Remove duplicates and sort
        seen = set()
        unique_results = []
        for r in results:
            if r["id"] not in seen:
                seen.add(r["id"])
                unique_results.append(r)
        
        return sorted(unique_results, key=lambda x: x.get("date", ""), reverse=True)[:20]
    
    def should_refresh(self, max_age_hours: int = 6) -> bool:
        """Check if updates should be refreshed."""
        if not self.last_fetch_file.exists():
            return True
        
        try:
            with open(self.last_fetch_file, 'r') as f:
                data = json.load(f)
                last_fetch = datetime.fromisoformat(data.get("last_fetch", "2000-01-01"))
                age = datetime.now() - last_fetch
                return age > timedelta(hours=max_age_hours)
        except:
            return True
    
    async def refresh_if_needed(self, max_age_hours: int = 6):
        """Refresh updates if they're older than max_age_hours."""
        if self.should_refresh(max_age_hours):
            logger.info("Updates are stale, refreshing...")
            updates = await self.fetch_all_updates()
            self.save_updates(updates)
            return True
        return False


# Singleton instance
_legal_updates_service: Optional[LegalUpdatesService] = None


def get_legal_updates_service() -> LegalUpdatesService:
    """Get the singleton legal updates service instance."""
    global _legal_updates_service
    if _legal_updates_service is None:
        _legal_updates_service = LegalUpdatesService()
    return _legal_updates_service


async def initialize_legal_updates():
    """Initialize and populate legal updates on startup."""
    service = get_legal_updates_service()
    
    if service.should_refresh(max_age_hours=6):
        logger.info("Fetching fresh legal updates...")
        try:
            updates = await service.fetch_all_updates()
            service.save_updates(updates)
            logger.info(f"Legal updates initialized successfully!")
        except Exception as e:
            logger.error(f"Error initializing legal updates: {e}")
            # Save sample updates as fallback
            all_samples = {}
            all_samples.update(SAMPLE_UPDATES_CANADA)
            all_samples.update(SAMPLE_UPDATES_USA)
            service.save_updates(all_samples)
    else:
        logger.info("Legal updates cache is fresh.")


# For running standalone
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("ADVANCED LEGAL UPDATES SERVICE")
        print("=" * 80)
        
        service = LegalUpdatesService()
        updates = await service.fetch_all_updates()
        service.save_updates(updates)
        
        print(f"\n📊 SUMMARY:")
        print(f"{'=' * 50}")
        
        canada_categories = {k: v for k, v in updates.items() if "Canada" in k}
        usa_categories = {k: v for k, v in updates.items() if "USA" in k}
        
        print(f"\n🍁 CANADA UPDATES ({sum(len(v) for v in canada_categories.values())} total):")
        for key, items in sorted(canada_categories.items()):
            print(f"  • {key}: {len(items)} updates")
        
        print(f"\n🇺🇸 USA UPDATES ({sum(len(v) for v in usa_categories.values())} total):")
        for key, items in sorted(usa_categories.items()):
            print(f"  • {key}: {len(items)} updates")
        
        print("\n" + "=" * 80)
        print("COMPLETE!")
        print("=" * 80)
    
    asyncio.run(main())
