"""
APIA Scholars spider for scraping scholarship data.

This spider scrapes scholarship information from APIAScholars.org,
focusing on scholarships for Asian Pacific Islander American students.
"""

import scrapy
from typing import Iterator
import re
from urllib.parse import urljoin

from .base import BaseScholarshipSpider
from items import ScholarshipItem


class APIAScholarsSpider(BaseScholarshipSpider):
    """Spider for scraping APIA Scholars scholarships"""
    
    name = 'apia'
    allowed_domains = ['apiascholars.org']
    
    start_urls = [
        'https://www.apiascholars.org/scholarships',
        'https://www.apiascholars.org/scholarships/undergraduate',
        'https://www.apiascholars.org/scholarships/graduate',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
    }
    
    def parse(self, response):
        """Parse APIA scholarship listing pages."""
        self.pages_visited += 1
        self.logger.info(f"Parsing APIA page: {response.url}")
        
        # Extract scholarship links
        scholarship_links = response.css('.scholarship-card a::attr(href)').getall() or \
                           response.css('a[href*="/scholarship"]::attr(href)').getall() or \
                           response.css('.program-card a::attr(href)').getall()
        
        for link in scholarship_links:
            if self.should_follow_link(link):
                url = self.clean_url(link, response.url)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_scholarship,
                    meta={'source_url': response.url}
                )
        
        # Follow pagination
        yield from self.parse_pagination(response)
    
    def parse_scholarship(self, response):
        """Parse individual APIA scholarship pages."""
        self.logger.info(f"Parsing APIA scholarship: {response.url}")
        
        # Extract title
        title = self.extract_with_selectors(response, 'title', [
            'h1.scholarship-title::text',
            'h1.page-title::text',
            'h1::text',
            '.program-name::text',
        ])
        
        if not title:
            self.logger.warning(f"No title found for APIA scholarship: {response.url}")
            return
        
        # Extract description
        description_parts = response.css('.scholarship-description p::text').getall() or \
                           response.css('.program-description p::text').getall() or \
                           response.css('.content p::text').getall()
        
        description = ' '.join([p.strip() for p in description_parts if p.strip()][:3])
        
        # Extract amount
        amount_text = response.css('.award-amount::text').get() or \
                     self.extract_with_selectors(response, 'amount')
        
        amount = self.extract_amount_from_text(amount_text) if amount_text else ""
        
        # Extract deadline
        deadline_text = response.css('.deadline::text').get() or \
                       response.css('.application-deadline::text').get() or \
                       self.extract_with_selectors(response, 'deadline')
        
        deadline = self.extract_deadline_from_text(deadline_text) if deadline_text else ""
        
        # Extract eligibility
        eligibility_parts = response.css('.eligibility-criteria li::text').getall() or \
                           response.css('.eligibility li::text').getall()
        
        if not eligibility_parts:
            eligibility_parts = [
                "Asian Pacific Islander American heritage",
                "US citizenship or legal residency",
                "Enrolled in accredited institution"
            ]
        
        eligibility = ' | '.join([e.strip() for e in eligibility_parts if e.strip()])
        
        # Extract requirements
        requirements_parts = response.css('.application-requirements li::text').getall() or \
                            response.css('.requirements li::text').getall()
        
        if not requirements_parts:
            requirements_parts = [
                "Complete online application",
                "Submit official transcripts",
                "Provide letters of recommendation",
                "Write personal essay"
            ]
        
        requirements = ' | '.join([r.strip() for r in requirements_parts if r.strip()])
        
        # Extract application URL
        application_url = response.css('a.apply-button::attr(href)').get() or \
                         response.css('a:contains("Apply")::attr(href)').get() or \
                         "https://www.apiascholars.org/apply"
        
        application_url = self.clean_url(application_url, response.url)
        
        # Provider
        provider = "APIA Scholars"
        
        # Determine category
        category = self.determine_category(title, description)
        
        # APIA-specific tags
        tags = ['Asian Pacific Islander', 'APIA', 'Minority']
        
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
        """Determine scholarship category for APIA scholarships."""
        text = f"{title} {description}".lower()
        
        categories = {
            'STEM': ['stem', 'engineering', 'computer', 'technology', 'science', 'math'],
            'Business': ['business', 'economics', 'finance', 'accounting', 'mba'],
            'Healthcare': ['medical', 'nursing', 'health', 'medicine', 'pharmacy'],
            'Education': ['education', 'teaching', 'teacher'],
            'Arts': ['art', 'music', 'creative', 'design', 'media'],
            'Law': ['law', 'legal', 'justice'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General'
