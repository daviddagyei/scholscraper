"""
Tests for the CollegeScholarships spider.

This module contains tests for the CollegeScholarshipsSpider class and its methods.
"""

import pytest
from unittest.mock import MagicMock, patch
import scrapy
import re

from scraper.spiders.collegescholarships import CollegeScholarshipsSpider
from tests.spiders.mock_spider import patch_spider_logger


# ----------------------- CollegeScholarshipsSpider initialization tests -----------------------

def test_collegescholarships_spider_initialization():
    """Test CollegeScholarshipsSpider initialization."""
    spider = CollegeScholarshipsSpider()
    
    assert spider.name == 'collegescholarships'
    assert 'collegescholarships.org' in spider.allowed_domains
    assert len(spider.start_urls) == 3
    assert 'https://www.collegescholarships.org/scholarships/' in spider.start_urls
    assert 'https://www.collegescholarships.org/scholarships/state/' in spider.start_urls
    assert 'https://www.collegescholarships.org/scholarships/field-of-study/' in spider.start_urls


def test_collegescholarships_spider_custom_settings():
    """Test CollegeScholarshipsSpider custom settings."""
    spider = CollegeScholarshipsSpider()
    
    assert 'DOWNLOAD_DELAY' in spider.custom_settings
    assert spider.custom_settings['DOWNLOAD_DELAY'] == 3
    assert 'CONCURRENT_REQUESTS_PER_DOMAIN' in spider.custom_settings
    assert spider.custom_settings['CONCURRENT_REQUESTS_PER_DOMAIN'] == 1
    assert 'RANDOMIZE_DOWNLOAD_DELAY' in spider.custom_settings


# ----------------------- CollegeScholarshipsSpider.parse tests -----------------------

def test_parse_extracts_scholarship_links(mock_response):
    """Test parse method extracts scholarship links."""
    spider = CollegeScholarshipsSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <a href="/scholarships/detail-page-1">Scholarship 1</a>
            <a href="/scholarships/detail-page-2">Scholarship 2</a>
            <a href="/scholarships/detail-page-3">Scholarship 3</a>
            <a href="/not-scholarships/other-page">Not a scholarship</a>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.collegescholarships.org/scholarships/',
        body=html
    )
    
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            results = list(spider.parse(response))
            
            assert len(results) == 3  # 3 scholarship links should be followed
            
            for request in results:
                assert isinstance(request, scrapy.Request)
                assert '/scholarships/detail-page-' in request.url
                assert request.callback == spider.parse_scholarship


def test_parse_follows_category_links(mock_response):
    """Test parse method follows category links."""
    spider = CollegeScholarshipsSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <div class="category-list">
                <a href="/scholarships/category1/">Category 1</a>
                <a href="/scholarships/category2/">Category 2</a>
            </div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.collegescholarships.org/scholarships/',
        body=html
    )
    
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch.object(spider, 'parse_pagination', return_value=[]):
                results = list(spider.parse(response))
                
                assert len(results) == 2  # 2 category links should be followed
                
                for request in results:
                    assert isinstance(request, scrapy.Request)
                    assert '/scholarships/category' in request.url
                    assert request.callback == spider.parse
                    assert request.meta['category'] is True


def test_parse_calls_pagination_method(mock_response):
    """Test parse method calls parse_pagination."""
    spider = CollegeScholarshipsSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = "<html><body></body></html>"
    
    response = mock_response(
        url='https://www.collegescholarships.org/scholarships/',
        body=html
    )
    
    pagination_result = [
        scrapy.Request(url='https://www.collegescholarships.org/scholarships/page2.html')
    ]
    
    with patch.object(spider, 'parse_pagination', return_value=pagination_result):
        results = list(spider.parse(response))
        
        assert len(results) == 1
        assert results[0].url == 'https://www.collegescholarships.org/scholarships/page2.html'


# ----------------------- CollegeScholarshipsSpider.parse_scholarship tests -----------------------

