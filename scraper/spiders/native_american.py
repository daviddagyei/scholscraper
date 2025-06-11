"""
Native American scholarship spider for scraping scholarship data.

This spider scrapes scholarship information from multiple Native American
scholarship sources including AISES, NAJA, and other tribal organizations.
"""

import scrapy
from typing import Iterator
import re
from urllib.parse import urljoin

from .base import BaseScholarshipSpider
from items import ScholarshipItem


class NativeAmericanSpider(BaseScholarshipSpider):
    """Spider for scraping Native American scholarships"""
    
    name = 'native_american'
    allowed_domains = ['aises.org', 'naja.com', 'collegefund.org', 'aianta.org']
    
    start_urls = [
        'https://www.aises.org/scholarships',
        'https://www.naja.com/scholarships',
        'https://collegefund.org/students/scholarships/',
        'https://www.aianta.org/scholarships/',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 4,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
    }
    
    def parse(self, response):
        """Parse Native American scholarship listing pages."""
        self.pages_visited += 1
        self.logger.info(f"Parsing Native American scholarship page: {response.url}")
        
        # Different selectors for different sites
        scholarship_selectors = [
            '.scholarship-item a::attr(href)',
            '.program-card a::attr(href)',
            'a[href*="/scholarship"]::attr(href)',
            '.scholarship-link::attr(href)',
            '.award-card a::attr(href)',
        ]
        
        scholarship_links = []
        for selector in scholarship_selectors:
            links = response.css(selector).getall()
            if links:
                scholarship_links = links
                break
        
        for link in scholarship_links:
            if self.should_follow_link(link):
                url = self.clean_url(link, response.url)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_scholarship,
                    meta={'source_url': response.url, 'source_domain': response.url.split('/')[2]}
                )
        
        # Follow pagination
        yield from self.parse_pagination(response)
    
    def parse_scholarship(self, response):
        """Parse individual Native American scholarship pages."""
        source_domain = response.meta.get('source_domain', response.url.split('/')[2])
        self.logger.info(f"Parsing Native American scholarship from {source_domain}: {response.url}")
        
        # Extract title
        title = self.extract_with_selectors(response, 'title', [
            'h1.scholarship-title::text',
            'h1.program-title::text',
            'h1.page-title::text',
            'h1::text',
            '.award-title::text',
        ])
        
        if not title:
            self.logger.warning(f"No title found for scholarship: {response.url}")
            return
        
        # Extract description based on source
        description = self.extract_description_by_source(response, source_domain)
        
        # Extract amount
        amount_text = self.extract_amount_by_source(response, source_domain)
        amount = self.extract_amount_from_text(amount_text) if amount_text else ""
        
        # Extract deadline
        deadline_text = self.extract_deadline_by_source(response, source_domain)
        deadline = self.extract_deadline_from_text(deadline_text) if deadline_text else ""
        
        # Extract eligibility
        eligibility = self.extract_eligibility_by_source(response, source_domain)
        
        # Extract requirements
        requirements = self.extract_requirements_by_source(response, source_domain)
        
        # Extract application URL
        application_url = self.extract_application_url_by_source(response, source_domain)
        
        # Determine provider based on domain
        provider = self.get_provider_by_domain(source_domain)
        
        # Determine category
        category = self.determine_category(title, description)
        
        # Native American-specific tags
        tags = ['Native American', 'Indigenous', 'Tribal', 'Minority']
        
        # Add source-specific tags
        if 'aises' in source_domain:
            tags.append('STEM')
        elif 'naja' in source_domain:
            tags.append('Journalism')
        
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
    
    def extract_description_by_source(self, response, domain: str) -> str:
        """Extract description based on source website structure."""
        if 'aises' in domain:
            parts = response.css('.scholarship-description p::text').getall() or \
                   response.css('.program-content p::text').getall()
        elif 'naja' in domain:
            parts = response.css('.entry-content p::text').getall() or \
                   response.css('.content p::text').getall()
        elif 'collegefund' in domain:
            parts = response.css('.program-description p::text').getall() or \
                   response.css('.field-body p::text').getall()
        else:
            parts = response.css('.description p::text').getall() or \
                   response.css('.content p::text').getall()
        
        return ' '.join([p.strip() for p in parts if p.strip()][:2])
    
    def extract_amount_by_source(self, response, domain: str) -> str:
        """Extract amount based on source website structure."""
        selectors = [
            '.award-amount::text',
            '.scholarship-amount::text',
            '.amount::text',
            '*:contains("$")::text',
        ]
        
        for selector in selectors:
            amount = response.css(selector).get()
            if amount and '$' in amount:
                return amount
        
        return ""
    
    def extract_deadline_by_source(self, response, domain: str) -> str:
        """Extract deadline based on source website structure."""
        selectors = [
            '.deadline::text',
            '.application-deadline::text',
            '.due-date::text',
            '*:contains("deadline")::text',
            '*:contains("due")::text',
        ]
        
        for selector in selectors:
            deadline = response.css(selector).get()
            if deadline:
                return deadline
        
        return ""
    
    def extract_eligibility_by_source(self, response, domain: str) -> str:
        """Extract eligibility based on source website structure."""
        eligibility_parts = response.css('.eligibility li::text').getall() or \
                           response.css('.requirements li::text').getall() or \
                           response.css('.criteria li::text').getall()
        
        if not eligibility_parts:
            # Default Native American eligibility
            eligibility_parts = [
                "Native American/Alaska Native heritage",
                "Tribal enrollment or documentation required",
                "US citizenship or legal residency"
            ]
        
        return ' | '.join([e.strip() for e in eligibility_parts if e.strip()])
    
    def extract_requirements_by_source(self, response, domain: str) -> str:
        """Extract requirements based on source website structure."""
        requirements_parts = response.css('.application-requirements li::text').getall() or \
                            response.css('.how-to-apply li::text').getall() or \
                            response.css('.submit li::text').getall()
        
        if not requirements_parts:
            requirements_parts = [
                "Complete online application",
                "Submit official transcripts",
                "Provide tribal enrollment documentation",
                "Write personal essay",
                "Submit letters of recommendation"
            ]
        
        return ' | '.join([r.strip() for r in requirements_parts if r.strip()])
    
    def extract_application_url_by_source(self, response, domain: str) -> str:
        """Extract application URL based on source website structure."""
        application_url = response.css('a.apply-button::attr(href)').get() or \
                         response.css('a:contains("Apply")::attr(href)').get() or \
                         response.css('.application-link a::attr(href)').get()
        
        if application_url:
            return self.clean_url(application_url, response.url)
        
        # Default application URLs by domain
        defaults = {
            'aises.org': 'https://www.aises.org/scholarships/apply',
            'naja.com': 'https://www.naja.com/apply',
            'collegefund.org': 'https://collegefund.org/students/apply/',
            'aianta.org': 'https://www.aianta.org/apply/',
        }
        
        for domain_key, default_url in defaults.items():
            if domain_key in domain:
                return default_url
        
        return response.url
    
    def get_provider_by_domain(self, domain: str) -> str:
        """Get provider name based on domain."""
        providers = {
            'aises.org': 'American Indian Science and Engineering Society (AISES)',
            'naja.com': 'Native American Journalists Association (NAJA)',
            'collegefund.org': 'American Indian College Fund',
            'aianta.org': 'American Indian Alaska Native Tourism Association (AIANTA)',
        }
        
        for domain_key, provider in providers.items():
            if domain_key in domain:
                return provider
        
        return 'Native American Organization'
    
    def determine_category(self, title: str, description: str) -> str:
        """Determine scholarship category for Native American scholarships."""
        text = f"{title} {description}".lower()
        
        categories = {
            'STEM': ['stem', 'engineering', 'computer', 'technology', 'science', 'math', 'environmental'],
            'Business': ['business', 'economics', 'finance', 'accounting', 'entrepreneurship'],
            'Healthcare': ['medical', 'nursing', 'health', 'medicine', 'public health'],
            'Education': ['education', 'teaching', 'teacher', 'childhood'],
            'Arts': ['art', 'music', 'creative', 'design', 'literature', 'cultural arts'],
            'Law': ['law', 'legal', 'justice', 'tribal law'],
            'Journalism': ['journalism', 'media', 'communication', 'broadcasting'],
            'Environmental': ['environmental', 'natural resources', 'forestry', 'wildlife'],
            'Social Work': ['social work', 'community', 'tribal services'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General'
