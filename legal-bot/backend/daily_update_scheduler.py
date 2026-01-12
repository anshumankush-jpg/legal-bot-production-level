"""
Daily Update Scheduler for Legal Data
Runs automated updates of legal data from all configured sources
"""

import schedule
import time
import logging
from datetime import datetime
from legal_data_scraper import LegalDataScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('legal_data_updates.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_daily_update():
    """Execute daily data update"""
    logger.info("="*80)
    logger.info(f"Starting scheduled legal data update at {datetime.now()}")
    logger.info("="*80)
    
    try:
        scraper = LegalDataScraper()
        summary = scraper.daily_update()
        
        # Log summary
        total_updates = len(summary["updates"])
        successful = sum(1 for u in summary["updates"] if u["status"] == "success")
        failed = total_updates - successful
        
        logger.info(f"Update complete: {successful}/{total_updates} successful, {failed} failed")
        
        if failed > 0:
            logger.warning(f"Some updates failed. Check logs for details.")
        
    except Exception as e:
        logger.error(f"Critical error during daily update: {e}", exc_info=True)
    
    logger.info("="*80)
    logger.info("Daily update finished")
    logger.info("="*80)

def start_scheduler():
    """Start the daily update scheduler"""
    logger.info("Legal Data Update Scheduler Starting...")
    logger.info(f"Scheduled to run daily at 2:00 AM")
    
    # Schedule daily update at 2 AM
    schedule.every().day.at("02:00").do(run_daily_update)
    
    # Also run immediately on startup (optional)
    # run_daily_update()
    
    logger.info("Scheduler is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)

if __name__ == "__main__":
    start_scheduler()
