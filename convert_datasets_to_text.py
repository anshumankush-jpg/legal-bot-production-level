#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert Enhanced Legal Datasets to Text Files for Ingestion
Creates plain text files from JSON datasets for standard ingestion
"""
import json
from pathlib import Path
import os

def convert_dataset_to_text(json_file: Path, output_dir: Path):
    """Convert a single JSON dataset to text files"""
    with open(json_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    category = json_file.stem.replace('_dataset', '')
    category_dir = output_dir / category
    category_dir.mkdir(exist_ok=True)

    print(f"Converting {category} dataset...")

    file_count = 0

    for i, doc in enumerate(dataset.get('documents', []), 1):
        content = doc.get('content', '').strip()
        if not content:
            continue

        # Create filename
        title = doc.get('title', f'document_{i}').replace(' ', '_').replace('/', '_')
        filename = f"{category}_{i:02d}_{title[:50]}.txt"
        filepath = category_dir / filename

        # Create comprehensive text content
        text_content = f"""
LEGAL DOCUMENT - {doc.get('title', 'Unknown Title')}
Category: {category.replace('_', ' ').title()}
Type: {doc.get('type', 'guide')}
Jurisdictions: {', '.join(dataset.get('jurisdictions', []))}

CONTENT:
{content}

PRACTICAL SOLUTIONS:
{chr(10).join(f"• {solution}" for solution in doc.get('solutions', []))}

REFERENCE INFORMATION:
- URL: {doc.get('url', 'N/A')}
- Sections: {', '.join(doc.get('sections', []))}
- Document Type: {doc.get('type', 'guide')}

This document provides comprehensive legal information and practical solutions for {category.replace('_', ' ')} matters.
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text_content.strip())

        file_count += 1
        print(f"  [+] Created {filename}")

    return file_count

def main():
    """Convert all enhanced datasets to text files"""
    print("CONVERTING ENHANCED LEGAL DATASETS TO TEXT FILES")
    print("="*60)

    # Directories
    input_dir = Path("enhanced_legal_dataset")
    output_dir = Path("enhanced_legal_text")

    if not input_dir.exists():
        print(f"ERROR: Input directory not found: {input_dir}")
        return 1

    # Clean output directory
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    # Convert each dataset
    total_files = 0
    json_files = [f for f in input_dir.glob("*.json") if f.name != "master_index.json"]

    print(f"Found {len(json_files)} datasets to convert")

    for json_file in json_files:
        try:
            files_created = convert_dataset_to_text(json_file, output_dir)
            category = json_file.stem.replace('_dataset', '')
            print(f"[+] {category}: {files_created} files created")
            total_files += files_created
        except Exception as e:
            print(f"[!] Error converting {json_file.name}: {e}")

    print("\n" + "="*60)
    print("CONVERSION COMPLETE!")
    print("="*60)
    print(f"Total text files created: {total_files}")

    # Show directory structure
    print("\nCreated directory structure:")
    for category_dir in sorted(output_dir.iterdir()):
        if category_dir.is_dir():
            files = list(category_dir.glob("*.txt"))
            print(f"  {category_dir.name}/ ({len(files)} files)")

    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. The text files are ready for ingestion")
    print("2. Run: python ingest_all_documents.py")
    print("3. Or use: python comprehensive_legal_dataset_builder.py")
    print("4. Test with: python test_offense_solution_reference.py")
    print("="*60)

    return 0

if __name__ == "__main__":
    exit(main())
