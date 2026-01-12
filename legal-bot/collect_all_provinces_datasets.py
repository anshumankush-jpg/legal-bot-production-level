"""
Comprehensive Provincial Legal Data Collector
Collects and organizes legal datasets for all Canadian provinces and territories
"""

import os
import json
from pathlib import Path
from datetime import datetime

# Provincial data sources and information
PROVINCIAL_DATA = {
    "ON": {
        "name": "Ontario",
        "traffic_act": "Highway Traffic Act",
        "traffic_act_url": "https://www.ontario.ca/laws/statute/90h08",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "Ontario Court of Justice - Criminal Division",
            "Legal Aid Ontario - Criminal Services"
        ],
        "immigration_programs": [
            "Ontario Immigrant Nominee Program (OINP)",
            "Ontario Settlement Services"
        ],
        "business_resources": [
            "Ontario Business Registry",
            "BizPal Ontario",
            "Ontario Ministry of Finance - Tax"
        ]
    },
    "QC": {
        "name": "Quebec",
        "traffic_act": "Code de la sécurité routière",
        "traffic_act_url": "https://www.legisquebec.gouv.qc.ca/en/document/cs/C-24.2",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "Court of Quebec - Criminal Division",
            "Commission des services juridiques (Legal Aid Quebec)"
        ],
        "immigration_programs": [
            "Quebec Immigration Programs",
            "Ministère de l'Immigration, de la Francisation et de l'Intégration (MIFI)"
        ],
        "business_resources": [
            "Registraire des entreprises du Québec",
            "Revenu Québec - Entreprises"
        ]
    },
    "BC": {
        "name": "British Columbia",
        "traffic_act": "Motor Vehicle Act",
        "traffic_act_url": "https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/96318_00",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "Provincial Court of BC - Criminal",
            "Legal Aid BC - Criminal Services"
        ],
        "immigration_programs": [
            "BC Provincial Nominee Program",
            "WelcomeBC Settlement Services"
        ],
        "business_resources": [
            "BC Registry Services",
            "Small Business BC",
            "BC Ministry of Finance - Tax"
        ]
    },
    "AB": {
        "name": "Alberta",
        "traffic_act": "Traffic Safety Act",
        "traffic_act_url": "https://www.qp.alberta.ca/documents/Acts/t06.pdf",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "Alberta Courts - Criminal Division",
            "Legal Aid Alberta - Criminal Services"
        ],
        "immigration_programs": [
            "Alberta Immigrant Nominee Program (AINP)",
            "Alberta Settlement Services"
        ],
        "business_resources": [
            "Alberta Corporate Registry",
            "Business Link Alberta",
            "Alberta Tax and Revenue Administration"
        ]
    },
    "MB": {
        "name": "Manitoba",
        "traffic_act": "Highway Traffic Act",
        "traffic_act_url": "https://web2.gov.mb.ca/laws/statutes/ccsm/h060e.php",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "Manitoba Provincial Court - Criminal",
            "Legal Aid Manitoba - Criminal Services"
        ],
        "immigration_programs": [
            "Manitoba Provincial Nominee Program",
            "Manitoba Settlement Services"
        ],
        "business_resources": [
            "Manitoba Companies Office",
            "Manitoba Finance - Tax",
            "Manitoba Business Services"
        ]
    },
    "SK": {
        "name": "Saskatchewan",
        "traffic_act": "Traffic Safety Act",
        "traffic_act_url": "https://www.saskatchewan.ca/residents/driving-and-transportation/traffic-safety",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "Saskatchewan Provincial Court - Criminal",
            "Legal Aid Saskatchewan - Criminal Services"
        ],
        "immigration_programs": [
            "Saskatchewan Immigrant Nominee Program (SINP)",
            "Saskatchewan Settlement Services"
        ],
        "business_resources": [
            "Saskatchewan Corporate Registry",
            "Saskatchewan Business Services",
            "Saskatchewan Revenue - Tax"
        ]
    },
    "NS": {
        "name": "Nova Scotia",
        "traffic_act": "Motor Vehicle Act",
        "traffic_act_url": "https://nslegislature.ca/sites/default/files/legc/statutes/motor%20vehicle.pdf",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "Nova Scotia Provincial Court - Criminal",
            "Nova Scotia Legal Aid - Criminal Services"
        ],
        "immigration_programs": [
            "Nova Scotia Nominee Program",
            "Nova Scotia Settlement Services"
        ],
        "business_resources": [
            "Nova Scotia Registry of Joint Stock Companies",
            "Service Nova Scotia - Business",
            "Nova Scotia Finance - Tax"
        ]
    },
    "NB": {
        "name": "New Brunswick",
        "traffic_act": "Motor Vehicle Act",
        "traffic_act_url": "https://laws.gnb.ca/en/showdoc/cs/M-17",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "New Brunswick Provincial Court - Criminal",
            "New Brunswick Legal Aid - Criminal Services"
        ],
        "immigration_programs": [
            "New Brunswick Provincial Nominee Program",
            "New Brunswick Settlement Services"
        ],
        "business_resources": [
            "Service New Brunswick - Corporate Registry",
            "New Brunswick Business Services",
            "New Brunswick Finance - Tax"
        ]
    },
    "PE": {
        "name": "Prince Edward Island",
        "traffic_act": "Highway Traffic Act",
        "traffic_act_url": "https://www.princeedwardisland.ca/en/legislation/highway-traffic-act",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "PEI Provincial Court - Criminal",
            "PEI Legal Aid - Criminal Services"
        ],
        "immigration_programs": [
            "PEI Provincial Nominee Program",
            "PEI Settlement Services"
        ],
        "business_resources": [
            "PEI Corporate Registry",
            "PEI Business Services",
            "PEI Finance - Tax"
        ]
    },
    "NL": {
        "name": "Newfoundland and Labrador",
        "traffic_act": "Highway Traffic Act",
        "traffic_act_url": "https://www.assembly.nl.ca/Legislation/sr/statutes/h03.htm",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "NL Provincial Court - Criminal",
            "NL Legal Aid - Criminal Services"
        ],
        "immigration_programs": [
            "Newfoundland and Labrador Provincial Nominee Program",
            "NL Settlement Services"
        ],
        "business_resources": [
            "NL Registry of Companies",
            "Service NL - Business",
            "NL Finance - Tax"
        ]
    },
    "YT": {
        "name": "Yukon",
        "traffic_act": "Motor Vehicles Act",
        "traffic_act_url": "https://laws.yukon.ca/cms/images/LEGISLATION/PRINCIPAL/2002/2002-0153/2002-0153.pdf",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "Yukon Territorial Court - Criminal",
            "Yukon Legal Services Society"
        ],
        "immigration_programs": [
            "Yukon Nominee Program",
            "Yukon Settlement Services"
        ],
        "business_resources": [
            "Yukon Corporate Affairs",
            "Yukon Business Services",
            "Yukon Finance - Tax"
        ]
    },
    "NT": {
        "name": "Northwest Territories",
        "traffic_act": "Motor Vehicles Act",
        "traffic_act_url": "https://www.justice.gov.nt.ca/en/files/legislation/motor-vehicles/motor-vehicles.a.pdf",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "NWT Territorial Court - Criminal",
            "NWT Legal Aid"
        ],
        "immigration_programs": [
            "NWT Nominee Program",
            "NWT Settlement Services"
        ],
        "business_resources": [
            "NWT Corporate Registry",
            "NWT Business Services",
            "NWT Finance - Tax"
        ]
    },
    "NU": {
        "name": "Nunavut",
        "traffic_act": "Motor Vehicles Act",
        "traffic_act_url": "https://www.nunavutlegislation.ca/en/consolidated-law/motor-vehicles-act",
        "criminal_resources": [
            "Criminal Code of Canada (Federal)",
            "Nunavut Court of Justice - Criminal",
            "Nunavut Legal Services Board"
        ],
        "immigration_programs": [
            "Nunavut Nominee Program",
            "Nunavut Settlement Services"
        ],
        "business_resources": [
            "Nunavut Corporate Registry",
            "Nunavut Business Services",
            "Nunavut Finance - Tax"
        ]
    }
}

