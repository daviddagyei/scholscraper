"""
CollegeScholarships.org spider for scraping scholarship data.

This spider scrapes scholarship information from CollegeScholarships.org,
one of the largest scholarship databases online.
"""

import scrapy
from typing import Iterator
import re
from urllib.parse import urljoin

from .base import BaseScholarshipSpider
from items import ScholarshipItem


class CollegeScholarshipsSpider(BaseScholarshipSpider):
    """Spider for scraping CollegeScholarships.org"""
    
    name = 'collegescholarships'
    allowed_domains = ['collegescholarships.org']
    
    start_urls = [
        'https://www.collegescholarships.org/scholarships/',
        'https://www.collegescholarships.org/scholarships/state/',
        'https://www.collegescholarships.org/scholarships/field-of-study/',
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
    }
    
    def parse(self, response):
        """Parse main pages and extract scholarship links."""
        self.pages_visited += 1
        self.logger.info(f"Parsing page: {response.url}")
        
        # Extract scholarship detail page links
        scholarship_links = response.css('a[href*="/scholarships/"]::attr(href)').getall()
        
        for link in scholarship_links:
            if self.should_follow_link(link):
                url = self.clean_url(link, response.url)
                # Skip if it's a category/listing page
                if not re.search(r'/scholarships/[^/]+/$', url):
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_scholarship,
                        meta={'source_url': response.url}
                    )
        
        # Follow category links
        category_links = response.css('.category-list a::attr(href)').getall()
        for link in category_links[:10]:  # Limit to avoid too many requests
            if self.should_follow_link(link):
                url = self.clean_url(link, response.url)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={'category': True}
                )
        
        # Handle pagination
        yield from self.parse_pagination(response)
    
    def parse_scholarship(self, response):
        """Parse individual scholarship pages."""
        self.logger.info(f"Parsing scholarship: {response.url}")
        
        # Extract title
        title = self.extract_with_selectors(response, 'title', [
            'h1.entry-title::text',
            'h1::text',
            '.scholarship-title::text',
            'title::text'
        ])
        
        if not title:
            self.logger.warning(f"No title found for {response.url}")
            return
        
        # Extract description
        description_parts = response.css('.entry-content p::text').getall()
        description = ' '.join([p.strip() for p in description_parts if p.strip()])
        
        # Extract amount
        amount_text = response.css('.scholarship-amount::text').get() or \
                     self.extract_with_selectors(response, 'amount', [
                         '.award-amount::text',
                         '.value::text',
                         '*:contains("$")::text'
                     ])
        
        amount = self.extract_amount_from_text(amount_text) if amount_text else ""
        
        # Extract deadline
        deadline_text = response.css('.deadline::text').get() or \
                       self.extract_with_selectors(response, 'deadline', [
                           '.due-date::text',
                           '*:contains("deadline")::text',
                           '*:contains("due")::text'
                       ])
        
        deadline = self.extract_deadline_from_text(deadline_text) if deadline_text else ""
        
        # Extract eligibility criteria
        eligibility_parts = response.css('.eligibility li::text').getall() or \
                           response.css('.requirements li::text').getall()
        eligibility = ' | '.join([e.strip() for e in eligibility_parts if e.strip()])
        
        # Extract requirements
        requirements_parts = response.css('.application-requirements li::text').getall() or \
                            response.css('.how-to-apply li::text').getall()
        requirements = ' | '.join([r.strip() for r in requirements_parts if r.strip()])
        
        # Extract application URL
        application_url = response.css('a[href*="apply"]::attr(href)').get() or \
                         response.css('a:contains("Apply")::attr(href)').get() or \
                         response.url
        
        application_url = self.clean_url(application_url, response.url)
        
        # Extract provider/organization
        provider = response.css('.provider::text').get() or \
                  response.css('.organization::text').get() or \
                  "CollegeScholarships.org"
        
        # Determine category
        category = self.determine_category(title, description, response.url)
        
        # Extract tags
        tags = response.css('.tags a::text').getall() or \
               response.css('.categories a::text').getall()
        
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
    
    def determine_category(self, title: str, description: str, url: str) -> str:
        """Determine scholarship category based on title, description, and URL."""
        text = f"{title} {description} {url}".lower()
        
        # Category keywords mapping
        categories = {
            'STEM': ['stem', 'engineering', 'computer', 'technology', 'science', 'math', 'programming'],
            'Business': ['business', 'economics', 'finance', 'accounting', 'mba', 'marketing'],
            'Healthcare': ['medical', 'nursing', 'health', 'medicine', 'pharmacy', 'dental'],
            'Arts': ['art', 'music', 'theater', 'creative', 'design', 'literature', 'humanities'],
            'Education': ['education', 'teaching', 'teacher', 'pedagogy'],
            'Need-Based': ['need', 'financial', 'low-income', 'pell'],
            'Merit-Based': ['merit', 'academic', 'achievement', 'gpa', 'honor'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General'
