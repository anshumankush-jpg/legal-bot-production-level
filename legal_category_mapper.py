#!/usr/bin/env python3
"""
Legal Category Mapper
Maps legal documents to standardized legal categories based on Canadian and US legal systems.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

# ============================================================================
# LEGAL CATEGORY DEFINITIONS
# ============================================================================

CANADA_CATEGORIES = {
    'constitutional': {
        'keywords': ['constitution', 'charter', 'rights', 'freedoms', 'constitutional'],
        'subcategories': ['constitutional_law', 'charter_rights', 'division_of_powers']
    },
    'criminal': {
        'keywords': ['criminal', 'criminal code', 'offence', 'offense', 'felony', 'misdemeanor', 
                     'assault', 'theft', 'fraud', 'dui', 'impaired', 'drug', 'homicide', 'robbery'],
        'subcategories': ['criminal_law', 'criminal_code', 'federal_criminal', 'provincial_criminal']
    },
    'administrative': {
        'keywords': ['administrative', 'tribunal', 'immigration', 'licensing', 'professional', 
                     'employment insurance', 'appeal', 'agency', 'regulatory'],
        'subcategories': ['administrative_law', 'immigration', 'licensing', 'tribunals']
    },
    'civil': {
        'keywords': ['civil', 'contract', 'tort', 'negligence', 'personal injury', 'property dispute',
                     'debt', 'collection', 'civil code', 'quebec civil'],
        'subcategories': ['contract_law', 'tort_law', 'property_disputes', 'debt_collections']
    },
    'family': {
        'keywords': ['family', 'divorce', 'custody', 'child support', 'spousal support', 
                     'marriage', 'adoption', 'separation'],
        'subcategories': ['divorce', 'custody', 'support', 'adoption']
    },
    'property': {
        'keywords': ['property', 'real estate', 'mortgage', 'landlord', 'tenant', 'eviction',
                     'zoning', 'land ownership'],
        'subcategories': ['real_estate', 'landlord_tenant', 'mortgages', 'zoning']
    },
    'regulatory_traffic': {
        'keywords': ['traffic', 'highway', 'motor vehicle', 'speeding', 'parking', 'ticket',
                     'demerit', 'provincial offences', 'bylaw', 'traffic act', 'highway traffic',
                     'regulatory', 'traffic violation'],
        'subcategories': ['traffic_law', 'provincial_offences', 'parking', 'speeding', 'dui_traffic']
    }
}

USA_CATEGORIES = {
    'constitutional': {
        'keywords': ['constitution', 'constitutional', 'bill of rights', 'due process', 
                     'equal protection', 'amendment'],
        'subcategories': ['constitutional_law', 'bill_of_rights', 'state_constitutions']
    },
    'criminal': {
        'keywords': ['criminal', 'felony', 'misdemeanor', 'offense', 'offence', 'assault',
                     'theft', 'fraud', 'homicide', 'robbery', 'drug', 'firearms'],
        'subcategories': ['federal_criminal', 'state_criminal', 'felonies', 'misdemeanors']
    },
    'civil': {
        'keywords': ['civil', 'contract', 'tort', 'negligence', 'personal injury', 'business dispute',
                     'consumer protection', 'civil code'],
        'subcategories': ['contracts', 'torts', 'business_disputes', 'consumer_protection']
    },
    'administrative': {
        'keywords': ['administrative', 'agency', 'immigration', 'social security', 'environmental',
                     'regulatory', 'federal agency', 'state agency'],
        'subcategories': ['immigration', 'social_security', 'environmental', 'agencies']
    },
    'family': {
        'keywords': ['family', 'divorce', 'custody', 'child support', 'spousal support',
                     'marriage', 'adoption'],
        'subcategories': ['divorce', 'custody', 'support', 'adoption']
    },
    'property': {
        'keywords': ['property', 'real estate', 'zoning', 'land ownership', 'eviction',
                     'mortgage', 'landlord', 'tenant'],
        'subcategories': ['real_estate', 'zoning', 'landlord_tenant', 'evictions']
    },
    'regulatory_traffic': {
        'keywords': ['traffic', 'highway', 'motor vehicle', 'speeding', 'parking', 'ticket',
                     'traffic violation', 'traffic court', 'municipal court', 'dui'],
        'subcategories': ['traffic_law', 'traffic_tickets', 'speeding', 'parking', 'dui_traffic']
    },
    'tax': {
        'keywords': ['tax', 'irs', 'income tax', 'state tax', 'tax code', 'taxation'],
        'subcategories': ['federal_tax', 'state_tax', 'irs_rules']
    },
    'employment': {
        'keywords': ['employment', 'labor', 'labour', 'worker rights', 'discrimination',
                     'union', 'employment law', 'labor law'],
        'subcategories': ['worker_rights', 'discrimination', 'unions', 'employment_law']
    }
}

# Priority order for your app (high to low)
APP_PRIORITY_CATEGORIES = [
    'regulatory_traffic',  # Core use case
    'administrative',      # Appeals, tribunals
    'criminal',           # DUI / hybrid cases (light)
    'civil',              # Small disputes
    'constitutional',     # Rights issues
    'property',           # Real estate disputes
    'family',             # Not needed for now
    'tax',                # Not needed for now
    'employment'          # Not needed for now
]


# ============================================================================
# CATEGORY MAPPING FUNCTIONS
# ============================================================================

def detect_jurisdiction(file_path: Path) -> str:
    """Detect if document is from Canada or USA."""
    path_str = str(file_path).lower()
    
    # Canada indicators
    canada_keywords = ['canada', 'canadian', 'ontario', 'quebec', 'british columbia', 'alberta',
                       'manitoba', 'saskatchewan', 'nova scotia', 'new brunswick', 
                       'newfoundland', 'pei', 'prince edward', 'yukon', 'northwest territories',
                       'nunavut', 'provincial', 'criminal code of canada']
    
    # USA indicators
    usa_keywords = ['usa', 'united states', 'us state', 'federal', 'california', 'texas', 'new york',
                    'florida', 'illinois', 'pennsylvania', 'ohio', 'georgia', 'north carolina',
                    'michigan', 'new jersey', 'virginia', 'washington', 'arizona', 'massachusetts',
                    'tennessee', 'indiana', 'missouri', 'maryland', 'wisconsin', 'colorado',
                    'minnesota', 'south carolina', 'alabama', 'louisiana', 'kentucky', 'oregon',
                    'oklahoma', 'connecticut', 'utah', 'iowa', 'nevada', 'arkansas', 'mississippi',
                    'kansas', 'new mexico', 'nebraska', 'west virginia', 'idaho', 'hawaii',
                    'new hampshire', 'maine', 'montana', 'rhode island', 'delaware', 'south dakota',
                    'north dakota', 'alaska', 'vermont', 'wyoming', 'district of columbia']
    
    for keyword in canada_keywords:
        if keyword in path_str:
            return 'canada'
    
    for keyword in usa_keywords:
        if keyword in path_str:
            return 'usa'
    
    # Check filename
    filename = file_path.name.lower()
    if any(kw in filename for kw in canada_keywords):
        return 'canada'
    if any(kw in filename for kw in usa_keywords):
        return 'usa'
    
    return 'unknown'


def classify_legal_category(file_path: Path, jurisdiction: Optional[str] = None) -> Tuple[str, str, List[str]]:
    """
    Classify a legal document into a legal category.
    
    Returns:
        (primary_category, subcategory, tags)
    """
    if jurisdiction is None:
        jurisdiction = detect_jurisdiction(file_path)
    
    path_str = str(file_path).lower()
    filename = file_path.name.lower()
    full_text = f"{path_str} {filename}"
    
    # Select category set based on jurisdiction
    categories = CANADA_CATEGORIES if jurisdiction == 'canada' else USA_CATEGORIES
    
    # Score each category
    category_scores = {}
    
    for category, config in categories.items():
        score = 0
        matched_keywords = []
        
        for keyword in config['keywords']:
            # Exact match gets higher score
            if keyword in full_text:
                score += 2
                matched_keywords.append(keyword)
            # Partial match
            elif keyword.replace(' ', '') in full_text.replace(' ', ''):
                score += 1
                matched_keywords.append(keyword)
        
        if score > 0:
            category_scores[category] = {
                'score': score,
                'keywords': matched_keywords,
                'subcategories': config['subcategories']
            }
    
    # Special handling for case law
    if 'case' in full_text or 'precedent' in full_text or 'court decision' in full_text:
        # Determine which category the case law belongs to
        if category_scores:
            # Use the highest scoring category
            primary_category = max(category_scores.items(), key=lambda x: x[1]['score'])[0]
            subcategory = 'case_law'
            tags = ['case_law', primary_category, jurisdiction]
        else:
            primary_category = 'case_law'
            subcategory = 'case_law'
            tags = ['case_law', jurisdiction]
        
        return primary_category, subcategory, tags
    
    # If no matches, try to infer from directory structure
    if not category_scores:
        if 'traffic' in path_str or 'highway' in path_str:
            return 'regulatory_traffic', 'traffic_law', ['traffic', jurisdiction]
        elif 'criminal' in path_str:
            return 'criminal', 'criminal_law', ['criminal', jurisdiction]
        elif 'case' in path_str:
            return 'case_law', 'case_law', ['case_law', jurisdiction]
        else:
            return 'general', 'general', ['general', jurisdiction]
    
    # Get highest scoring category
    primary_category = max(category_scores.items(), key=lambda x: x[1]['score'])[0]
    category_info = category_scores[primary_category]
    
    # Determine subcategory (use first subcategory for now, or case-specific logic)
    subcategory = category_info['subcategories'][0] if category_info['subcategories'] else primary_category
    
    # Build tags
    tags = [primary_category, subcategory, jurisdiction]
    tags.extend(category_info['keywords'][:3])  # Add top matched keywords as tags
    
    return primary_category, subcategory, tags


def get_category_priority(category: str) -> int:
    """Get priority score for a category (lower = higher priority for your app)."""
    try:
        return APP_PRIORITY_CATEGORIES.index(category)
    except ValueError:
        return 999  # Unknown categories get lowest priority


def get_category_display_name(category: str) -> str:
    """Get human-readable display name for category."""
    display_names = {
        'constitutional': 'Constitutional Law',
        'criminal': 'Criminal Law',
        'administrative': 'Administrative Law',
        'civil': 'Civil Law',
        'family': 'Family Law',
        'property': 'Property & Real Estate Law',
        'regulatory_traffic': 'Regulatory / Traffic Law',
        'tax': 'Tax Law',
        'employment': 'Employment & Labor Law',
        'case_law': 'Case Law',
        'general': 'General Law'
    }
    return display_names.get(category, category.replace('_', ' ').title())


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def categorize_document_batch(file_paths: List[Path]) -> Dict[str, Dict]:
    """
    Categorize a batch of documents.
    
    Returns:
        Dictionary mapping file paths to category information
    """
    results = {}
    
    for file_path in file_paths:
        jurisdiction = detect_jurisdiction(file_path)
        primary_category, subcategory, tags = classify_legal_category(file_path, jurisdiction)
        priority = get_category_priority(primary_category)
        
        results[str(file_path)] = {
            'file_path': str(file_path),
            'jurisdiction': jurisdiction,
            'primary_category': primary_category,
            'category_display': get_category_display_name(primary_category),
            'subcategory': subcategory,
            'tags': tags,
            'priority': priority,
            'is_high_priority': priority < 4  # Top 4 categories
        }
    
    return results


if __name__ == '__main__':
    # Example usage
    test_files = [
        Path('canada_traffic_acts/ontario_highway_traffic_act.pdf'),
        Path('usa_criminal_law/federal_criminal_code.pdf'),
        Path('canada_case_law/supreme_court_decision.pdf'),
    ]
    
    results = categorize_document_batch(test_files)
    
    for file_path, info in results.items():
        print(f"\n{Path(file_path).name}")
        print(f"  Jurisdiction: {info['jurisdiction']}")
        print(f"  Category: {info['category_display']}")
        print(f"  Subcategory: {info['subcategory']}")
        print(f"  Priority: {info['priority']} ({'HIGH' if info['is_high_priority'] else 'LOW'})")
        print(f"  Tags: {', '.join(info['tags'])}")
