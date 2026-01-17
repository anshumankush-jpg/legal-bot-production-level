"""URL validation and verification for court portals."""
import requests
import logging
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
from ..models import VerificationResult
from ..config import (
    REQUEST_DELAY, MAX_RETRIES, TIMEOUT, USER_AGENT,
    COURT_KEYWORDS, OFFICIAL_DOMAINS
)

logger = logging.getLogger(__name__)


class URLValidator:
    """Validates and verifies portal URLs."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
    
    def is_official_domain(self, url: str) -> bool:
        """Check if URL is from an official government domain."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return any(domain.endswith(official) for official in OFFICIAL_DOMAINS)
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {e}")
            return False
    
    def has_court_keywords(self, text: str) -> bool:
        """Check if text contains court-related keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in COURT_KEYWORDS)
    
    def verify_url(self, url: str) -> VerificationResult:
        """Verify a portal URL."""
        result = VerificationResult(url=url)
        
        # Check if official domain
        result.is_official = self.is_official_domain(url)
        
        # Try to fetch the page
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    timeout=TIMEOUT,
                    allow_redirects=True,
                    verify=False  # Some government sites have SSL issues
                )
                result.status_code = response.status_code
                
                if response.status_code == 200:
                    # Parse HTML to check for keywords
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.find('title')
                    result.title = title.get_text(strip=True) if title else ""
                    
                    # Check for keywords in title and page text
                    page_text = soup.get_text()[:5000]  # First 5000 chars
                    result.has_keywords = self.has_court_keywords(result.title) or \
                                         self.has_court_keywords(page_text)
                    
                    # Check for captcha or blocks
                    if "captcha" in page_text.lower() or "recaptcha" in response.text.lower():
                        result.is_blocked = True
                        result.notes = "Captcha detected"
                    
                    # Determine verification status and confidence
                    if result.is_official and result.has_keywords and not result.is_blocked:
                        result.verification_status = "verified"
                        result.confidence = 0.9
                    elif result.is_official and not result.is_blocked:
                        result.verification_status = "verified"
                        result.confidence = 0.7
                    elif result.has_keywords:
                        result.verification_status = "unverified"
                        result.confidence = 0.5
                    else:
                        result.verification_status = "unverified"
                        result.confidence = 0.3
                    
                    break
                
                elif response.status_code in [403, 429]:
                    result.is_blocked = True
                    result.verification_status = "broken"
                    result.notes = f"Access denied: {response.status_code}"
                    break
                
                else:
                    result.verification_status = "broken"
                    result.notes = f"HTTP {response.status_code}"
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(REQUEST_DELAY * (attempt + 1))
                    else:
                        break
            
            except requests.exceptions.Timeout:
                result.notes = "Request timeout"
                result.verification_status = "broken"
                if attempt == MAX_RETRIES - 1:
                    break
            
            except requests.exceptions.SSLError:
                result.notes = "SSL certificate error (common for some gov sites)"
                if result.is_official:
                    result.verification_status = "unverified"
                    result.confidence = 0.6
                else:
                    result.verification_status = "broken"
                break
            
            except Exception as e:
                logger.error(f"Error verifying {url}: {e}")
                result.notes = f"Error: {str(e)[:100]}"
                result.verification_status = "broken"
                if attempt == MAX_RETRIES - 1:
                    break
        
        # Rate limiting
        time.sleep(REQUEST_DELAY)
        
        logger.info(f"Verified {url}: {result.verification_status} (confidence: {result.confidence})")
        return result


def verify_portal(url: str) -> VerificationResult:
    """Helper function to verify a single portal URL."""
    validator = URLValidator()
    return validator.verify_url(url)
