"""
Scrapy items for scholarship scraping.

Defines the data structure for scholarships scraped from various sources.
"""

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags
import re
from datetime import datetime


def clean_text(value):
    """Clean and normalize text content."""
    if not value:
        return ''
    # Remove extra whitespace and newlines
    cleaned = re.sub(r'\s+', ' ', value.strip())
    return cleaned


def clean_amount(value):
    """Clean and normalize scholarship amount."""
    if not value:
        return ''
    # Extract monetary amounts and normalize format
    cleaned = re.sub(r'[^\d,$.-]', '', value)
    return cleaned


def parse_deadline(value):
    """Parse and normalize deadline dates."""
    if not value:
        return ''
    
    # Common date formats to try
    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%m-%d-%Y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%d %B %Y',
        '%d %b %Y'
    ]
    
    cleaned_value = clean_text(value)
    
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(cleaned_value, date_format)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # If no format matches, return the cleaned original
    return cleaned_value


class ScholarshipItem(scrapy.Item):
    """
    Main scholarship item that matches our React app's data model.
    
    This structure aligns with the Scholarship interface in 
    src/types/scholarship.ts to ensure seamless integration.
    """
    
    # Core fields (required)
    title = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    description = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=Join(' ')
    )
    
    amount = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_amount),
        output_processor=TakeFirst()
    )
    
    deadline = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text, parse_deadline),
        output_processor=TakeFirst()
    )
    
    eligibility = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=Join(' | ')
    )
    
    requirements = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=Join(' | ')
    )
    
    application_url = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    
    provider = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    category = scrapy.Field(
        input_processor=MapCompose(remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    
    # Metadata fields
    source = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    source_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    scraped_date = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    last_updated = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    # Additional categorization
    tags = scrapy.Field()
    
    # Status tracking
    is_active = scrapy.Field(
        output_processor=TakeFirst()
    )
    
    # Internal ID for deduplication
    item_id = scrapy.Field(
        output_processor=TakeFirst()
    )