# Common legal categories and their descriptions
LEGAL_CATEGORIES = {
    "Traffic Law": {
        "description": "Provincial traffic violations, tickets, and road safety regulations",
        "common_topics": [
            "Speeding violations",
            "Careless/dangerous driving",
            "Distracted driving",
            "Impaired driving (DUI/DWI)",
            "License suspensions",
            "Demerit points",
            "Traffic ticket disputes"
        ]
    },
    "Criminal Law": {
        "description": "Federal criminal offenses under the Criminal Code of Canada",
        "common_topics": [
            "Theft and property crimes",
            "Assault and violent crimes",
            "Fraud and financial crimes",
            "Drug offenses",
            "Criminal procedure and rights",
            "Bail and sentencing",
            "Criminal appeals"
        ]
    },
    "Immigration Law": {
        "description": "Immigration programs, visas, and citizenship matters",
        "common_topics": [
            "Provincial Nominee Programs",
            "Work permits",
            "Study permits",
            "Permanent residence",
            "Citizenship applications",
            "Refugee claims",
            "Immigration appeals"
        ]
    },
    "Business Law": {
        "description": "Business formation, operations, and compliance",
        "common_topics": [
            "Business incorporation",
            "Corporate governance",
            "Business contracts",
            "Intellectual property",
            "Business tax compliance",
            "Regulatory compliance",
            "Business licensing"
        ]
    },
    "Tax Law": {
        "description": "Federal and provincial tax matters",
        "common_topics": [
            "Income tax",
            "Corporate tax",
            "GST/HST/PST",
            "Tax audits and appeals",
            "Tax planning",
            "CRA disputes",
            "Provincial tax matters"
        ]
    }
}

