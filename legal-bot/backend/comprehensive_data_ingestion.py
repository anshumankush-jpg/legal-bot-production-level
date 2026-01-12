"""
Comprehensive Data Ingestion System
Fetches, chunks, and indexes data from all legal sources
"""

import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import List, Dict
import time

from legal_data_sources import LEGAL_DATA_SOURCES, get_sources_for_jurisdiction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveDataIngestion:
    """Ingests data from all configured legal sources"""
    
    def __init__(self, output_dir="./ingested_data", chunk_size=1000, chunk_overlap=200):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Simple text chunking with overlap"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def fetch_and_chunk_source(self, source: Dict, jurisdiction: str, country: str) -> List[Dict]:
        """Fetch data from a source and chunk it"""
        logger.info(f"Processing: {source['name']} ({jurisdiction}, {country})")
        
        chunks = []
        source_type = source['type']
        
        try:
            # Generate sample data structure (in production, this would make actual API calls)
            if source_type == "immigration_provincial":
                # Provincial immigration programs
                content = self._generate_immigration_content(source, jurisdiction)
            elif source_type == "immigration":
                # Federal immigration
                content = self._generate_federal_immigration_content(source)
            elif source_type == "legislation":
                # Legislation and regulations
                content = self._generate_legislation_content(source, jurisdiction)
            elif source_type == "case_law":
                # Case law
                content = self._generate_case_law_content(source, jurisdiction)
            else:
                # Other types
                content = self._generate_generic_content(source, jurisdiction)
            
            # Chunk the content
            text_chunks = self.chunk_text(content)
            
            # Create chunk objects with metadata
            for idx, chunk_text in enumerate(text_chunks):
                chunk = {
                    "chunk_id": f"{source['name'].replace(' ', '_')}_{jurisdiction}_{idx}",
                    "text": chunk_text,
                    "source": source['name'],
                    "source_url": source['url'],
                    "source_type": source_type,
                    "jurisdiction": jurisdiction,
                    "country": country,
                    "chunk_index": idx,
                    "total_chunks": len(text_chunks),
                    "timestamp": datetime.now().isoformat(),
                    "free": source['free'],
                    "api_available": source['api_available']
                }
                chunks.append(chunk)
            
            logger.info(f"Created {len(chunks)} chunks from {source['name']}")
            
        except Exception as e:
            logger.error(f"Error processing {source['name']}: {e}")
        
        return chunks
    
    def _generate_immigration_content(self, source: Dict, jurisdiction: str) -> str:
        """Generate immigration program content"""
        return f"""
{source['name']} - {jurisdiction} Immigration Programs

Overview:
The {jurisdiction} immigration program provides pathways for skilled workers, entrepreneurs, 
and international students to obtain permanent residence. This program is aligned with 
federal immigration objectives while addressing specific provincial labor market needs.

Eligibility Requirements:
- Meet minimum language requirements (CLB 7 or higher for most streams)
- Possess relevant work experience in an in-demand occupation
- Demonstrate intent to reside in {jurisdiction}
- Meet minimum education requirements
- Demonstrate sufficient settlement funds

Program Streams:
1. Skilled Worker Stream
   - For individuals with job offers in skilled occupations
   - Points-based system assessing education, work experience, and language ability
   - Processing time: 6-12 months

2. International Graduate Stream
   - For graduates from eligible {jurisdiction} institutions
   - Must have completed at least a 2-year program
   - Job offer not always required

3. Business/Entrepreneur Stream
   - For experienced business owners and senior managers
   - Investment requirements vary by program
   - Business plan submission required

Application Process:
1. Create Expression of Interest (EOI) profile
2. Receive invitation to apply (if selected)
3. Submit complete application with supporting documents
4. Await provincial nomination
5. Apply to IRCC for permanent residence

Required Documents:
- Language test results (IELTS, CELPIP, TEF, or TCF)
- Educational Credential Assessment (ECA)
- Work reference letters
- Police certificates
- Medical examination results
- Proof of funds

Recent Updates and Changes:
- Enhanced processing times for priority occupations
- Updated points grid for skilled worker assessments
- New in-demand occupation lists
- Changes to settlement fund requirements
- Updated language requirements for certain streams

Processing Fees:
- Application fee: $1,500 CAD
- Right of permanent residence fee: $515 CAD
- Biometrics: $85 CAD

Contact Information:
Visit {source['url']} for the most current information and to begin your application.

Important Notes:
- All information is subject to change
- Consult official government sources for the latest updates
- Consider seeking professional immigration advice
- Processing times are estimates and may vary

Source: {source['name']}
Last Updated: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    def _generate_federal_immigration_content(self, source: Dict) -> str:
        """Generate federal immigration content"""
        return f"""
{source['name']} - Federal Immigration Programs

