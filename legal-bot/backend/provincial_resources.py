"""
Provincial Government Resources Configuration
Dynamic resources for all Canadian provinces and territories
"""

PROVINCIAL_RESOURCES = {
    "Traffic Law": {
        "ON": [  # Ontario
            {
                "title": "Highway Traffic Act (Ontario)",
                "url": "https://www.ontario.ca/laws/statute/90h08",
                "source": "Ontario Government"
            },
            {
                "title": "Ontario Traffic Tickets",
                "url": "https://www.ontario.ca/page/pay-your-traffic-ticket",
                "source": "Ontario Government"
            },
            {
                "title": "Driver Licensing and Suspensions",
                "url": "https://www.ontario.ca/page/your-drivers-licence",
                "source": "Ontario Ministry of Transportation"
            }
        ],
        "QC": [  # Quebec
            {
                "title": "Code de la sécurité routière (Highway Safety Code)",
                "url": "https://www.legisquebec.gouv.qc.ca/en/document/cs/C-24.2",
                "source": "Gouvernement du Québec"
            },
            {
                "title": "SAAQ - Traffic Violations and Demerit Points",
                "url": "https://saaq.gouv.qc.ca/en/traffic-violations-and-demerit-points/",
                "source": "Société de l'assurance automobile du Québec"
            },
            {
                "title": "Contesting a Traffic Ticket in Quebec",
                "url": "https://www.quebec.ca/en/transport/driving-and-road-safety/traffic-violations/contesting-ticket",
                "source": "Gouvernement du Québec"
            }
        ],
        "BC": [  # British Columbia
            {
                "title": "Motor Vehicle Act (BC)",
                "url": "https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96318_00",
                "source": "BC Government"
            },
            {
                "title": "ICBC - Traffic Tickets and Violations",
                "url": "https://www.icbc.com/driver-licensing/tickets",
                "source": "Insurance Corporation of British Columbia"
            },
            {
                "title": "Disputing a Traffic Ticket (BC)",
                "url": "https://www2.gov.bc.ca/gov/content/justice/courthouse-services/fines-payments/dispute-ticket",
                "source": "BC Government"
            }
        ],
        "AB": [  # Alberta
            {
                "title": "Traffic Safety Act (Alberta)",
                "url": "https://www.qp.alberta.ca/documents/Acts/t06.pdf",
                "source": "Alberta Government"
            },
            {
                "title": "Alberta Traffic Tickets and Fines",
                "url": "https://www.alberta.ca/traffic-tickets-fines.aspx",
                "source": "Alberta Government"
            },
            {
                "title": "Demerit Points System (Alberta)",
                "url": "https://www.alberta.ca/demerit-points-program.aspx",
                "source": "Alberta Transportation"
            }
        ],
        "MB": [  # Manitoba
            {
                "title": "Highway Traffic Act (Manitoba)",
                "url": "https://web2.gov.mb.ca/laws/statutes/ccsm/h060e.php",
                "source": "Manitoba Government"
            },
            {
                "title": "MPI - Traffic Violations and Demerits",
                "url": "https://www.mpi.mb.ca/Pages/traffic-violations.aspx",
                "source": "Manitoba Public Insurance"
            },
            {
                "title": "Disputing Traffic Tickets (Manitoba)",
                "url": "https://www.gov.mb.ca/justice/crown/prosecution/pubs/traffic.html",
                "source": "Manitoba Justice"
            }
        ],
        "SK": [  # Saskatchewan
            {
                "title": "Traffic Safety Act (Saskatchewan)",
                "url": "https://www.saskatchewan.ca/residents/driving-and-transportation/traffic-safety",
                "source": "Saskatchewan Government"
            },
            {
                "title": "SGI - Traffic Tickets and Penalties",
                "url": "https://www.sgi.sk.ca/traffic-tickets",
                "source": "Saskatchewan Government Insurance"
            },
            {
                "title": "Demerit Points (Saskatchewan)",
                "url": "https://www.sgi.sk.ca/demerit-points",
                "source": "SGI"
            }
        ],
        "NS": [  # Nova Scotia
            {
                "title": "Motor Vehicle Act (Nova Scotia)",
                "url": "https://nslegislature.ca/sites/default/files/legc/statutes/motor%20vehicle.pdf",
                "source": "Nova Scotia Government"
            },
            {
                "title": "Traffic Tickets and Fines (NS)",
                "url": "https://novascotia.ca/sns/paal/rmv/paal269.asp",
                "source": "Service Nova Scotia"
            },
            {
                "title": "Demerit Points System (NS)",
                "url": "https://novascotia.ca/sns/paal/rmv/paal271.asp",
                "source": "Service Nova Scotia"
            }
        ],
        "NB": [  # New Brunswick
            {
                "title": "Motor Vehicle Act (New Brunswick)",
                "url": "https://laws.gnb.ca/en/showdoc/cs/M-17",
                "source": "New Brunswick Government"
            },
            {
                "title": "Traffic Violations and Penalties (NB)",
                "url": "https://www2.gnb.ca/content/gnb/en/services/services_renderer.201418.Traffic_Violations_and_Penalties.html",
                "source": "Service New Brunswick"
            },
            {
                "title": "Point Demerit System (NB)",
                "url": "https://www2.gnb.ca/content/gnb/en/departments/public-safety/drivers_vehicles/content/drivers_licences/content/point_demerit_system.html",
                "source": "New Brunswick Public Safety"
            }
        ],
        "PE": [  # Prince Edward Island
            {
                "title": "Highway Traffic Act (PEI)",
                "url": "https://www.princeedwardisland.ca/en/legislation/highway-traffic-act",
                "source": "PEI Government"
            },
            {
                "title": "Traffic Violations and Fines (PEI)",
                "url": "https://www.princeedwardisland.ca/en/information/justice-and-public-safety/traffic-violations",
                "source": "PEI Justice and Public Safety"
            },
            {
                "title": "Driver's Licence Points (PEI)",
                "url": "https://www.princeedwardisland.ca/en/information/transportation-and-infrastructure/drivers-licence-points",
                "source": "PEI Transportation"
            }
        ],
        "NL": [  # Newfoundland and Labrador
            {
                "title": "Highway Traffic Act (NL)",
                "url": "https://www.assembly.nl.ca/Legislation/sr/statutes/h03.htm",
                "source": "Newfoundland and Labrador Government"
            },
            {
                "title": "Traffic Tickets and Fines (NL)",
                "url": "https://www.gov.nl.ca/dgsnl/drivers/tickets-fines/",
                "source": "Service NL"
            },
            {
                "title": "Demerit Points System (NL)",
                "url": "https://www.gov.nl.ca/dgsnl/drivers/demerit-points/",
                "source": "Service NL"
            }
        ],
        "YT": [  # Yukon
            {
                "title": "Motor Vehicles Act (Yukon)",
                "url": "https://laws.yukon.ca/cms/images/LEGISLATION/PRINCIPAL/2002/2002-0153/2002-0153.pdf",
                "source": "Yukon Government"
            },
            {
                "title": "Traffic Tickets and Violations (YT)",
                "url": "https://yukon.ca/en/driving-and-transportation/traffic-tickets",
                "source": "Yukon Government"
            },
            {
                "title": "Driver's Licence Points (YT)",
                "url": "https://yukon.ca/en/driving-and-transportation/drivers-licences/demerit-points",
                "source": "Yukon Transportation"
            }
        ],
        "NT": [  # Northwest Territories
            {
                "title": "Motor Vehicles Act (NWT)",
                "url": "https://www.justice.gov.nt.ca/en/files/legislation/motor-vehicles/motor-vehicles.a.pdf",
                "source": "NWT Government"
            },
            {
                "title": "Traffic Violations (NWT)",
                "url": "https://www.inf.gov.nt.ca/en/services/traffic-violations",
                "source": "NWT Infrastructure"
            },
            {
                "title": "Demerit Points (NWT)",
                "url": "https://www.inf.gov.nt.ca/en/services/demerit-points",
                "source": "NWT Infrastructure"
            }
        ],
        "NU": [  # Nunavut
            {
                "title": "Motor Vehicles Act (Nunavut)",
                "url": "https://www.nunavutlegislation.ca/en/consolidated-law/motor-vehicles-act",
                "source": "Nunavut Government"
            },
            {
                "title": "Traffic Safety (Nunavut)",
                "url": "https://www.gov.nu.ca/economic-development-and-transportation/information/traffic-safety",
                "source": "Nunavut Transportation"
            },
            {
                "title": "Driver Licensing (Nunavut)",
                "url": "https://www.gov.nu.ca/economic-development-and-transportation/information/drivers-licences",
                "source": "Nunavut Government"
            }
        ]
    },
    "Criminal Law": {
        "ON": [
            {
                "title": "Criminal Code of Canada",
                "url": "https://laws-lois.justice.gc.ca/eng/acts/c-46/",
                "source": "Department of Justice Canada"
            },
            {
                "title": "Legal Aid Ontario - Criminal",
                "url": "https://www.legalaid.on.ca/services/criminal-law/",
                "source": "Legal Aid Ontario"
            },
            {
                "title": "Ontario Court of Justice - Criminal",
                "url": "https://www.ontariocourts.ca/ocj/criminal-matters/",
                "source": "Ontario Courts"
            }
        ],
        "QC": [
            {
                "title": "Criminal Code of Canada",
                "url": "https://laws-lois.justice.gc.ca/eng/acts/c-46/",
                "source": "Department of Justice Canada"
            },
            {
                "title": "Commission des services juridiques (Legal Aid Quebec)",
                "url": "https://www.csj.qc.ca/commission-des-services-juridiques/en/Pages/home.aspx",
                "source": "Quebec Legal Aid"
            },
            {
                "title": "Court of Quebec - Criminal Division",
                "url": "https://www.tribunaux.qc.ca/c-quebec/index-a.html",
                "source": "Quebec Courts"
            }
        ],
        "BC": [
            {
                "title": "Criminal Code of Canada",
                "url": "https://laws-lois.justice.gc.ca/eng/acts/c-46/",
                "source": "Department of Justice Canada"
            },
            {
                "title": "Legal Aid BC - Criminal",
                "url": "https://legalaid.bc.ca/criminal",
                "source": "Legal Aid BC"
            },
            {
                "title": "Provincial Court of BC - Criminal",
                "url": "https://www.provincialcourt.bc.ca/types-of-cases/criminal-cases",
                "source": "BC Provincial Court"
            }
        ],
        "AB": [
            {
                "title": "Criminal Code of Canada",
                "url": "https://laws-lois.justice.gc.ca/eng/acts/c-46/",
                "source": "Department of Justice Canada"
            },
            {
                "title": "Legal Aid Alberta - Criminal",
                "url": "https://www.legalaid.ab.ca/services/criminal-law/",
                "source": "Legal Aid Alberta"
            },
            {
                "title": "Alberta Courts - Criminal",
                "url": "https://albertacourts.ca/pc/areas-of-law/criminal",
                "source": "Alberta Courts"
            }
        ]
    },
    "Immigration Law": {
        "Federal": [
            {
                "title": "Immigration, Refugees and Citizenship Canada",
                "url": "https://www.canada.ca/en/immigration-refugees-citizenship.html",
                "source": "IRCC"
            },
            {
                "title": "Immigration and Refugee Board",
                "url": "https://irb-cisr.gc.ca/en/Pages/index.aspx",
                "source": "IRB Canada"
            },
            {
                "title": "Express Entry System",
                "url": "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html",
                "source": "IRCC"
            }
        ],
        "ON": [
            {
                "title": "Ontario Immigrant Nominee Program",
                "url": "https://www.ontario.ca/page/ontario-immigrant-nominee-program-oinp",
                "source": "Ontario Government"
            },
            {
                "title": "Settlement Services in Ontario",
                "url": "https://www.ontario.ca/page/settle-ontario",
                "source": "Ontario Government"
            }
        ],
        "QC": [
            {
                "title": "Quebec Immigration Programs",
                "url": "https://www.quebec.ca/en/immigration",
                "source": "Gouvernement du Québec"
            },
            {
                "title": "Ministère de l'Immigration (MIFI)",
                "url": "https://www.immigration-quebec.gouv.qc.ca/en/",
                "source": "Quebec Immigration"
            }
        ],
        "BC": [
            {
                "title": "BC Provincial Nominee Program",
                "url": "https://www.welcomebc.ca/Immigrate-to-B-C/BC-PNP",
                "source": "WelcomeBC"
            },
            {
                "title": "Settlement Services in BC",
                "url": "https://www.welcomebc.ca/",
                "source": "WelcomeBC"
            }
        ],
        "AB": [
            {
                "title": "Alberta Immigrant Nominee Program",
                "url": "https://www.alberta.ca/ainp.aspx",
                "source": "Alberta Government"
            },
            {
                "title": "Settlement Services Alberta",
                "url": "https://www.alberta.ca/immigration-settlement-services.aspx",
                "source": "Alberta Government"
            }
        ]
    },
    "Business Law": {
        "Federal": [
            {
                "title": "Canada Business Registry",
                "url": "https://www.ic.gc.ca/eic/site/cd-dgc.nsf/eng/home",
                "source": "Innovation, Science and Economic Development Canada"
            },
            {
                "title": "Canada Revenue Agency - Business",
                "url": "https://www.canada.ca/en/revenue-agency/services/tax/businesses.html",
                "source": "CRA"
            }
        ],
        "ON": [
            {
                "title": "Ontario Business Registry",
                "url": "https://www.ontario.ca/page/business-registry",
                "source": "Ontario Government"
            },
            {
                "title": "BizPal Ontario",
                "url": "https://www.ontario.ca/page/bizpal-ontario",
                "source": "Ontario Government"
            }
        ],
        "QC": [
            {
                "title": "Registraire des entreprises du Québec",
                "url": "https://www.registreentreprises.gouv.qc.ca/en/",
                "source": "Gouvernement du Québec"
            },
            {
                "title": "Revenu Québec - Entreprises",
                "url": "https://www.revenuquebec.ca/en/businesses/",
                "source": "Revenu Québec"
            }
        ],
        "BC": [
            {
                "title": "BC Registry Services",
                "url": "https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/permits-licences/businesses-incorporated-companies",
                "source": "BC Government"
            },
            {
                "title": "Small Business BC",
                "url": "https://smallbusinessbc.ca/",
                "source": "Small Business BC"
            }
        ],
        "AB": [
            {
                "title": "Alberta Corporate Registry",
                "url": "https://www.alberta.ca/corporate-registry.aspx",
                "source": "Alberta Government"
            },
            {
                "title": "Business Link Alberta",
                "url": "https://www.alberta.ca/business-link.aspx",
                "source": "Alberta Government"
            }
        ]
    },
    "Tax Law": {
        "Federal": [
            {
                "title": "Canada Revenue Agency",
                "url": "https://www.canada.ca/en/revenue-agency.html",
                "source": "CRA"
            },
            {
                "title": "Tax Court of Canada",
                "url": "https://www.tcc-cci.gc.ca/en/Pages/default.aspx",
                "source": "Tax Court"
            }
        ],
        "ON": [
            {
                "title": "Ontario Ministry of Finance - Tax",
                "url": "https://www.fin.gov.on.ca/en/tax/",
                "source": "Ontario Ministry of Finance"
            }
        ],
        "QC": [
            {
                "title": "Revenu Québec",
                "url": "https://www.revenuquebec.ca/en/",
                "source": "Revenu Québec"
            }
        ],
        "BC": [
            {
                "title": "BC Ministry of Finance - Tax",
                "url": "https://www2.gov.bc.ca/gov/content/taxes",
                "source": "BC Ministry of Finance"
            }
        ],
        "AB": [
            {
                "title": "Alberta Tax and Revenue Administration",
                "url": "https://www.alberta.ca/tax-revenue-administration.aspx",
                "source": "Alberta Treasury Board and Finance"
            }
        ]
    }
}

