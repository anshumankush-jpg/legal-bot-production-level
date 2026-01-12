"""
Daily Legal Updater
Runs the legal news scraper daily and ingests new content into the vector database
"""

import schedule
import time
from datetime import datetime
import subprocess
import os
import json
import requests

# Configuration
SCRAPER_SCRIPT = "legal_news_scraper.py"
BACKEND_URL = "http://localhost:8000"
UPDATES_DIR = "legal_updates"


def run_scraper():
    """Run the legal news scraper"""
    print(f"\n{'='*80}")
    print(f"RUNNING DAILY LEGAL UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    try:
        # Run the scraper
        result = subprocess.run(
            ["python", SCRAPER_SCRIPT],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n[OK] Scraper completed successfully")
            return True
        else:
            print(f"\n[X] Scraper failed with error:\n{result.stderr}")
            return False
            
    except Exception as e:
        print(f"[X] Error running scraper: {str(e)}")
        return False


def ingest_new_updates():
    """Ingest new legal updates into the vector database"""
    print(f"\n[*] Ingesting new updates into vector database...")
    
    try:
        # Find today's update file
        date_str = datetime.now().strftime('%Y%m%d')
        update_file = os.path.join(UPDATES_DIR, f"legal_updates_{date_str}.json")
        
        if not os.path.exists(update_file):
            print("[!] No updates file found for today")
            return False
        
        # Load updates
        with open(update_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total_updates = data.get('total_updates', 0)
        
        if total_updates == 0:
            print("[INFO] No new updates to ingest")
            return True
        
        print(f"[*] Found {total_updates} new updates to ingest")
        
        # Prepare documents for ingestion
        documents = []
        for category, items in data.get('updates', {}).items():
            for item in items:
                doc = {
                    "title": item['title'],
                    "content": f"{item['title']}\n\n{item['summary']}\n\nSource: {item['source']}\nJurisdiction: {item['jurisdiction']}\nDate: {item['date']}\nLink: {item['link']}",
                    "metadata": {
                        "source": item['source'],
                        "jurisdiction": item['jurisdiction'],
                        "type": item['type'],
                        "date": item['date'],
                        "url": item['link'],
                        "category": category,
                        "scraped_at": item['scraped_at']
                    }
                }
                documents.append(doc)
        
        # TODO: Ingest into vector database
        # This would call your backend API to add these documents
        # For now, we'll save them to a file for manual ingestion
        
        ingestion_file = os.path.join(UPDATES_DIR, f"to_ingest_{date_str}.json")
        with open(ingestion_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Prepared {len(documents)} documents for ingestion")
        print(f"[FILE] Saved to: {ingestion_file}")
        print("[INFO] Manual ingestion required - upload via web interface")
        
        return True
        
    except Exception as e:
        print(f"[X] Error ingesting updates: {str(e)}")
        return False


def daily_update_job():
    """Complete daily update job"""
    print("\n" + "="*80)
    print("STARTING DAILY LEGAL UPDATE JOB")
    print("="*80)
    
    # Step 1: Run scraper
    scraper_success = run_scraper()
    
    if not scraper_success:
        print("\n[X] Daily update failed - scraper error")
        return
    
    # Step 2: Ingest new updates
    ingest_success = ingest_new_updates()
    
    if ingest_success:
        print("\n[OK] Daily update completed successfully")
    else:
        print("\n[!] Daily update completed with warnings")
    
    print("="*80)


def run_scheduler():
    """Run the scheduler"""
    print("="*80)
    print("DAILY LEGAL UPDATER - SCHEDULER")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Schedule: Daily at 2:00 AM")
    print("="*80)
    
    # Schedule daily update at 2:00 AM
    schedule.every().day.at("02:00").do(daily_update_job)
    
    # For testing: also run every hour (comment out in production)
    # schedule.every().hour.do(daily_update_job)
    
    print("\n[OK] Scheduler is running...")
    print("[INFO] Press Ctrl+C to stop\n")
    
    # Run once immediately for testing
    print("[*] Running initial update...")
    daily_update_job()
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n[INFO] Scheduler stopped by user")


if __name__ == "__main__":
    # Create updates directory if it doesn't exist
    os.makedirs(UPDATES_DIR, exist_ok=True)
    
    # Run scheduler
    run_scheduler()