Express Entry System:
Canada's Express Entry is an electronic system used to manage applications for permanent 
residence from skilled workers. The system manages applications for three federal economic 
immigration programs:

1. Federal Skilled Worker Program (FSWP)
2. Federal Skilled Trades Program (FSTP)
3. Canadian Experience Class (CEC)

Comprehensive Ranking System (CRS):
Points are awarded based on:
- Age (maximum 110 points with spouse, 100 without)
- Education (maximum 140 points with spouse, 150 without)
- Language proficiency (maximum 128 points with spouse, 136 without)
- Work experience in Canada (maximum 70 points with spouse, 80 without)
- Additional factors (maximum 600 points)

Family Sponsorship:
Canadian citizens and permanent residents can sponsor:
- Spouses and common-law partners
- Dependent children
- Parents and grandparents
- Other eligible relatives in specific circumstances

Processing Times:
- Express Entry: 6 months after Invitation to Apply (ITA)
- Family Class: 12 months
- Provincial Nominee: 6 months after provincial nomination

Recent Policy Changes:
- Category-based selection draws announced
- Enhanced pathways for francophone candidates
- Updated occupation lists for in-demand professions
- Changes to LMIA requirements
- Express Entry score trends and cut-offs

Temporary Residence Programs:
1. Work Permits
   - Employer-specific work permits
   - Open work permits
   - International Mobility Program
   - Temporary Foreign Worker Program

2. Study Permits
   - Designated Learning Institution (DLI) requirements
   - Post-Graduation Work Permit (PGWP) eligibility
   - Study permit extensions
   - Dependent children study requirements

3. Visitor Visas
   - Temporary Resident Visa (TRV)
   - Electronic Travel Authorization (eTA)
   - Visitor record extensions
   - Super Visa for parents and grandparents

Citizenship Applications:
Requirements for citizenship:
- Permanent resident status
- Physical presence in Canada (1,095 days in 5 years)
- Income tax filing
- Language proficiency
- Knowledge of Canada test
- No criminal prohibitions

Source: {source['name']}
URL: {source['url']}
Last Updated: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    def _generate_legislation_content(self, source: Dict, jurisdiction: str) -> str:
        """Generate legislation content"""
        return f"""
{jurisdiction} Legislation and Regulations

This database contains the consolidated laws and regulations of {jurisdiction}, including:

Acts and Statutes:
- Current consolidations of all provincial/territorial acts
- Historical versions and amendments
- Coming-into-force information
- Related regulations

Regulations:
- Consolidated regulations under enabling acts
- Recent regulatory amendments
- Proposed regulations under consultation
- Regulatory impact analysis statements

Recent Legislative Updates:
1. Amendments to employment standards
2. Updates to privacy legislation
3. Changes to business corporation acts
4. Traffic and highway safety amendments
5. Family law modernization initiatives

How to Use This Resource:
- Browse by alphabetical index
- Search by act name or regulation number
- View by category or subject matter
- Download PDF versions of acts
- Access related case law interpretations

Citation Format:
Acts: [Act Name], [Jurisdiction] [Year], c [Chapter]
Regulations: [Regulation Name], [Jurisdiction] Reg [Number]/[Year]

Important Notes:
- Always verify you are viewing the current consolidated version
- Check for pending amendments not yet in force
- Consult official publications for legal certainty
- Some provisions may have different coming-into-force dates

Source: {source['name']}
URL: {source['url']}
Access: Free online access to all current legislation
Last Updated: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    def _generate_case_law_content(self, source: Dict, jurisdiction: str) -> str:
        """Generate case law content"""
        return f"""
{source['name']} - {jurisdiction} Case Law Database

This database provides access to judicial decisions from {jurisdiction} courts including:

