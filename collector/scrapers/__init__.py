"""Scrapers for collecting court and ticket portal data."""
from .base_scraper import BaseScraper
from .canada_scraper import CanadaScraper
from .usa_scraper import USAScraper

__all__ = ["BaseScraper", "CanadaScraper", "USAScraper"]
