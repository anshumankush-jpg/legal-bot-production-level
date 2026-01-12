"""
Legal Data Sources Configuration
Manages sources for case law, statutes, and legal information
"""

# Official Legal Data Sources by Jurisdiction
LEGAL_DATA_SOURCES = {
    "Canada": {
        "Federal": {
            "sources": [
                {
                    "name": "CanLII (Canadian Legal Information Institute)",
                    "url": "https://www.canlii.org/en/",
                    "type": "case_law",
                    "api_available": True,
                    "free": True,
                    "description": "Primary source for Canadian case law and legislation"
                },
                {
                    "name": "Department of Justice Canada",
                    "url": "https://laws-lois.justice.gc.ca/",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "Official federal legislation"
                },
                {
                    "name": "Supreme Court of Canada",
                    "url": "https://scc-csc.ca/",
                    "type": "case_law",
                    "api_available": False,
                    "free": True,
                    "description": "Supreme Court decisions and judgments"
                },
                {
                    "name": "Immigration, Refugees and Citizenship Canada (IRCC)",
                    "url": "https://www.canada.ca/en/immigration-refugees-citizenship.html",
                    "type": "immigration",
                    "api_available": False,
                    "free": True,
                    "description": "Official federal immigration information and programs"
                },
                {
                    "name": "Immigration and Refugee Board of Canada (IRB)",
                    "url": "https://irb-cisr.gc.ca/",
                    "type": "immigration_tribunal",
                    "api_available": False,
                    "free": True,
                    "description": "Immigration and refugee decisions and guidelines"
                }
            ],
            "categories": ["Criminal Law", "Constitutional Law", "Tax Law", "Immigration Law"]
        },
        "Ontario": {
            "sources": [
                {
                    "name": "Ontario Court of Appeal",
                    "url": "https://www.ontariocourts.ca/coa/",
                    "type": "case_law",
                    "api_available": False,
                    "free": True,
                    "description": "Ontario Court of Appeal decisions"
                },
                {
                    "name": "Ontario Superior Court of Justice",
                    "url": "https://www.ontariocourts.ca/scj/",
                    "type": "case_law",
                    "api_available": False,
                    "free": True,
                    "description": "Superior Court decisions"
                },
                {
                    "name": "Ontario Regulations",
                    "url": "https://www.ontario.ca/laws",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "Provincial legislation and regulations"
                },
                {
                    "name": "Law Society of Ontario",
                    "url": "https://lso.ca/",
                    "type": "professional_resources",
                    "api_available": False,
                    "free": True,
                    "description": "Legal practice resources"
                },
                {
                    "name": "Ontario Immigrant Nominee Program (OINP)",
                    "url": "https://www.ontario.ca/page/ontario-immigrant-nominee-program-oinp",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "Ontario provincial immigration program"
                }
            ],
            "categories": ["Family Law", "Employment Law", "Real Estate Law", "Traffic Law", "Immigration Law"]
        },
        "Quebec": {
            "sources": [
                {
                    "name": "SOQUIJ (Société québécoise d'information juridique)",
                    "url": "https://soquij.qc.ca/",
                    "type": "case_law",
                    "api_available": False,
                    "free": False,
                    "description": "Quebec legal information"
                },
                {
                    "name": "Publications du Québec",
                    "url": "http://legisquebec.gouv.qc.ca/",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "Quebec legislation"
                },
                {
                    "name": "Quebec Immigrant Investor Program (QIIP)",
                    "url": "https://www.quebec.ca/en/immigration",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "Quebec immigration programs"
                },
                {
                    "name": "Ministère de l'Immigration, de la Francisation et de l'Intégration",
                    "url": "https://www.quebec.ca/en/immigration/immigrate-settle-quebec",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "Quebec immigration ministry"
                }
            ],
            "categories": ["Civil Law", "Family Law", "Labour Law", "Immigration Law"]
        },
        "British Columbia": {
            "sources": [
                {
                    "name": "BC Laws",
                    "url": "https://www.bclaws.gov.bc.ca/",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "BC provincial legislation"
                },
                {
                    "name": "BC Provincial Nominee Program (BC PNP)",
                    "url": "https://www.welcomebc.ca/Immigrate-to-B-C/BC-PNP-Immigration",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "British Columbia provincial immigration program"
                }
            ],
            "categories": ["Family Law", "Employment Law", "Real Estate Law", "Immigration Law"]
        },
        "Alberta": {
            "sources": [
                {
                    "name": "Alberta Queen's Printer",
                    "url": "https://www.qp.alberta.ca/",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "Alberta legislation"
                },
                {
                    "name": "Alberta Advantage Immigration Program (AAIP)",
                    "url": "https://www.alberta.ca/alberta-advantage-immigration-program.aspx",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "Alberta provincial immigration program"
                }
            ],
            "categories": ["Energy Law", "Family Law", "Employment Law", "Immigration Law"]
        },
        "Manitoba": {
            "sources": [
                {
                    "name": "Manitoba Laws",
                    "url": "https://web2.gov.mb.ca/laws/",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "Manitoba provincial legislation"
                },
                {
                    "name": "Manitoba Provincial Nominee Program (MPNP)",
                    "url": "https://immigratemanitoba.com/",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "Manitoba provincial immigration program"
                }
            ],
            "categories": ["Family Law", "Employment Law", "Immigration Law"]
        },
        "Saskatchewan": {
            "sources": [
                {
                    "name": "Saskatchewan Laws",
                    "url": "https://www.canlii.org/en/sk/laws/",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "Saskatchewan provincial legislation"
                },
                {
                    "name": "Saskatchewan Immigrant Nominee Program (SINP)",
                    "url": "https://www.saskatchewan.ca/residents/moving-to-saskatchewan/immigrating-to-saskatchewan/saskatchewan-immigrant-nominee-program",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "Saskatchewan provincial immigration program"
                }
            ],
            "categories": ["Family Law", "Employment Law", "Immigration Law"]
        },
        "Nova Scotia": {
            "sources": [
                {
                    "name": "Nova Scotia Laws",
                    "url": "https://nslegislature.ca/legislative-business/laws-and-regulations",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "Nova Scotia provincial legislation"
                },
                {
                    "name": "Nova Scotia Nominee Program (NSNP)",
                    "url": "https://novascotiaimmigration.com/",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "Nova Scotia provincial immigration program"
                }
            ],
            "categories": ["Family Law", "Employment Law", "Immigration Law"]
        },
        "New Brunswick": {
            "sources": [
                {
                    "name": "New Brunswick Laws",
                    "url": "https://www.canlii.org/en/nb/laws/",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "New Brunswick provincial legislation"
                },
                {
                    "name": "New Brunswick Provincial Nominee Program (NBPNP)",
                    "url": "https://www.welcomenb.ca/content/wel-bien/en/immigrating.html",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "New Brunswick provincial immigration program"
                }
            ],
            "categories": ["Family Law", "Employment Law", "Immigration Law"]
        },
        "Prince Edward Island": {
            "sources": [
                {
                    "name": "PEI Laws",
                    "url": "https://www.princeedwardisland.ca/en/legislation/all/all/a",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "PEI provincial legislation"
                },
                {
                    "name": "PEI Provincial Nominee Program (PEI PNP)",
                    "url": "https://www.princeedwardisland.ca/en/topic/office-immigration",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "Prince Edward Island provincial immigration program"
                }
            ],
            "categories": ["Family Law", "Employment Law", "Immigration Law"]
        },
        "Newfoundland and Labrador": {
            "sources": [
                {
                    "name": "Newfoundland and Labrador Laws",
                    "url": "https://www.assembly.nl.ca/legislation/",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "Newfoundland and Labrador provincial legislation"
                },
                {
                    "name": "Newfoundland and Labrador Provincial Nominee Program (NLPNP)",
                    "url": "https://www.gov.nl.ca/immigration/immigrating-to-newfoundland-and-labrador/",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "Newfoundland and Labrador provincial immigration program"
                }
            ],
            "categories": ["Family Law", "Employment Law", "Immigration Law"]
        },
        "Yukon": {
            "sources": [
                {
                    "name": "Yukon Laws",
                    "url": "https://laws.yukon.ca/",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "Yukon territorial legislation"
                },
                {
                    "name": "Yukon Nominee Program (YNP)",
                    "url": "https://yukon.ca/en/doing-business/immigrate-yukon",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "Yukon territorial immigration program"
                }
            ],
            "categories": ["Family Law", "Employment Law", "Immigration Law"]
        },
        "Northwest Territories": {
            "sources": [
                {
                    "name": "Northwest Territories Laws",
                    "url": "https://www.justice.gov.nt.ca/en/legislation/",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "Northwest Territories territorial legislation"
                },
                {
                    "name": "Northwest Territories Nominee Program (NTNP)",
                    "url": "https://www.immigratenwt.ca/",
                    "type": "immigration_provincial",
                    "api_available": False,
                    "free": True,
                    "description": "Northwest Territories territorial immigration program"
                }
            ],
            "categories": ["Family Law", "Employment Law", "Immigration Law"]
        }
    },
    "USA": {
        "Federal": {
            "sources": [
                {
                    "name": "PACER (Public Access to Court Electronic Records)",
                    "url": "https://pacer.uscourts.gov/",
                    "type": "case_law",
                    "api_available": True,
                    "free": False,
                    "description": "Federal court documents"
                },
                {
                    "name": "Supreme Court of the United States",
                    "url": "https://www.supremecourt.gov/",
                    "type": "case_law",
                    "api_available": False,
                    "free": True,
                    "description": "Supreme Court opinions"
                },
                {
                    "name": "Cornell Legal Information Institute",
                    "url": "https://www.law.cornell.edu/",
                    "type": "legislation",
                    "api_available": False,
                    "free": True,
                    "description": "Federal and state law"
                },
                {
                    "name": "GovInfo",
                    "url": "https://www.govinfo.gov/",
                    "type": "legislation",
                    "api_available": True,
                    "free": True,
                    "description": "Federal government information"
                }
            ],
            "categories": ["Criminal Law", "Constitutional Law", "Tax Law", "Immigration Law"]
        }
    }
}