# Province name mapping
PROVINCE_NAMES = {
    "ON": "Ontario",
    "QC": "Quebec",
    "BC": "British Columbia",
    "AB": "Alberta",
    "MB": "Manitoba",
    "SK": "Saskatchewan",
    "NS": "Nova Scotia",
    "NB": "New Brunswick",
    "PE": "Prince Edward Island",
    "NL": "Newfoundland and Labrador",
    "YT": "Yukon",
    "NT": "Northwest Territories",
    "NU": "Nunavut"
}

def get_provincial_resources(law_type: str, province_code: str = None):
    """
    Get government resources for a specific law type and province
    
    Args:
        law_type: Type of law (e.g., "Traffic Law", "Criminal Law")
        province_code: Two-letter province code (e.g., "ON", "QC")
    
    Returns:
        List of resource dictionaries
    """
    if law_type not in PROVINCIAL_RESOURCES:
        return []
    
    resources = []
    
    # Add federal resources if available
    if "Federal" in PROVINCIAL_RESOURCES[law_type]:
        resources.extend(PROVINCIAL_RESOURCES[law_type]["Federal"])
    
    # Add province-specific resources
    if province_code and province_code in PROVINCIAL_RESOURCES[law_type]:
        resources.extend(PROVINCIAL_RESOURCES[law_type][province_code])
    
    return resources

def get_all_provinces():
    """Get list of all provinces with their codes"""
    return [{"code": code, "name": name} for code, name in PROVINCE_NAMES.items()]