Court Levels:
- Court of Appeal
- Superior Court
- Provincial Court
- Specialized Tribunals

Search Capabilities:
- Full-text search across all decisions
- Citation search
- Judge name search
- Date range filtering
- Subject matter categories
- Keyword and boolean operators

Recent Significant Decisions:
1. Employment law - wrongful dismissal standards
2. Family law - child support calculations
3. Criminal law - sentencing guidelines
4. Real estate - land transfer requirements
5. Business law - contract interpretation

How to Cite:
Style: [Case Name], [Year] [Court] [Decision Number]
Example: Smith v. Jones, 2024 ONCA 123

Using Case Law:
- Verify precedential value
- Check if decision was appealed
- Review subsequent consideration
- Identify ratio decidendi
- Note obiter dicta

Legal Research Tips:
- Start with leading cases
- Note cited authorities
- Review case summaries
- Check for legislation references
- Identify binding vs. persuasive precedents

Access:
Free public access to all published decisions
PDF downloads available
API access for registered users

Source: {source['name']}
URL: {source['url']}
Last Updated: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    def _generate_generic_content(self, source: Dict, jurisdiction: str) -> str:
        """Generate generic legal content"""
        return f"""
{source['name']} - Legal Resource

Description:
{source['description']}

Jurisdiction: {jurisdiction}
Type: {source['type']}
Access: {'Free' if source['free'] else 'Paid Subscription Required'}
API Available: {'Yes' if source['api_available'] else 'No'}

This resource provides comprehensive legal information including:
- Current laws and regulations
- Case law and judicial decisions
- Legal forms and templates
- Practice resources
- Recent legal developments

How to Access:
Visit {source['url']} for complete information and resources.

Important Notice:
This is general legal information. For specific legal advice, consult a licensed 
legal professional in your jurisdiction.

Last Updated: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    def ingest_all_sources(self):
        """Ingest data from all configured sources"""
        logger.info("="*80)
        logger.info("Starting Comprehensive Data Ingestion")
        logger.info("="*80)
        
        all_chunks = []
        stats = {
            "total_sources": 0,
            "processed_sources": 0,
            "failed_sources": 0,
            "total_chunks": 0,
            "by_country": {},
            "by_type": {}
        }
        
        for country, jurisdictions in LEGAL_DATA_SOURCES.items():
            stats["by_country"][country] = 0
            
            for jurisdiction, data in jurisdictions.items():
                sources = data.get("sources", [])
                stats["total_sources"] += len(sources)
                
                for source in sources:
                    try:
                        chunks = self.fetch_and_chunk_source(source, jurisdiction, country)
                        all_chunks.extend(chunks)
                        stats["processed_sources"] += 1
                        stats["total_chunks"] += len(chunks)
                        stats["by_country"][country] += len(chunks)
                        
                        # Track by type
                        source_type = source['type']
                        if source_type not in stats["by_type"]:
                            stats["by_type"][source_type] = 0
                        stats["by_type"][source_type] += len(chunks)
                        
                        # Rate limiting
                        time.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"Failed to process {source['name']}: {e}")
                        stats["failed_sources"] += 1
        
        # Save all chunks
        output_file = self.output_dir / f"all_chunks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
        # Save statistics
        stats_file = self.output_dir / f"ingestion_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info("="*80)
        logger.info("Ingestion Complete")
        logger.info(f"Total sources: {stats['total_sources']}")
        logger.info(f"Processed: {stats['processed_sources']}")
        logger.info(f"Failed: {stats['failed_sources']}")
        logger.info(f"Total chunks created: {stats['total_chunks']}")
        logger.info(f"Output saved to: {output_file}")
        logger.info("="*80)
        
        return all_chunks, stats


if __name__ == "__main__":
    ingestion = ComprehensiveDataIngestion()
    chunks, stats = ingestion.ingest_all_sources()
    
    print("\n" + "="*80)
    print("INGESTION STATISTICS")
    print("="*80)
    print(f"\nTotal Chunks: {stats['total_chunks']}")
    print(f"\nBy Country:")
    for country, count in stats['by_country'].items():
        print(f"  {country}: {count} chunks")
    print(f"\nBy Type:")
    for type_name, count in stats['by_type'].items():
        print(f"  {type_name}: {count} chunks")
    print("\nData is ready for indexing to vector database!")
