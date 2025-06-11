"""
Base spider class for scholarship scraping.

This module provides a common base class for all scholarship spiders
with shared functionality for data extraction and processing.
"""

import scrapy
from typing import Iterator, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from datetime import datetime
import re

from items import ScholarshipItem


class BaseScholarshipSpider(scrapy.Spider):
    """
    Base spider class with common functionality for scholarship scraping.
    """
    
    name = 'base_scholarship'
    
    # Common CSS selectors that might be reused
    COMMON_SELECTORS = {
        'title': [
            'h1::text',
            'h2::text',
            '.title::text',
            '.scholarship-title::text',
            '[class*="title"]::text',
        ],
        'description': [
            '.description::text',
            '.content::text',
            '.summary::text',
            'p::text',
            '[class*="description"]::text',
        ],
        'amount': [
            '.amount::text',
            '.value::text',
            '.award::text',
            '[class*="amount"]::text',
            '[class*="value"]::text',
        ],
        'deadline': [
            '.deadline::text',
            '.due-date::text',
            '.expires::text',
            '[class*="deadline"]::text',
            '[class*="due"]::text',
        ],
        'requirements': [
            '.requirements::text',
            '.eligibility::text',
            '.criteria::text',
            '[class*="requirement"]::text',
            '[class*="eligible"]::text',
        ],
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items_scraped = 0
        self.pages_visited = 0
        
    def start_requests(self) -> Iterator[scrapy.Request]:
        """Generate initial requests."""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'page_number': 1}
            )
    
    def parse(self, response) -> Iterator[scrapy.Request]:
        """Default parse method - should be overridden by subclasses."""
        self.logger.warning("Base parse method called - this should be overridden")
        return []
    
    def extract_with_selectors(self, response, field_name: str, selectors: list = None) -> str:
        """
        Extract text using multiple CSS selectors until one works.
        
        Args:
            response: Scrapy response object
            field_name: Name of the field being extracted
            selectors: List of CSS selectors to try
            
        Returns:
            Extracted text or empty string
        """
        if selectors is None:
            selectors = self.COMMON_SELECTORS.get(field_name, [])
            
        for selector in selectors:
            try:
                result = response.css(selector).get()
                if result and result.strip():
                    return result.strip()
            except Exception as e:
                self.logger.debug(f"Selector '{selector}' failed for {field_name}: {e}")
                continue
                
        self.logger.warning(f"No selector worked for {field_name} on {response.url}")
        return ""
    
    def extract_multiple_with_selectors(self, response, field_name: str, selectors: list = None) -> list:
        """
        Extract multiple text values using CSS selectors.
        
        Args:
            response: Scrapy response object
            field_name: Name of the field being extracted
            selectors: List of CSS selectors to try
            
        Returns:
            List of extracted text values
        """
        if selectors is None:
            selectors = self.COMMON_SELECTORS.get(field_name, [])
            
        for selector in selectors:
            try:
                results = response.css(selector).getall()
                if results:
                    return [r.strip() for r in results if r.strip()]
            except Exception as e:
                self.logger.debug(f"Selector '{selector}' failed for {field_name}: {e}")
                continue
                
        self.logger.warning(f"No selector worked for {field_name} on {response.url}")
        return []
    
    def clean_url(self, url: str, response_url: str) -> str:
        """Clean and normalize URLs."""
        if not url:
            return ""
        
        # Strip whitespace first
        url = url.strip()
            
        # Convert relative URLs to absolute
        if url.startswith('/'):
            return urljoin(response_url, url)
        elif not url.startswith('http'):
            return urljoin(response_url, url)
            
        return url
    
    def extract_amount_from_text(self, text: str) -> str:
        """
        Extract monetary amount from text using regex patterns.
        
        Args:
            text: Text that might contain monetary amounts
            
        Returns:
            Cleaned amount string
        """
        if not text:
            return ""
            
        # Common patterns for scholarship amounts
        patterns = [
            r'\$[\d,]+(?:\.\d{2})?',  # $1,000 or $1,000.00
            r'[\d,]+\s*dollars?',      # 1000 dollars
            r'up to \$[\d,]+',         # up to $1000
            r'maximum \$[\d,]+',       # maximum $1000
            r'[\d,]+\s*USD',          # 1000 USD
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group().strip()
                
        # If no specific pattern found, look for any number
        number_match = re.search(r'[\d,]+', text)
        if number_match:
            return f"${number_match.group()}"
            
        return text.strip()
    
    def extract_deadline_from_text(self, text: str) -> str:
        """
        Extract deadline date from text.
        
        Args:
            text: Text that might contain date information
            
        Returns:
            Cleaned date string
        """
        if not text:
            return ""
            
        # Common date patterns
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',        # MM/DD/YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',        # YYYY-MM-DD
            r'\w+ \d{1,2}, \d{4}',           # Month DD, YYYY
            r'\d{1,2} \w+ \d{4}',            # DD Month YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group().strip()
                
        return text.strip()
    
    def create_scholarship_item(self, response, **kwargs) -> ScholarshipItem:
        """
        Create a ScholarshipItem with common fields populated.
        
        Args:
            response: Scrapy response object
            **kwargs: Additional field values
            
        Returns:
            ScholarshipItem instance
        """
        item = ScholarshipItem()
        
        # Set source information
        item['source_url'] = response.url
        item['source'] = self.name
        
        # Populate with provided kwargs
        for key, value in kwargs.items():
            if key in item.fields:
                item[key] = value
                
        self.items_scraped += 1
        return item
    
    def should_follow_link(self, url: str) -> bool:
        """
        Determine if a link should be followed.
        
        Args:
            url: URL to check
            
        Returns:
            True if link should be followed
        """
        if not url:
            return False
            
        # Skip common non-content URLs
        skip_patterns = [
            r'\.pdf$',
            r'\.doc[x]?$',
            r'\.xls[x]?$',
            r'/login',
            r'/register',
            r'/contact',
            r'/privacy',
            r'/terms',
            r'javascript:',
            r'mailto:',
            r'tel:',
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
                
        return True
    
    def parse_pagination(self, response) -> Iterator[scrapy.Request]:
        """
        Extract pagination links. Should be overridden by subclasses if needed.
        
        Args:
            response: Scrapy response object
            
        Yields:
            Scrapy Request objects for pagination
        """
        # Common pagination selectors
        pagination_selectors = [
            'a[href*="page"]',
            '.pagination a',
            '.pager a',
            'a:contains("Next")',
            'a:contains(">")',
        ]
        
        for selector in pagination_selectors:
            links = response.css(selector)
            for link in links:
                href = link.css('::attr(href)').get()
                if href and self.should_follow_link(href):
                    url = self.clean_url(href, response.url)
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse,
                        meta={
                            'page_number': response.meta.get('page_number', 1) + 1
                        }
                    )
                    break  # Only follow first working pagination link
    
    def closed(self, reason):
        """Log statistics when spider closes."""
        self.logger.info(f"Spider closed: {reason}")
        self.logger.info(f"Pages visited: {self.pages_visited}")
        self.logger.info(f"Items scraped: {self.items_scraped}")
        
        # Log performance metrics
        if hasattr(self.crawler.stats, 'get_stats'):
            stats = self.crawler.stats.get_stats()
            self.logger.info(f"Total requests: {stats.get('downloader/request_count', 0)}")
            self.logger.info(f"Response codes: {stats.get('downloader/response_status_count', {})}")
            self.logger.info(f"Items passed through pipelines: {stats.get('item_scraped_count', 0)}")
            self.logger.info(f"Items dropped in pipelines: {stats.get('item_dropped_count', 0)}")
