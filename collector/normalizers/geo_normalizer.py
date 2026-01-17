"""Geographic name normalizer for cities, provinces, and states."""
import re
from typing import Dict, Optional


# Province/Territory name mappings
CANADA_PROVINCES = {
    "AB": "Alberta",
    "BC": "British Columbia",
    "MB": "Manitoba",
    "NB": "New Brunswick",
    "NL": "Newfoundland and Labrador",
    "NS": "Nova Scotia",
    "NT": "Northwest Territories",
    "NU": "Nunavut",
    "ON": "Ontario",
    "PE": "Prince Edward Island",
    "QC": "Quebec",
    "SK": "Saskatchewan",
    "YT": "Yukon"
}

# State name mappings
USA_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia"
}

# Reverse mappings
CANADA_PROVINCES_REVERSE = {v.lower(): k for k, v in CANADA_PROVINCES.items()}
USA_STATES_REVERSE = {v.lower(): k for k, v in USA_STATES.items()}


class GeoNormalizer:
    """Normalizes geographic names."""
    
    @staticmethod
    def normalize_province_state(name: str, country: str = "Canada") -> str:
        """Normalize province/state name to full name."""
        name = name.strip()
        name_upper = name.upper()
        name_lower = name.lower()
        
        if country == "Canada":
            # Check if it's already a code
            if name_upper in CANADA_PROVINCES:
                return CANADA_PROVINCES[name_upper]
            # Check if it's a full name
            if name_lower in CANADA_PROVINCES_REVERSE:
                return name.title()
            # Try to match partial
            for full_name in CANADA_PROVINCES.values():
                if full_name.lower() == name_lower:
                    return full_name
        
        elif country == "USA":
            # Check if it's already a code
            if name_upper in USA_STATES:
                return USA_STATES[name_upper]
            # Check if it's a full name
            if name_lower in USA_STATES_REVERSE:
                return name.title()
            # Try to match partial
            for full_name in USA_STATES.values():
                if full_name.lower() == name_lower:
                    return full_name
        
        # Return as-is if no match
        return name.strip()
    
    @staticmethod
    def normalize_city(name: str) -> str:
        """Normalize city name."""
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Common replacements
        replacements = {
            "St.": "Saint",
            "St ": "Saint ",
            "Ft.": "Fort",
            "Ft ": "Fort ",
            "Mt.": "Mount",
            "Mt ": "Mount "
        }
        
        for old, new in replacements.items():
            name = name.replace(old, new)
        
        # Title case
        return name.title()
    
    @staticmethod
    def get_province_code(province_name: str) -> Optional[str]:
        """Get province/territory code from full name."""
        province_lower = province_name.lower()
        return CANADA_PROVINCES_REVERSE.get(province_lower)
    
    @staticmethod
    def get_state_code(state_name: str) -> Optional[str]:
        """Get state code from full name."""
        state_lower = state_name.lower()
        return USA_STATES_REVERSE.get(state_lower)


def normalize_city(name: str) -> str:
    """Helper function to normalize city name."""
    return GeoNormalizer.normalize_city(name)


def normalize_province_state(name: str, country: str = "Canada") -> str:
    """Helper function to normalize province/state name."""
    return GeoNormalizer.normalize_province_state(name, country)
