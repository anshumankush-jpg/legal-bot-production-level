"""Configuration for the collector system."""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
SEEDS_DIR = BASE_DIR / "seeds"
OUTPUT_DIR = BASE_DIR / "output"
OVERRIDES_DIR = BASE_DIR / "overrides"

# Ensure directories exist
SEEDS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
OVERRIDES_DIR.mkdir(exist_ok=True)

# Rate limiting
REQUEST_DELAY = 1.0  # seconds between requests
MAX_RETRIES = 3
TIMEOUT = 10  # seconds

# Keywords for portal verification
COURT_KEYWORDS = [
    "court", "ticket", "case", "offence", "violation", "citation",
    "municipal", "traffic", "parking", "provincial", "superior",
    "justice", "judiciary", "tribunal", "lookup", "search", "pay"
]

# Official domain patterns
OFFICIAL_DOMAINS = [
    ".gov",  # USA government
    ".gc.ca",  # Canada government
    ".on.ca",  # Ontario
    ".qc.ca",  # Quebec
    ".bc.ca",  # British Columbia
    ".ab.ca",  # Alberta
    ".sk.ca",  # Saskatchewan
    ".mb.ca",  # Manitoba
    ".ns.ca",  # Nova Scotia
    ".nb.ca",  # New Brunswick
    ".pe.ca",  # Prince Edward Island
    ".nl.ca",  # Newfoundland and Labrador
    ".nt.ca",  # Northwest Territories
    ".nu.ca",  # Nunavut
    ".yk.ca",  # Yukon
]

# User agent for requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
