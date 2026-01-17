"""Command-line interface for the collector."""
import json
import logging
import argparse
from pathlib import Path
from typing import List
from .scrapers import CanadaScraper, USAScraper
from .models import JurisdictionRecord
from .config import OUTPUT_DIR, OVERRIDES_DIR, LOG_LEVEL
from .lookup_api import get_lookup_api
import csv

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_manual_overrides() -> List[JurisdictionRecord]:
    """Load manual override records."""
    manual_file = OVERRIDES_DIR / "manual_portals.json"
    if not manual_file.exists():
        return []
    
    try:
        with open(manual_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [JurisdictionRecord(**record) for record in data]
    except Exception as e:
        logger.error(f"Error loading manual overrides: {e}")
        return []


def save_dataset(records: List[JurisdictionRecord], output_file: Path):
    """Save records to JSON file."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Convert to dicts
    data = [record.dict() for record in records]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(records)} records to {output_file}")


def collect_canada(verify: bool = False, limit: int = None):
    """Collect Canadian court portals."""
    logger.info("Starting Canadian portal collection")
    
    scraper = CanadaScraper(dry_run=False)
    records = scraper.collect_all(verify=verify, limit_cities=limit)
    
    # Add manual overrides for Canada
    manual_records = [r for r in load_manual_overrides() if r.country == "Canada"]
    
    # Merge: manual overrides replace auto-collected for same jurisdiction
    manual_ids = {r.id for r in manual_records}
    auto_records = [r for r in records if r.id not in manual_ids]
    
    all_records = manual_records + auto_records
    
    output_file = OUTPUT_DIR / "canada.json"
    save_dataset(all_records, output_file)
    
    return all_records


def collect_usa(verify: bool = False, limit: int = None):
    """Collect USA court portals."""
    logger.info("Starting USA portal collection")
    
    scraper = USAScraper(dry_run=False)
    records = scraper.collect_all(verify=verify, limit_cities=limit)
    
    # Add manual overrides for USA
    manual_records = [r for r in load_manual_overrides() if r.country == "USA"]
    
    # Merge: manual overrides replace auto-collected for same jurisdiction
    manual_ids = {r.id for r in manual_records}
    auto_records = [r for r in records if r.id not in manual_ids]
    
    all_records = manual_records + auto_records
    
    output_file = OUTPUT_DIR / "usa.json"
    save_dataset(all_records, output_file)
    
    return all_records


def collect_all(verify: bool = False, limit: int = None):
    """Collect all court portals (Canada + USA)."""
    logger.info("Starting full collection (Canada + USA)")
    
    canada_records = collect_canada(verify=verify, limit=limit)
    usa_records = collect_usa(verify=verify, limit=limit)
    
    all_records = canada_records + usa_records
    
    output_file = OUTPUT_DIR / "all.json"
    save_dataset(all_records, output_file)
    
    logger.info(f"Collection complete: {len(all_records)} total records")
    return all_records


def validate_dataset():
    """Validate the collected dataset."""
    logger.info("Validating dataset")
    
    all_file = OUTPUT_DIR / "all.json"
    if not all_file.exists():
        logger.error("Dataset not found. Run collection first.")
        return
    
    api = get_lookup_api(all_file)
    stats = api.get_stats()
    
    print("\n=== DATASET VALIDATION REPORT ===")
    print(f"Total Records: {stats['total_records']}")
    print(f"\nBy Country:")
    for country, count in stats['by_country'].items():
        print(f"  {country}: {count}")
    print(f"\nBy Verification Status:")
    for status, count in stats['by_verification'].items():
        print(f"  {status}: {count}")
    print(f"\nAverage Confidence: {stats['average_confidence']:.2f}")
    print("="*35 + "\n")


def export_csv():
    """Export dataset to CSV format."""
    logger.info("Exporting dataset to CSV")
    
    all_file = OUTPUT_DIR / "all.json"
    if not all_file.exists():
        logger.error("Dataset not found. Run collection first.")
        return
    
    with open(all_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    csv_file = OUTPUT_DIR / "all.csv"
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "ID", "Country", "Province/State", "City/County", "Jurisdiction Level",
            "Ticket Types", "Portal Name", "Portal URL", "Portal Type",
            "Verification Status", "Confidence"
        ])
        
        # Data
        for record in records:
            base_row = [
                record['id'],
                record['country'],
                record['province_state'],
                record['city_or_county'],
                record['jurisdiction_level'],
                ', '.join(record['ticket_types']),
            ]
            
            for portal in record['portals']:
                row = base_row + [
                    portal['name'],
                    portal['url'],
                    portal['portal_type'],
                    record['verification_status'],
                    record['confidence']
                ]
                writer.writerow(row)
    
    logger.info(f"Exported to {csv_file}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Court/Ticket Portal Dataset Collector for LEGID"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Collect commands
    collect_parser = subparsers.add_parser('collect', help='Collect portal data')
    collect_parser.add_argument(
        'country',
        choices=['canada', 'usa', 'all'],
        help='Country to collect data for'
    )
    collect_parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify URLs (slow)'
    )
    collect_parser.add_argument(
        '--limit',
        type=int,
        help='Limit cities per province/state (for testing)'
    )
    
    # Validate command
    subparsers.add_parser('validate', help='Validate collected dataset')
    
    # Export command
    subparsers.add_parser('export-csv', help='Export dataset to CSV')
    
    # Lookup command
    lookup_parser = subparsers.add_parser('lookup', help='Test lookup functionality')
    lookup_parser.add_argument('--city', help='City name')
    lookup_parser.add_argument('--province-state', help='Province or state')
    lookup_parser.add_argument('--country', choices=['Canada', 'USA'], help='Country')
    lookup_parser.add_argument('--ticket-type', help='Ticket type')
    lookup_parser.add_argument('--search', help='Free-text search query')
    
    args = parser.parse_args()
    
    if args.command == 'collect':
        if args.country == 'canada':
            collect_canada(verify=args.verify, limit=args.limit)
        elif args.country == 'usa':
            collect_usa(verify=args.verify, limit=args.limit)
        elif args.country == 'all':
            collect_all(verify=args.verify, limit=args.limit)
    
    elif args.command == 'validate':
        validate_dataset()
    
    elif args.command == 'export-csv':
        export_csv()
    
    elif args.command == 'lookup':
        api = get_lookup_api()
        
        if args.search:
            results = api.search(args.search)
        else:
            results = api.lookup_jurisdiction(
                country=args.country,
                province_state=args.province_state,
                city=args.city,
                ticket_type=args.ticket_type
            )
        
        print(json.dumps(results, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
