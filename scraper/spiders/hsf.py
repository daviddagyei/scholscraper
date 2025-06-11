"""
Hispanic Scholarship Fund (HSF) spider for scraping scholarship data.

This spider scrapes scholarship information from HSF.net,
focusing on scholarships for Hispanic/Latino students.
"""

import scrapy
from typing import Iterator
import re
from urllib.parse import urljoin

from .base import BaseScholarshipSpider
from items import ScholarshipItem


class HSFSpider(BaseScholarshipSpider):
    """Spider for scraping HSF.net scholarships"""
    
    name = 'hsf'
    allowed_domains = ['hsf.net']
    
    start_urls = [
        'https://www.hsf.net/scholarship',
        'https://www.hsf.net/scholarship/high-school',
        'https://www.hsf.net/scholarship/undergraduate',
        'https://www.hsf.net/scholarship/graduate',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
    }
    
    def parse(self, response):
        """Parse HSF scholarship listing pages."""
        self.pages_visited += 1
        self.logger.info(f"Parsing HSF page: {response.url}")
        
        # Extract scholarship links
        scholarship_links = response.css('.scholarship-item a::attr(href)').getall() or \
                           response.css('a[href*="/scholarship/"]::attr(href)').getall() or \
                           response.css('.program-link a::attr(href)').getall()
        
        for link in scholarship_links:
            if self.should_follow_link(link) and '/scholarship/' in link and link.count('/') > 3:
                url = self.clean_url(link, response.url)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_scholarship,
                    meta={'source_url': response.url}
                )
        
        # Handle scholarship cards that might need JavaScript
        scholarship_cards = response.css('.scholarship-card')
        for card in scholarship_cards:
            title = card.css('.scholarship-title::text').get()
            if title:
                # Try to extract data directly from the card
                yield self.parse_scholarship_card(card, response)
        
        # Follow pagination
        yield from self.parse_pagination(response)
    
    def parse_scholarship_card(self, card_selector, response):
        """Parse scholarship data from card view if detail page not available."""
        title = card_selector.css('.scholarship-title::text').get() or \
                card_selector.css('h3::text').get() or \
                card_selector.css('h4::text').get()
        
        if not title:
            return None
        
        description = card_selector.css('.scholarship-description::text').get() or \
                     card_selector.css('.description::text').get() or \
                     ""
        
        amount = card_selector.css('.amount::text').get() or ""
        deadline = card_selector.css('.deadline::text').get() or ""
        
        # Extract application link
        application_url = card_selector.css('a::attr(href)').get()
        if application_url:
            application_url = self.clean_url(application_url, response.url)
        else:
            application_url = response.url
        
        provider = "Hispanic Scholarship Fund (HSF)"
        category = self.determine_category(title, description)
        
        tags = ['Hispanic', 'Latino', 'Minority']
        
        item = self.create_scholarship_item(
            response,
            title=title.strip(),
            description=description.strip(),
            amount=self.extract_amount_from_text(amount),
            deadline=self.extract_deadline_from_text(deadline),
            eligibility="Hispanic/Latino heritage required",
            requirements="Varies by scholarship",
            application_url=application_url,
            provider=provider,
            category=category,
            tags=tags
        )
        
        return item
    
    def parse_scholarship(self, response):
        """Parse individual HSF scholarship pages."""
        self.logger.info(f"Parsing HSF scholarship: {response.url}")
        
        # Extract title
        title = self.extract_with_selectors(response, 'title', [
            'h1.scholarship-title::text',
            'h1.page-title::text',
            'h1::text',
            '.program-title::text',
        ])
        
        if not title:
            self.logger.warning(f"No title found for HSF scholarship: {response.url}")
            return
        
        # Extract description
        description_selectors = [
            '.scholarship-description *::text',
            '.program-description *::text',
            '.content-area *::text',
            '.description *::text',
        ]
        
        description_parts = []
        for selector in description_selectors:
            parts = response.css(selector).getall()
            if parts:
                description_parts = [p.strip() for p in parts if p.strip() and len(p.strip()) > 20]
                break
        
        description = ' '.join(description_parts[:2])  # Limit to first 2 substantial paragraphs
        
        # Extract amount
        amount_text = response.css('.award-amount::text').get() or \
                     response.css('.scholarship-amount::text').get() or \
                     self.extract_with_selectors(response, 'amount')
        
        amount = self.extract_amount_from_text(amount_text) if amount_text else ""
        
        # Extract deadline
        deadline_text = response.css('.deadline::text').get() or \
                       response.css('.application-deadline::text').get() or \
                       self.extract_with_selectors(response, 'deadline')
        
        deadline = self.extract_deadline_from_text(deadline_text) if deadline_text else ""
        
        # Extract eligibility
        eligibility_parts = response.css('.eligibility-requirements li::text').getall() or \
                           response.css('.eligibility li::text').getall() or \
                           response.css('.requirements li::text').getall()
        
        # Default HSF eligibility if not found
        if not eligibility_parts:
            eligibility_parts = ["Hispanic/Latino heritage", "US citizenship or legal residency", "Minimum GPA requirement"]
        
        eligibility = ' | '.join([e.strip() for e in eligibility_parts if e.strip()])
        
        # Extract requirements
        requirements_parts = response.css('.application-requirements li::text').getall() or \
                            response.css('.how-to-apply li::text').getall()
        
        if not requirements_parts:
            requirements_parts = ["Complete online application", "Submit transcripts", "Provide letters of recommendation"]
        
        requirements = ' | '.join([r.strip() for r in requirements_parts if r.strip()])
        
        # Extract application URL
        application_url = response.css('a.apply-now::attr(href)').get() or \
                         response.css('a:contains("Apply")::attr(href)').get() or \
                         response.css('.application-link a::attr(href)').get() or \
                         "https://www.hsf.net/apply"
        
        application_url = self.clean_url(application_url, response.url)
        
        # Provider is always HSF
        provider = "Hispanic Scholarship Fund (HSF)"
        
        # Determine category
        category = self.determine_category(title, description)
        
        # HSF-specific tags
        tags = response.css('.program-tags a::text').getall() or \
               ['Hispanic', 'Latino', 'Minority']
        
        # Ensure Hispanic/Latino tags are present
        if 'Hispanic' not in tags:
            tags.append('Hispanic')
        if 'Latino' not in tags:
            tags.append('Latino')
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
        """Determine scholarship category for HSF scholarships."""
        text = f"{title} {description}".lower()
        
        # HSF-specific category mapping
        categories = {
            'STEM': ['stem', 'engineering', 'computer', 'technology', 'science', 'math', 
                    'programming', 'coding', 'data', 'cybersecurity', 'robotics'],
            'Business': ['business', 'economics', 'finance', 'accounting', 'mba', 
                        'marketing', 'management', 'entrepreneurship', 'commerce'],
            'Healthcare': ['medical', 'nursing', 'health', 'medicine', 'pharmacy', 
                          'dental', 'healthcare', 'public health', 'veterinary'],
            'Education': ['education', 'teaching', 'teacher', 'pedagogy', 'childhood', 'bilingual'],
            'Arts': ['art', 'music', 'theater', 'creative', 'design', 'literature', 
                    'humanities', 'communication', 'media', 'journalism'],
            'Law': ['law', 'legal', 'justice', 'pre-law', 'paralegal', 'criminal justice'],
            'Social Work': ['social work', 'community', 'nonprofit', 'public service', 'psychology'],
            'Agriculture': ['agriculture', 'farming', 'agricultural', 'food science'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General'
