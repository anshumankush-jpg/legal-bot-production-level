"""
Legal Data Scraper and Update System
Fetches case law, statutes, and legal information from official sources
"""

import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalDataScraper:
    """Scrapes and updates legal data from official sources"""
    
    def __init__(self, data_dir="./legal_data_cache"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.cache_duration = 24  # hours
        
    def should_update(self, cache_file):
        """Check if cache needs updating"""
        if not cache_file.exists():
            return True
        
        modified_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age_hours = (datetime.now() - modified_time).total_seconds() / 3600
        
        return age_hours >= self.cache_duration
    
    def fetch_canlii_recent_cases(self, law_type="all", province=None, limit=50):
        """
        Fetch recent cases from CanLII
        Note: Requires CanLII API key for full access
        """
        logger.info(f"Fetching recent cases for {law_type} in {province or 'all jurisdictions'}")
        
        # CanLII API endpoint (requires registration and API key)
        # For demo purposes, we'll structure the response format
        # In production, you would implement actual API calls
        
        cache_file = self.data_dir / f"canlii_{law_type}_{province}_{datetime.now().strftime('%Y%m%d')}.json"
        
        if not self.should_update(cache_file):
            logger.info(f"Using cached data from {cache_file}")
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # Structure for case data
        cases = {
            "source": "CanLII",
            "last_updated": datetime.now().isoformat(),
            "jurisdiction": province or "Federal",
            "law_type": law_type,
            "cases": []
        }
        
        # In production: Implement actual API calls here
        # Example structure of what the API would return
        """
        response = requests.get(
            f"https://api.canlii.org/v1/caseBrowse/{language}/{jurisdiction}/",
            headers={"Authorization": f"Bearer {API_KEY}"},
            params={
                "offset": 0,
                "resultCount": limit
            }
        )
        """
        
        # Cache the results
        with open(cache_file, 'w') as f:
            json.dump(cases, f, indent=2)
        
        return cases
    
    def fetch_legislation_updates(self, jurisdiction, law_type):
        """Fetch recent legislation updates"""
        logger.info(f"Checking legislation updates for {law_type} in {jurisdiction}")
        
        cache_file = self.data_dir / f"legislation_{jurisdiction}_{law_type}_{datetime.now().strftime('%Y%m%d')}.json"
        
        if not self.should_update(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        legislation = {
            "source": "Official Government Sources",
            "last_updated": datetime.now().isoformat(),
            "jurisdiction": jurisdiction,
            "law_type": law_type,
            "updates": []
        }
        
        # Cache results
        with open(cache_file, 'w') as f:
            json.dump(legislation, f, indent=2)
        
        return legislation
    
    def fetch_case_summaries(self, jurisdiction, law_type, date_from=None):
        """
        Fetch case summaries with citations
        Generates structured data with:
        - Case name
        - Citation
        - Court
        - Date
        - Summary
        - Key principles
        - Related statutes
        """
        if date_from is None:
            date_from = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        logger.info(f"Fetching case summaries from {date_from}")
        
        cache_file = self.data_dir / f"summaries_{jurisdiction}_{law_type}_{datetime.now().strftime('%Y%m%d')}.json"
        
        if not self.should_update(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        summaries = {
            "source": "Multiple Legal Databases",
            "last_updated": datetime.now().isoformat(),
            "jurisdiction": jurisdiction,
            "law_type": law_type,
            "date_from": date_from,
            "summaries": []
        }
        
        # In production: Fetch from actual sources
        # This would integrate with CanLII, court websites, etc.
        
        with open(cache_file, 'w') as f:
            json.dump(summaries, f, indent=2)
        
        return summaries
    
    def get_data_sources_metadata(self):
        """Return metadata about all configured data sources"""
        from legal_data_sources import LEGAL_DATA_SOURCES
        
        sources_info = []
        for country, jurisdictions in LEGAL_DATA_SOURCES.items():
            for jurisdiction, data in jurisdictions.items():
                for source in data.get("sources", []):
                    sources_info.append({
                        "name": source["name"],
                        "url": source["url"],
                        "country": country,
                        "jurisdiction": jurisdiction,
                        "type": source["type"],
                        "free": source["free"],
                        "api_available": source["api_available"],
                        "description": source["description"]
                    })
        
        return sources_info
    
    def daily_update(self):
        """Run daily data update for all configured sources"""
        logger.info("Starting daily legal data update...")
        
        from legal_data_sources import LEGAL_DATA_SOURCES, LAW_TYPE_SOURCE_MAPPING
        
        update_summary = {
            "timestamp": datetime.now().isoformat(),
            "updates": []
        }
        
        # Update each law type for each jurisdiction
        for country, jurisdictions in LEGAL_DATA_SOURCES.items():
            for jurisdiction, data in jurisdictions.items():
                for law_type in data.get("categories", []):
                    try:
                        # Fetch recent cases
                        cases = self.fetch_canlii_recent_cases(
                            law_type=law_type,
                            province=jurisdiction if jurisdiction != "Federal" else None
                        )
                        
                        # Fetch legislation updates
                        legislation = self.fetch_legislation_updates(jurisdiction, law_type)
                        
                        # Fetch case summaries
                        summaries = self.fetch_case_summaries(jurisdiction, law_type)
                        
                        update_summary["updates"].append({
                            "country": country,
                            "jurisdiction": jurisdiction,
                            "law_type": law_type,
                            "status": "success",
                            "cases_count": len(cases.get("cases", [])),
                            "legislation_count": len(legislation.get("updates", [])),
                            "summaries_count": len(summaries.get("summaries", []))
                        })
                        
                        # Rate limiting
                        time.sleep(1)
                        
                    except Exception as e:
                        logger.error(f"Error updating {law_type} for {jurisdiction}: {e}")
                        update_summary["updates"].append({
                            "country": country,
                            "jurisdiction": jurisdiction,
                            "law_type": law_type,
                            "status": "error",
                            "error": str(e)
                        })
        
        # Save update summary
        summary_file = self.data_dir / f"update_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(update_summary, f, indent=2)
        
        logger.info(f"Daily update complete. Summary saved to {summary_file}")
        return update_summary


if __name__ == "__main__":
    # Run daily update
    scraper = LegalDataScraper()
    scraper.daily_update()
