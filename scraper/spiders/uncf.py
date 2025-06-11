"""
UNCF (United Negro College Fund) spider for scraping scholarship data.

This spider scrapes scholarship information from UNCF.org,
focusing on scholarships for African American students.
"""

import scrapy
from typing import Iterator
import re
from urllib.parse import urljoin

from .base import BaseScholarshipSpider
from items import ScholarshipItem


class UNCFSpider(BaseScholarshipSpider):
    """Spider for scraping UNCF.org scholarships"""
    
    name = 'uncf'
    allowed_domains = ['uncf.org']
    
    start_urls = [
        'https://uncf.org/scholarships',
        'https://uncf.org/scholarships/undergraduate-scholarships',
        'https://uncf.org/scholarships/graduate-scholarships',
        'https://uncf.org/scholarships/high-school-scholarships',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 4,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
    }
    
    def parse(self, response):
        """Parse main scholarship listing pages."""
        self.pages_visited += 1
        self.logger.info(f"Parsing UNCF page: {response.url}")
        
        # Extract scholarship card links
        scholarship_links = response.css('.scholarship-card a::attr(href)').getall() or \
                           response.css('a[href*="/scholarship/"]::attr(href)').getall() or \
                           response.css('.program-card a::attr(href)').getall()
        
        for link in scholarship_links:
            if self.should_follow_link(link):
                url = self.clean_url(link, response.url)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_scholarship,
                    meta={'source_url': response.url}
                )
        
        # Handle AJAX-loaded content if present
        ajax_links = response.css('[data-ajax-url]::attr(data-ajax-url)').getall()
        for ajax_url in ajax_links[:5]:  # Limit AJAX requests
            if ajax_url:
                url = self.clean_url(ajax_url, response.url)
                yield scrapy.Request(url=url, callback=self.parse)
        
        # Follow pagination
        yield from self.parse_pagination(response)
    
    def parse_scholarship(self, response):
        """Parse individual UNCF scholarship pages."""
        self.logger.info(f"Parsing UNCF scholarship: {response.url}")
        
        # Extract title
        title = self.extract_with_selectors(response, 'title', [
            'h1.page-title::text',
            'h1.program-title::text',
            'h1::text',
            '.scholarship-title::text',
        ])
        
        if not title:
            self.logger.warning(f"No title found for UNCF scholarship: {response.url}")
            return
        
        # Extract description
        description_selectors = [
            '.program-description *::text',
            '.scholarship-description *::text',
            '.content-body *::text',
            '.field-body *::text',
        ]
        
        description_parts = []
        for selector in description_selectors:
            parts = response.css(selector).getall()
            if parts:
                description_parts = [p.strip() for p in parts if p.strip()]
                break
        
        description = ' '.join(description_parts[:3])  # Limit to first 3 paragraphs
        
        # Extract amount
        amount_selectors = [
            '.award-amount::text',
            '.program-amount::text',
            '*:contains("$")::text',
            '.field-award-amount .field-item::text',
        ]
        
        amount_text = ""
        for selector in amount_selectors:
            amount_text = response.css(selector).get()
            if amount_text and '$' in amount_text:
                break
        
        amount = self.extract_amount_from_text(amount_text) if amount_text else ""
        
        # Extract deadline
        deadline_selectors = [
            '.deadline-date::text',
            '.application-deadline::text',
            '.field-deadline .field-item::text',
            '*:contains("deadline")::text',
        ]
        
        deadline_text = ""
        for selector in deadline_selectors:
            deadline_text = response.css(selector).get()
            if deadline_text:
                break
        
        deadline = self.extract_deadline_from_text(deadline_text) if deadline_text else ""
        
        # Extract eligibility
        eligibility_selectors = [
            '.eligibility-criteria li::text',
            '.program-eligibility li::text',
            '.field-eligibility li::text',
            '.requirements li::text',
        ]
        
        eligibility_parts = []
        for selector in eligibility_selectors:
            parts = response.css(selector).getall()
            if parts:
                eligibility_parts = [e.strip() for e in parts if e.strip()]
                break
        
        eligibility = ' | '.join(eligibility_parts)
        
        # Extract requirements
        requirements_selectors = [
            '.application-requirements li::text',
            '.program-requirements li::text',
            '.field-requirements li::text',
            '.how-to-apply li::text',
        ]
        
        requirements_parts = []
        for selector in requirements_selectors:
            parts = response.css(selector).getall()
            if parts:
                requirements_parts = [r.strip() for r in parts if r.strip()]
                break
        
        requirements = ' | '.join(requirements_parts)
        
        # Extract application URL
        application_url = response.css('a.apply-button::attr(href)').get() or \
                         response.css('a:contains("Apply")::attr(href)').get() or \
                         response.css('.application-link a::attr(href)').get() or \
                         response.url
        
        application_url = self.clean_url(application_url, response.url)
        
        # Provider is always UNCF
        provider = "United Negro College Fund (UNCF)"
        
        # Determine category
        category = self.determine_category(title, description)
        
        # Extract tags/keywords
        tags = response.css('.program-tags a::text').getall() or \
               response.css('.field-tags a::text').getall() or \
               ['African American', 'Minority']
        
        # Add UNCF-specific tags
        if 'African American' not in tags:
            tags.append('African American')
        if 'Minority' not in tags:
            tags.append('Minority')
        
        # Create scholarship item
        item = self.create_scholarship_item(
            response,
            title=title,
            description=description,
            amount=amount,
            deadline=deadline,
            eligibility=eligibility,
            requirements=requirements,
            application_url=application_url,
            provider=provider,
            category=category,
            tags=tags
        )
        
        yield item
    
    def determine_category(self, title: str, description: str) -> str:
        """Determine scholarship category for UNCF scholarships."""
        text = f"{title} {description}".lower()
        
        # UNCF-specific category mapping
        categories = {
            'STEM': ['stem', 'engineering', 'computer', 'technology', 'science', 'math', 
                    'programming', 'coding', 'data', 'cybersecurity'],
            'Business': ['business', 'economics', 'finance', 'accounting', 'mba', 
                        'marketing', 'management', 'entrepreneurship'],
            'Healthcare': ['medical', 'nursing', 'health', 'medicine', 'pharmacy', 
                          'dental', 'healthcare', 'public health'],
            'Education': ['education', 'teaching', 'teacher', 'pedagogy', 'childhood'],
            'Arts': ['art', 'music', 'theater', 'creative', 'design', 'literature', 
                    'humanities', 'communication', 'media'],
            'Law': ['law', 'legal', 'justice', 'pre-law', 'paralegal'],
            'Social Work': ['social work', 'community', 'nonprofit', 'public service'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General'