# Law Type to Data Source Mapping
LAW_TYPE_SOURCE_MAPPING = {
    "Criminal Law": {
        "primary_sources": ["CanLII", "Supreme Court of Canada", "Department of Justice Canada"],
        "case_types": ["criminal", "charter"],
        "keywords": ["criminal code", "offence", "sentence", "prosecution"]
    },
    "Family Law": {
        "primary_sources": ["CanLII", "Ontario Superior Court of Justice"],
        "case_types": ["family", "divorce", "custody"],
        "keywords": ["family law act", "divorce", "custody", "support", "property division"]
    },
    "Employment Law": {
        "primary_sources": ["CanLII", "Ontario Court of Appeal"],
        "case_types": ["employment", "labour"],
        "keywords": ["employment standards", "wrongful dismissal", "human rights"]
    },
    "Traffic Law": {
        "primary_sources": ["Ontario Regulations", "CanLII"],
        "case_types": ["provincial offences", "traffic"],
        "keywords": ["highway traffic act", "speeding", "careless driving"]
    },
    "Real Estate Law": {
        "primary_sources": ["CanLII", "Ontario Regulations"],
        "case_types": ["real estate", "property"],
        "keywords": ["land transfer", "lease", "title", "conveyance"]
    },
    "Business Law": {
        "primary_sources": ["CanLII", "Supreme Court of Canada"],
        "case_types": ["commercial", "corporate"],
        "keywords": ["business corporations act", "contract", "partnership"]
    },
    "Tax Law": {
        "primary_sources": ["Department of Justice Canada", "CanLII"],
        "case_types": ["tax"],
        "keywords": ["income tax act", "gst", "hst", "assessment"]
    },
    "Wills, Estates, and Trusts": {
        "primary_sources": ["CanLII", "Ontario Superior Court of Justice"],
        "case_types": ["estate", "probate"],
        "keywords": ["will", "estate", "probate", "executor", "beneficiary"]
    },
    "Immigration Law": {
        "primary_sources": ["IRCC", "IRB", "CanLII"],
        "case_types": ["immigration", "refugee", "citizenship"],
        "keywords": ["immigration", "permanent residence", "work permit", "study permit", "refugee", "citizenship", "visa", "provincial nominee"]
    }
}