def create_provincial_dataset():
    """Create comprehensive dataset for all provinces"""
    
    output_dir = Path("provincial_legal_datasets")
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("COMPREHENSIVE PROVINCIAL LEGAL DATA COLLECTOR")
    print("=" * 80)
    print(f"\nCreating datasets for all {len(PROVINCIAL_DATA)} Canadian provinces/territories\n")
    
    # Create master dataset
    master_dataset = {
        "created": datetime.now().isoformat(),
        "total_provinces": len(PROVINCIAL_DATA),
        "provinces": {},
        "legal_categories": LEGAL_CATEGORIES
    }
    
    # Process each province
    for province_code, province_info in PROVINCIAL_DATA.items():
        print(f"\n{'='*60}")
        print(f"Processing: {province_info['name']} ({province_code})")
        print(f"{'='*60}")
        
        province_dataset = {
            "code": province_code,
            "name": province_info["name"],
            "legal_resources": {}
        }
        
        # Traffic Law
        print(f"  [+] Traffic Law: {province_info['traffic_act']}")
        province_dataset["legal_resources"]["Traffic Law"] = {
            "primary_act": province_info["traffic_act"],
            "act_url": province_info["traffic_act_url"],
            "topics": LEGAL_CATEGORIES["Traffic Law"]["common_topics"]
        }
        
        # Criminal Law
        print(f"  [+] Criminal Law: {len(province_info['criminal_resources'])} resources")
        province_dataset["legal_resources"]["Criminal Law"] = {
            "resources": province_info["criminal_resources"],
            "topics": LEGAL_CATEGORIES["Criminal Law"]["common_topics"]
        }
        
        # Immigration Law
        print(f"  [+] Immigration Law: {len(province_info['immigration_programs'])} programs")
        province_dataset["legal_resources"]["Immigration Law"] = {
            "programs": province_info["immigration_programs"],
            "topics": LEGAL_CATEGORIES["Immigration Law"]["common_topics"]
        }
        
        # Business Law
        print(f"  [+] Business Law: {len(province_info['business_resources'])} resources")
        province_dataset["legal_resources"]["Business Law"] = {
            "resources": province_info["business_resources"],
            "topics": LEGAL_CATEGORIES["Business Law"]["common_topics"]
        }
        
        # Tax Law
        print(f"  [+] Tax Law: Provincial and federal resources")
        province_dataset["legal_resources"]["Tax Law"] = {
            "resources": ["Canada Revenue Agency (Federal)", "Provincial Tax Authority"],
            "topics": LEGAL_CATEGORIES["Tax Law"]["common_topics"]
        }
        
        # Save individual province dataset
        province_file = output_dir / f"{province_code}_legal_dataset.json"
        with open(province_file, 'w', encoding='utf-8') as f:
            json.dump(province_dataset, f, indent=2, ensure_ascii=False)
        print(f"  [SAVED] {province_file}")
        
        # Add to master dataset
        master_dataset["provinces"][province_code] = province_dataset
    
    # Save master dataset
    master_file = output_dir / "master_provincial_dataset.json"
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(master_dataset, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print("[SUCCESS] DATASET CREATION COMPLETE")
    print(f"{'='*80}")
    print(f"\n[SUMMARY]")
    print(f"  - Total Provinces/Territories: {len(PROVINCIAL_DATA)}")
    print(f"  - Legal Categories per Province: {len(LEGAL_CATEGORIES)}")
    print(f"  - Master Dataset: {master_file}")
    print(f"  - Individual Datasets: {output_dir}/")
    print(f"\n[SAVED] All datasets saved to: {output_dir.absolute()}")
    
    # Create summary report
    create_summary_report(master_dataset, output_dir)
    
    return master_dataset

def create_summary_report(dataset, output_dir):
    """Create a human-readable summary report"""
    
    report_file = output_dir / "DATASET_SUMMARY.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Canadian Provincial Legal Datasets Summary\n\n")
        f.write(f"**Created:** {dataset['created']}\n\n")
        f.write(f"**Total Provinces/Territories:** {dataset['total_provinces']}\n\n")
        
        f.write("## Legal Categories Covered\n\n")
        for category, info in dataset['legal_categories'].items():
            f.write(f"### {category}\n")
            f.write(f"{info['description']}\n\n")
            f.write("**Common Topics:**\n")
            for topic in info['common_topics']:
                f.write(f"- {topic}\n")
            f.write("\n")
        
        f.write("## Provincial Coverage\n\n")
        f.write("| Province | Code | Traffic Act | Resources |\n")
        f.write("|----------|------|-------------|----------|\n")
        
        for code, province in dataset['provinces'].items():
            name = province['name']
            traffic_act = province['legal_resources']['Traffic Law']['primary_act']
            resource_count = len(province['legal_resources'])
            f.write(f"| {name} | {code} | {traffic_act} | {resource_count} categories |\n")
        
        f.write("\n## Usage\n\n")
        f.write("These datasets power the PLAZA-AI Legal Assistant to provide:\n\n")
        f.write("- **Province-specific legal resources** based on user location\n")
        f.write("- **Dynamic government links** for each province\n")
        f.write("- **Accurate legal information** tailored to jurisdiction\n")
        f.write("- **Comprehensive coverage** of all Canadian provinces and territories\n\n")
        
        f.write("## Files\n\n")
        f.write("- `master_provincial_dataset.json` - Complete dataset for all provinces\n")
        f.write("- `[PROVINCE_CODE]_legal_dataset.json` - Individual province datasets\n")
        f.write("- `DATASET_SUMMARY.md` - This summary report\n")
    
        print(f"  [REPORT] Summary report: {report_file}")

if __name__ == "__main__":
    dataset = create_provincial_dataset()
    print("\n[SUCCESS] All provincial datasets created successfully!")
    print("\n[INFO] The system will now dynamically serve resources based on province selection.")
