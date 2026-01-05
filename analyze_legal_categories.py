#!/usr/bin/env python3
V# -*- coding: utf-8 -*-
"""
Analyze and categorize all legal documents in your dataset.
Shows breakdown by legal category, jurisdiction, and priority.
"""

import sys
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List
import json

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from legal_category_mapper import (
        categorize_document_batch,
        get_category_display_name,
        APP_PRIORITY_CATEGORIES
    )
except ImportError:
    print("ERROR: legal_category_mapper.py not found!")
    print("Make sure legal_category_mapper.py is in the project root.")
    sys.exit(1)

# Document directories to analyze
DOCUMENT_DIRECTORIES = [
    "canada criminal and federal law",
    "CANADA TRAFFIC FILES",
    "canada_case_law",
    "canada_criminal_law",
    "canada_traffic_acts",
    "data/downloaded_pdfs",
    "docs/downloaded_pdfs",
    "us_state_codes",
    "us_traffic_laws",
    "usa",
    "usa_case_law",
    "usa_criminal_law"
]

SUPPORTED_EXTENSIONS = {'.pdf', '.html', '.htm', '.txt', '.docx', '.json', '.md'}


def find_all_documents(base_path: Path) -> List[Path]:
    """Find all supported documents."""
    documents = []
    
    for doc_dir in DOCUMENT_DIRECTORIES:
        dir_path = base_path / doc_dir
        if dir_path.exists() and dir_path.is_dir():
            for file_path in dir_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    documents.append(file_path)
    
    return documents


def analyze_categories(documents: List[Path]) -> Dict:
    """Analyze and categorize all documents."""
    print(f"\n[*] Analyzing {len(documents)} documents...\n")
    
    # Categorize all documents
    results = categorize_document_batch(documents)
    
    # Build statistics
    stats = {
        'by_category': defaultdict(int),
        'by_jurisdiction': defaultdict(int),
        'by_priority': defaultdict(int),
        'high_priority_count': 0,
        'category_details': defaultdict(lambda: {
            'count': 0,
            'jurisdictions': defaultdict(int),
            'files': []
        })
    }
    
    for file_path, info in results.items():
        category = info['primary_category']
        jurisdiction = info['jurisdiction']
        priority = info['priority']
        
        # Count by category
        stats['by_category'][category] += 1
        
        # Count by jurisdiction
        stats['by_jurisdiction'][jurisdiction] += 1
        
        # Count by priority
        stats['by_priority'][priority] += 1
        
        # High priority count
        if info['is_high_priority']:
            stats['high_priority_count'] += 1
        
        # Category details
        cat_detail = stats['category_details'][category]
        cat_detail['count'] += 1
        cat_detail['jurisdictions'][jurisdiction] += 1
        cat_detail['files'].append({
            'file': Path(file_path).name,
            'jurisdiction': jurisdiction,
            'subcategory': info['subcategory'],
            'priority': priority
        })
    
    return stats, results


def print_analysis(stats: Dict, results: Dict):
    """Print formatted analysis results."""
    
    print("=" * 80)
    print("LEGAL DOCUMENT CATEGORIZATION ANALYSIS")
    print("=" * 80)
    
    # Overall statistics
    print(f"\n[*] OVERALL STATISTICS")
    print(f"  Total Documents: {sum(stats['by_category'].values())}")
    print(f"  High Priority Documents: {stats['high_priority_count']} (for your app)")
    
    # By jurisdiction
    print(f"\n[*] BY JURISDICTION")
    for jurisdiction, count in sorted(stats['by_jurisdiction'].items(), key=lambda x: -x[1]):
        print(f"  {jurisdiction:12} : {count:4} documents")
    
    # By category (sorted by priority)
    print(f"\n[*] BY LEGAL CATEGORY (Priority Order)")
    print("-" * 80)
    
    # Sort categories by priority
    category_list = []
    for category, count in stats['by_category'].items():
        try:
            priority = APP_PRIORITY_CATEGORIES.index(category)
        except ValueError:
            priority = 999
        category_list.append((priority, category, count))
    
    category_list.sort()
    
    for priority, category, count in category_list:
        display_name = get_category_display_name(category)
        priority_marker = "[HIGH]" if priority < 4 else "      "
        print(f"{priority_marker} [{priority:2}] {display_name:35} : {count:4} documents")
        
        # Show jurisdiction breakdown for this category
        cat_detail = stats['category_details'][category]
        if len(cat_detail['jurisdictions']) > 1:
            for jur, jur_count in sorted(cat_detail['jurisdictions'].items(), key=lambda x: -x[1]):
                print(f"      └─ {jur:12} : {jur_count:4} documents")
    
    # High priority categories detail
    print(f"\n[HIGH PRIORITY] HIGH PRIORITY CATEGORIES (Core for Your App)")
    print("-" * 80)
    for priority, category, count in category_list:
        if priority < 4:
            display_name = get_category_display_name(category)
            cat_detail = stats['category_details'][category]
            print(f"\n  {display_name} ({count} documents)")
            print(f"    Priority: {priority} (Lower = Higher Priority)")
            
            # Show sample files
            sample_files = cat_detail['files'][:5]
            print(f"    Sample files:")
            for file_info in sample_files:
                print(f"      • {file_info['file']} [{file_info['jurisdiction']}]")
            if len(cat_detail['files']) > 5:
                print(f"      ... and {len(cat_detail['files']) - 5} more")
    
    # Summary recommendations
    print(f"\n[*] RECOMMENDATIONS")
    print("-" * 80)
    print(f"  1. Focus ingestion on HIGH PRIORITY categories first:")
    for priority, category, count in category_list[:4]:
        display_name = get_category_display_name(category)
        print(f"     • {display_name} ({count} documents)")
    
    print(f"\n  2. Total high-priority documents: {stats['high_priority_count']}")
    print(f"  3. These categories cover your core use case: tickets, summons, paralegal advice")
    
    print("\n" + "=" * 80)


def save_analysis_report(stats: Dict, results: Dict, output_file: str = "legal_category_analysis.json"):
    """Save analysis to JSON file."""
    report = {
        'summary': {
            'total_documents': sum(stats['by_category'].values()),
            'high_priority_count': stats['high_priority_count'],
            'by_jurisdiction': dict(stats['by_jurisdiction']),
            'by_category': dict(stats['by_category']),
            'by_priority': dict(stats['by_priority'])
        },
        'category_details': {
            cat: {
                'count': detail['count'],
                'jurisdictions': dict(detail['jurisdictions']),
                'files': detail['files']
            }
            for cat, detail in stats['category_details'].items()
        },
        'all_documents': {
            str(path): info
            for path, info in results.items()
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[*] Analysis saved to: {output_file}")


def main():
    """Main analysis function."""
    base_path = Path(__file__).parent
    
    # Find all documents
    print("[*] Scanning for documents...")
    documents = find_all_documents(base_path)
    
    if not documents:
        print("[!] No documents found!")
        return
    
    # Analyze
    stats, results = analyze_categories(documents)
    
    # Print analysis
    print_analysis(stats, results)
    
    # Save report
    save_analysis_report(stats, results)
    
    print("\n[+] Analysis complete!")


if __name__ == '__main__':
    main()
