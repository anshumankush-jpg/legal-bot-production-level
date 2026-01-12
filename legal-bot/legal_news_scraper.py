"""
Legal News and Updates Scraper
Automatically scrapes legal websites daily for new laws, amendments, and legal updates
Supports Canadian and US legal sources
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import hashlib
import os
import re

# Legal news and update sources
LEGAL_SOURCES = {
    "canada_federal": [
        {
            "name": "Justice Canada - What's New",
            "url": "https://www.justice.gc.ca/eng/news-nouv/index.html",
            "type": "news",
            "jurisdiction": "Canada Federal"
        },
        {
            "name": "Canada Gazette",
            "url": "https://gazette.gc.ca/rp-pr/p1/index-eng.html",
            "type": "official",
            "jurisdiction": "Canada Federal"
        }
    ],
    "canada_provincial": [
        {
            "name": "Ontario Laws Updates",
            "url": "https://www.ontario.ca/laws",
            "type": "legislation",
            "jurisdiction": "Ontario"
        },
        {
            "name": "BC Laws Updates",
            "url": "https://www.bclaws.gov.bc.ca/",
            "type": "legislation",
            "jurisdiction": "British Columbia"
        },
        {
            "name": "Alberta Laws",
            "url": "https://www.alberta.ca/laws-and-legislation.aspx",
            "type": "legislation",
            "jurisdiction": "Alberta"
        }
    ],
    "usa_federal": [
        {
            "name": "Congress.gov Recent Laws",
            "url": "https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%7D",
            "type": "legislation",
            "jurisdiction": "USA Federal"
        },
        {
            "name": "Federal Register",
            "url": "https://www.federalregister.gov/",
            "type": "official",
            "jurisdiction": "USA Federal"
        },
        {
            "name": "DOJ Press Releases",
            "url": "https://www.justice.gov/news",
            "type": "news",
            "jurisdiction": "USA Federal"
        }
    ],
    "usa_state": [
        {
            "name": "California Legislative Information",
            "url": "https://leginfo.legislature.ca.gov/",
            "type": "legislation",
            "jurisdiction": "California"
        },
        {
            "name": "Texas Legislature Online",
            "url": "https://capitol.texas.gov/",
            "type": "legislation",
            "jurisdiction": "Texas"
        },
        {
            "name": "New York State Senate",
            "url": "https://www.nysenate.gov/legislation",
            "type": "legislation",
            "jurisdiction": "New York"
        }
    ]
}

# RSS Feeds for legal updates
RSS_FEEDS = [
    {
        "name": "Supreme Court of Canada",
        "url": "https://www.scc-csc.ca/case-dossier/info/rss-eng.aspx",
        "jurisdiction": "Canada Federal",
        "type": "case_law"
    },
    {
        "name": "US Supreme Court",
        "url": "https://www.supremecourt.gov/rss/cases.xml",
        "jurisdiction": "USA Federal",
        "type": "case_law"
    }
]


class LegalNewsScraper:
    """Scrapes legal news and updates from various sources"""
    
    def __init__(self, data_dir="legal_updates"):
        self.data_dir = data_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load previous updates
        self.previous_updates = self.load_previous_updates()
    
    def load_previous_updates(self) -> Dict:
        """Load previously scraped updates"""
        updates_file = os.path.join(self.data_dir, "previous_updates.json")
        if os.path.exists(updates_file):
            with open(updates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_updates(self, updates: Dict):
        """Save scraped updates"""
        updates_file = os.path.join(self.data_dir, "previous_updates.json")
        with open(updates_file, 'w', encoding='utf-8') as f:
            json.dump(updates, f, indent=2, ensure_ascii=False)
    
    def generate_hash(self, content: str) -> str:
        """Generate hash for content to detect duplicates"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def scrape_generic_news(self, source: Dict) -> List[Dict]:
        """Generic scraper for news pages"""
        updates = []
        
        try:
            print(f"  Scraping: {source['name']}...")
            response = self.session.get(source['url'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for common news article patterns
            articles = soup.find_all(['article', 'div'], class_=re.compile(r'news|article|post|item'))
            
            for article in articles[:10]:  # Limit to 10 most recent
                try:
                    # Extract title
                    title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Extract link
                    link_elem = article.find('a', href=True)
                    link = link_elem['href'] if link_elem else ""
                    if link and not link.startswith('http'):
                        from urllib.parse import urljoin
                        link = urljoin(source['url'], link)
                    
                    # Extract date
                    date_elem = article.find(['time', 'span'], class_=re.compile(r'date|time'))
                    date_str = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')
                    
                    # Extract summary
                    summary_elem = article.find(['p', 'div'], class_=re.compile(r'summary|excerpt|description'))
                    summary = summary_elem.get_text(strip=True)[:300] if summary_elem else ""
                    
                    # Generate hash
                    content_hash = self.generate_hash(title + link)
                    
                    # Check if new
                    if content_hash not in self.previous_updates:
                        updates.append({
                            "hash": content_hash,
                            "title": title,
                            "link": link,
                            "date": date_str,
                            "summary": summary,
                            "source": source['name'],
                            "jurisdiction": source['jurisdiction'],
                            "type": source['type'],
                            "scraped_at": datetime.now().isoformat()
                        })
                
                except Exception as e:
                    continue
            
            print(f"    Found {len(updates)} new updates")
            
        except Exception as e:
            print(f"    Error scraping {source['name']}: {str(e)}")
        
        return updates
    
    def scrape_rss_feed(self, feed: Dict) -> List[Dict]:
        """Scrape RSS feed for updates"""
        updates = []
        
        try:
            print(f"  Scraping RSS: {feed['name']}...")
            response = self.session.get(feed['url'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            
            items = soup.find_all('item')
            
            for item in items[:10]:
                try:
                    title = item.find('title').get_text(strip=True) if item.find('title') else ""
                    link = item.find('link').get_text(strip=True) if item.find('link') else ""
                    description = item.find('description').get_text(strip=True) if item.find('description') else ""
                    pub_date = item.find('pubDate').get_text(strip=True) if item.find('pubDate') else ""
                    
                    content_hash = self.generate_hash(title + link)
                    
                    if content_hash not in self.previous_updates:
                        updates.append({
                            "hash": content_hash,
                            "title": title,
                            "link": link,
                            "date": pub_date,
                            "summary": description[:300],
                            "source": feed['name'],
                            "jurisdiction": feed['jurisdiction'],
                            "type": feed['type'],
                            "scraped_at": datetime.now().isoformat()
                        })
                
                except Exception as e:
                    continue
            
            print(f"    Found {len(updates)} new updates")
            
        except Exception as e:
            print(f"    Error scraping RSS {feed['name']}: {str(e)}")
        
        return updates
    
    def scrape_all_sources(self) -> Dict[str, List[Dict]]:
        """Scrape all configured sources"""
        all_updates = {
            "canada_federal": [],
            "canada_provincial": [],
            "usa_federal": [],
            "usa_state": [],
            "rss_feeds": []
        }
        
        print("\n" + "="*80)
        print("LEGAL NEWS SCRAPER - DAILY UPDATE")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Scrape Canadian federal sources
        print("\n[*] Scraping Canadian Federal Sources...")
        for source in LEGAL_SOURCES["canada_federal"]:
            updates = self.scrape_generic_news(source)
            all_updates["canada_federal"].extend(updates)
            time.sleep(2)  # Be respectful
        
        # Scrape Canadian provincial sources
        print("\n[*] Scraping Canadian Provincial Sources...")
        for source in LEGAL_SOURCES["canada_provincial"]:
            updates = self.scrape_generic_news(source)
            all_updates["canada_provincial"].extend(updates)
            time.sleep(2)
        
        # Scrape US federal sources
        print("\n[*] Scraping US Federal Sources...")
        for source in LEGAL_SOURCES["usa_federal"]:
            updates = self.scrape_generic_news(source)
            all_updates["usa_federal"].extend(updates)
            time.sleep(2)
        
        # Scrape US state sources
        print("\n[*] Scraping US State Sources...")
        for source in LEGAL_SOURCES["usa_state"]:
            updates = self.scrape_generic_news(source)
            all_updates["usa_state"].extend(updates)
            time.sleep(2)
        
        # Scrape RSS feeds
        print("\n[*] Scraping RSS Feeds...")
        for feed in RSS_FEEDS:
            updates = self.scrape_rss_feed(feed)
            all_updates["rss_feeds"].extend(updates)
            time.sleep(2)
        
        return all_updates
    
    def generate_report(self, updates: Dict[str, List[Dict]]) -> str:
        """Generate a report of new updates"""
        report = []
        report.append("="*80)
        report.append("LEGAL UPDATES REPORT")
        report.append("="*80)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*80)
        
        total_updates = sum(len(v) for v in updates.values())
        report.append(f"\nTotal New Updates Found: {total_updates}")
        
        for category, items in updates.items():
            if items:
                report.append(f"\n--- {category.upper().replace('_', ' ')} ({len(items)} updates) ---")
                for item in items:
                    report.append(f"\n  Title: {item['title']}")
                    report.append(f"  Source: {item['source']}")
                    report.append(f"  Jurisdiction: {item['jurisdiction']}")
                    report.append(f"  Date: {item['date']}")
                    if item['link']:
                        report.append(f"  Link: {item['link']}")
                    if item['summary']:
                        report.append(f"  Summary: {item['summary'][:200]}...")
        
        if total_updates == 0:
            report.append("\n[INFO] No new updates found since last scrape.")
        
        return "\n".join(report)
    
    def save_daily_report(self, updates: Dict[str, List[Dict]]):
        """Save daily report to file"""
        date_str = datetime.now().strftime('%Y%m%d')
        report_file = os.path.join(self.data_dir, f"legal_updates_{date_str}.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "date": datetime.now().isoformat(),
                "total_updates": sum(len(v) for v in updates.values()),
                "updates": updates
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n[FILE] Daily report saved to: {report_file}")
        
        # Update previous updates
        for category, items in updates.items():
            for item in items:
                self.previous_updates[item['hash']] = {
                    "title": item['title'],
                    "date": item['date'],
                    "scraped_at": item['scraped_at']
                }
        
        self.save_updates(self.previous_updates)


def main():
    """Main scraper function"""
    scraper = LegalNewsScraper()
    
    # Scrape all sources
    updates = scraper.scrape_all_sources()
    
    # Generate and print report
    report = scraper.generate_report(updates)
    print("\n" + report)
    
    # Save daily report
    scraper.save_daily_report(updates)
    
    print("\n" + "="*80)
    print("SCRAPING COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
