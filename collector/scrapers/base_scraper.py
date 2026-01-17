"""Base scraper class for court portal collection."""
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from ..models import JurisdictionRecord, Portal, SeedSource
from ..validators import verify_portal
from ..normalizers import normalize_city, normalize_province_state
from ..config import REQUEST_DELAY, USER_AGENT, TIMEOUT
import time

logger = logging.getLogger(__name__)


class BaseScraper:
    """Base class for scraping court portals."""
    
    def __init__(self, seed_file: Path, country: str, dry_run: bool = False):
        """Initialize scraper.
        
        Args:
            seed_file: Path to JSON file with seed sources
            country: "Canada" or "USA"
            dry_run: If True, don't make actual HTTP requests
        """
        self.country = country
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        
        # Load seed sources
        with open(seed_file, 'r', encoding='utf-8') as f:
            seed_data = json.load(f)
            self.seeds = [SeedSource(**seed) for seed in seed_data]
        
        logger.info(f"Initialized {country} scraper with {len(self.seeds)} seed sources")
    
    def search_for_portal(self, city: str, province_state: str, search_pattern: str) -> List[str]:
        """Search for court portals using search pattern.
        
        This is a placeholder - in production you'd integrate with:
        - Google Custom Search API
        - Bing Search API
        - SerpAPI
        - Or similar service
        
        For now, returns empty list to avoid API costs.
        """
        query = search_pattern.format(city=city)
        logger.info(f"Search query would be: {query} (not implemented in dry mode)")
        return []
    
    def scrape_directory_page(self, url: str) -> List[Dict[str, str]]:
        """Scrape a directory page for court links.
        
        Returns list of dicts with 'name', 'url', 'authority' fields.
        """
        if self.dry_run:
            logger.info(f"DRY RUN: Would scrape {url}")
            return []
        
        try:
            response = self.session.get(url, timeout=TIMEOUT, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Look for links containing court-related keywords
            keywords = ['court', 'ticket', 'case', 'lookup', 'municipal', 'provincial', 'traffic']
            
            for link in soup.find_all('a', href=True):
                text = link.get_text(strip=True).lower()
                href = link['href']
                
                # Check if link text contains keywords
                if any(keyword in text for keyword in keywords):
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        from urllib.parse import urljoin
                        href = urljoin(url, href)
                    
                    if href.startswith('http'):
                        results.append({
                            'name': link.get_text(strip=True),
                            'url': href,
                            'authority': 'Unknown'  # Would need to extract from context
                        })
            
            time.sleep(REQUEST_DELAY)
            logger.info(f"Found {len(results)} potential portals from {url}")
            return results
        
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return []
    
    def create_record(
        self,
        province_state: str,
        city: str,
        portals: List[Portal],
        ticket_types: List[str],
        jurisdiction_level: str = "city"
    ) -> JurisdictionRecord:
        """Create a jurisdiction record."""
        normalized_province = normalize_province_state(province_state, self.country)
        normalized_city = normalize_city(city)
        
        record_id = JurisdictionRecord.generate_id(
            self.country,
            normalized_province,
            normalized_city,
            ""
        )
        
        return JurisdictionRecord(
            id=record_id,
            country=self.country,
            province_state=normalized_province,
            city_or_county=normalized_city,
            jurisdiction_level=jurisdiction_level,
            ticket_types=ticket_types,
            portals=portals,
            language=["en"] if self.country == "USA" else ["en", "fr"]
        )
    
    def collect_for_city(
        self,
        city: str,
        seed: SeedSource,
        verify: bool = False
    ) -> Optional[JurisdictionRecord]:
        """Collect portals for a specific city.
        
        Args:
            city: City name
            seed: Seed source for the province/state
            verify: Whether to verify URLs (slow)
        
        Returns:
            JurisdictionRecord or None if no portals found
        """
        logger.info(f"Collecting portals for {city}, {seed.region_name}")
        
        portals = []
        
        # Try search patterns if available
        for pattern in seed.search_patterns[:1]:  # Limit to 1 pattern to avoid API costs
            urls = self.search_for_portal(city, seed.region_name, pattern)
            for url in urls:
                # Would verify and create portal here
                pass
        
        # For now, return None - would be populated by actual scraping
        if not portals:
            logger.info(f"No portals found for {city}, {seed.region_name}")
            return None
        
        return self.create_record(
            province_state=seed.region_name,
            city=city,
            portals=portals,
            ticket_types=["traffic", "parking", "municipal"]
        )
    
    def collect_all(self, verify: bool = False, limit_cities: Optional[int] = None) -> List[JurisdictionRecord]:
        """Collect all portals for all seeds.
        
        Args:
            verify: Whether to verify URLs
            limit_cities: Max cities per province/state (for testing)
        
        Returns:
            List of jurisdiction records
        """
        all_records = []
        
        for seed in self.seeds:
            logger.info(f"Processing {seed.region_name}")
            
            # Collect for each city
            cities = seed.top_cities[:limit_cities] if limit_cities else seed.top_cities
            
            for city in cities:
                record = self.collect_for_city(city, seed, verify=verify)
                if record:
                    all_records.append(record)
            
            # Also create a province/state level record
            # This would contain province-wide portals
        
        logger.info(f"Collected {len(all_records)} records total")
        return all_records