def test_parse_scholarship_extracts_data(mock_response):
    """Test parse_scholarship method extracts scholarship data."""
    spider = CollegeScholarshipsSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <h1 class="entry-title">STEM Excellence Scholarship</h1>
            <div class="entry-content">
                <p>This scholarship is for students pursuing STEM fields.</p>
                <p>It provides financial assistance for tuition and books.</p>
            </div>
            <div class="scholarship-amount">$5,000</div>
            <div class="deadline">January 15, 2026</div>
            <ul class="eligibility">
                <li>Must be a full-time student</li>
                <li>GPA of 3.0 or higher</li>
            </ul>
            <ul class="application-requirements">
                <li>Application form</li>
                <li>Essay</li>
            </ul>
            <a href="https://example.com/apply" class="apply-button">Apply Now</a>
            <div class="provider">STEM Foundation</div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.collegescholarships.org/scholarships/stem-scholarship.html',
        body=html
    )
    
    with patch.object(spider, 'create_scholarship_item') as mock_create_item:
        mock_create_item.return_value = {'title': 'STEM Excellence Scholarship'}
        
        results = list(spider.parse_scholarship(response))
        
        assert len(results) == 1
        assert results[0] == {'title': 'STEM Excellence Scholarship'}
        
        mock_create_item.assert_called_once()
        call_kwargs = mock_create_item.call_args[1]
        
        assert call_kwargs['title'] == 'STEM Excellence Scholarship'
        assert 'STEM fields' in call_kwargs['description']
        assert call_kwargs['amount'] == '$5,000'
        assert call_kwargs['deadline'] == 'January 15, 2026'
        assert 'Must be a full-time student' in call_kwargs['eligibility']
        assert 'Application form' in call_kwargs['requirements']
        assert call_kwargs['application_url'] == 'https://example.com/apply'
        assert call_kwargs['provider'] == 'STEM Foundation'


def test_parse_scholarship_no_title_found(mock_response):
    """Test parse_scholarship method when no title is found."""
    spider = CollegeScholarshipsSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <!-- No title element -->
            <div class="entry-content">
                <p>This scholarship is for students pursuing STEM fields.</p>
            </div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.collegescholarships.org/scholarships/stem-scholarship.html',
        body=html
    )
    
    with patch.object(spider, 'extract_with_selectors', return_value=None):
        results = list(spider.parse_scholarship(response))
        
        assert len(results) == 0  # Should not yield an item
        spider.logger.warning.assert_called_once()  # Should log a warning


def test_parse_scholarship_alternative_selectors(mock_response):
    """Test parse_scholarship method with alternative selectors."""
    spider = CollegeScholarshipsSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <!-- No primary selectors -->
            <h1>STEM Excellence Scholarship</h1>
            <div class="content">
                <p>This scholarship is for students pursuing STEM fields.</p>
            </div>
            <div class="value">$5,000</div>
            <div class="due-date">January 15, 2026</div>
            <ul class="requirements">
                <li>Must be a full-time student</li>
                <li>GPA of 3.0 or higher</li>
            </ul>
            <ul class="how-to-apply">
                <li>Application form</li>
                <li>Essay</li>
            </ul>
            <a href="https://example.com/apply">Apply</a>
            <div class="organization">STEM Foundation</div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.collegescholarships.org/scholarships/stem-scholarship.html',
        body=html
    )
    
    def mock_extract_with_selectors(resp, field_name, selectors):
        if field_name == 'title':
            return 'STEM Excellence Scholarship'
        elif field_name == 'amount':
            return '$5,000'
        elif field_name == 'deadline':
            return 'January 15, 2026'
        return None
    
    with patch.object(spider, 'extract_with_selectors', side_effect=mock_extract_with_selectors):
        with patch.object(spider, 'extract_amount_from_text', return_value='$5,000'):
            with patch.object(spider, 'extract_deadline_from_text', return_value='January 15, 2026'):
                with patch.object(spider, 'clean_url', return_value='https://example.com/apply'):
                    with patch.object(spider, 'create_scholarship_item') as mock_create_item:
                        mock_create_item.return_value = {'title': 'STEM Excellence Scholarship'}
                        
                        results = list(spider.parse_scholarship(response))
                        
                        assert len(results) == 1
                        assert results[0] == {'title': 'STEM Excellence Scholarship'}


# ----------------------- CollegeScholarshipsSpider.determine_category tests -----------------------