def get_sources_for_jurisdiction(country, province=None):
    """Get legal data sources for a specific jurisdiction"""
    sources = []
    
    if country in LEGAL_DATA_SOURCES:
        # Add federal sources
        if "Federal" in LEGAL_DATA_SOURCES[country]:
            sources.extend(LEGAL_DATA_SOURCES[country]["Federal"]["sources"])
        
        # Add provincial/state sources if available
        if province and province in LEGAL_DATA_SOURCES[country]:
            sources.extend(LEGAL_DATA_SOURCES[country][province]["sources"])
    
    return sources

def get_sources_for_law_type(law_type, country, province=None):
    """Get specific sources for a law type and jurisdiction"""
    all_sources = get_sources_for_jurisdiction(country, province)
    
    if law_type not in LAW_TYPE_SOURCE_MAPPING:
        return all_sources
    
    mapping = LAW_TYPE_SOURCE_MAPPING[law_type]
    primary_source_names = mapping["primary_sources"]
    
    # Filter sources to prioritize primary sources
    prioritized = [s for s in all_sources if s["name"] in primary_source_names]
    other = [s for s in all_sources if s["name"] not in primary_source_names]
    
    return prioritized + other

def get_search_keywords(law_type):
    """Get search keywords for a specific law type"""
    if law_type in LAW_TYPE_SOURCE_MAPPING:
        return LAW_TYPE_SOURCE_MAPPING[law_type]["keywords"]
    return []