def test_determine_category_stem():
    """Test determine_category with STEM content."""
    spider = CollegeScholarshipsSpider()
    
    title = "Engineering Scholarship"
    description = "For students in computer science or technology fields."
    url = "https://example.com/engineering-scholarship"
    
    category = spider.determine_category(title, description, url)
    
    assert category == 'STEM'


def test_determine_category_business():
    """Test determine_category with business content."""
    spider = CollegeScholarshipsSpider()
    
    title = "MBA Finance Scholarship"
    description = "For students pursuing business or accounting degrees."
    url = "https://example.com/business-scholarship"
    
    category = spider.determine_category(title, description, url)
    
    assert category == 'Business'


def test_determine_category_healthcare():
    """Test determine_category with healthcare content."""
    spider = CollegeScholarshipsSpider()
    
    title = "Nursing Scholarship"
    description = "For students in medical or health-related fields."
    url = "https://example.com/nursing-scholarship"
    
    category = spider.determine_category(title, description, url)
    
    assert category == 'Healthcare'


def test_determine_category_arts():
    """Test determine_category with arts content."""
    spider = CollegeScholarshipsSpider()
    
    title = "Music Performance Scholarship"
    description = "For students in humanities and creative arts."
    url = "https://example.com/arts-scholarship"
    
    category = spider.determine_category(title, description, url)
    
    assert category == 'Arts'


def test_determine_category_education():
    """Test determine_category with education content."""
    spider = CollegeScholarshipsSpider()
    
    title = "Future Teachers Scholarship"
    description = "For students studying education and pedagogy."
    url = "https://example.com/teaching-scholarship"
    
    category = spider.determine_category(title, description, url)
    
    assert category == 'Education'


def test_determine_category_need_based():
    """Test determine_category with need-based content."""
    spider = CollegeScholarshipsSpider()
    
    title = "Financial Need Scholarship"
    description = "For low-income students qualifying for Pell grants."
    url = "https://example.com/need-based-scholarship"
    
    category = spider.determine_category(title, description, url)
    
    assert category == 'Need-Based'


def test_determine_category_merit_based():
    """Test determine_category with merit-based content."""
    spider = CollegeScholarshipsSpider()
    
    title = "Academic Achievement Scholarship"
    description = "For students with high GPA and academic merit."
    url = "https://example.com/honor-scholarship"
    
    category = spider.determine_category(title, description, url)
    
    assert category == 'Merit-Based'


def test_determine_category_general():
    """Test determine_category with general content."""
    spider = CollegeScholarshipsSpider()
    
    title = "Student Scholarship"
    description = "Available to all students."
    url = "https://example.com/scholarship"
    
    category = spider.determine_category(title, description, url)
    
    assert category == 'General'


# ----------------------- Integration tests -----------------------

def test_integration_full_page_parsing(mock_response):
    """Test full page parsing integration."""
    from urllib.parse import urljoin
    
    spider = CollegeScholarshipsSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    # Sample HTML for a listing page
    listing_html = """
    <html>
        <body>
            <a href="/scholarships/detail-page-1">Scholarship 1</a>
            <a href="/scholarships/detail-page-2">Scholarship 2</a>
            
            <div class="category-list">
                <a href="/scholarships/category1/">Category 1</a>
            </div>
            
            <div class="pagination">
                <a href="/scholarships/page2.html">Next Page</a>
            </div>
        </body>
    </html>
    """
    
    listing_response = mock_response(
        url='https://www.collegescholarships.org/scholarships/',
        body=listing_html
    )
    
    # Sample HTML for a scholarship detail page
    detail_html = """
    <html>
        <body>
            <h1 class="entry-title">STEM Excellence Scholarship</h1>
            <div class="entry-content">
                <p>This scholarship is for students pursuing STEM fields.</p>
            </div>
            <div class="scholarship-amount">$5,000</div>
            <div class="deadline">January 15, 2026</div>
            <ul class="eligibility">
                <li>Must be a full-time student</li>
            </ul>
            <a href="https://example.com/apply" class="apply-button">Apply Now</a>
            <div class="provider">STEM Foundation</div>
        </body>
    </html>
    """
    
    # Create patches for all relevant methods
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch('scrapy.Request') as mock_request:
                results = list(spider.parse(listing_response))
                
                # Should have made 4 requests: 2 detail pages, 1 category, 1 next page
                assert mock_request.call_count >= 4
