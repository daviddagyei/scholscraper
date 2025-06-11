"""
Tests for the APIA (Asian Pacific Islander American) Scholars spider.

This module contains tests for the APIAScholarsSpider class and its methods.
"""

import pytest
from unittest.mock import MagicMock, patch
import scrapy
from urllib.parse import urljoin

from scraper.spiders.apia import APIAScholarsSpider
from tests.spiders.mock_spider import patch_spider_logger


# ----------------------- APIAScholarsSpider initialization tests -----------------------

def test_apia_spider_initialization():
    """Test APIAScholarsSpider initialization."""
    spider = APIAScholarsSpider()
    
    assert spider.name == 'apia'
    assert 'apiascholars.org' in spider.allowed_domains
    assert len(spider.start_urls) == 3
    assert 'https://www.apiascholars.org/scholarships' in spider.start_urls
    assert 'https://www.apiascholars.org/scholarships/undergraduate' in spider.start_urls
    assert 'https://www.apiascholars.org/scholarships/graduate' in spider.start_urls


def test_apia_spider_custom_settings():
    """Test APIAScholarsSpider custom settings."""
    spider = APIAScholarsSpider()
    
    assert 'DOWNLOAD_DELAY' in spider.custom_settings
    assert spider.custom_settings['DOWNLOAD_DELAY'] == 3
    assert 'CONCURRENT_REQUESTS_PER_DOMAIN' in spider.custom_settings
    assert spider.custom_settings['CONCURRENT_REQUESTS_PER_DOMAIN'] == 1
    assert 'RANDOMIZE_DOWNLOAD_DELAY' in spider.custom_settings


# ----------------------- APIAScholarsSpider.parse tests -----------------------

def test_parse_extracts_scholarship_links(mock_response):
    """Test parse method extracts scholarship links."""
    spider = APIAScholarsSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <div class="scholarship-card">
                <a href="/scholarship/detail1">Scholarship 1</a>
            </div>
            <div class="scholarship-card">
                <a href="/scholarship/detail2">Scholarship 2</a>
            </div>
            <a href="/not-scholarship/detail">Not a scholarship</a>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.apiascholars.org/scholarships',
        body=html
    )
    
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch.object(spider, 'parse_pagination', return_value=[]):
                results = list(spider.parse(response))
                
                assert len(results) == 2  # 2 scholarship links should be followed
                
                for request in results:
                    assert isinstance(request, scrapy.Request)
                    assert '/scholarship/detail' in request.url
                    assert request.callback == spider.parse_scholarship


def test_parse_alternative_scholarship_link_selectors(mock_response):
    """Test parse method uses alternative selectors when primary ones fail."""
    spider = APIAScholarsSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <!-- No scholarship-card class -->
            <div class="program-card">
                <a href="/scholarship/program1">Program 1</a>
            </div>
            <a href="/scholarship/generic">Generic link to scholarship</a>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.apiascholars.org/scholarships',
        body=html
    )
    
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch.object(spider, 'parse_pagination', return_value=[]):
                results = list(spider.parse(response))
                
                assert len(results) == 2  # Both links should be followed
                
                for request in results:
                    assert isinstance(request, scrapy.Request)
                    assert '/scholarship/' in request.url
                    assert request.callback == spider.parse_scholarship


def test_parse_calls_pagination_method(mock_response):
    """Test parse method calls parse_pagination."""
    spider = APIAScholarsSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = "<html><body></body></html>"
    
    response = mock_response(
        url='https://www.apiascholars.org/scholarships',
        body=html
    )
    
    pagination_result = [
        scrapy.Request(url='https://www.apiascholars.org/scholarships?page=2')
    ]
    
    with patch.object(spider, 'parse_pagination', return_value=pagination_result):
        results = list(spider.parse(response))
        
        assert len(results) == 1
        assert results[0].url == 'https://www.apiascholars.org/scholarships?page=2'


# ----------------------- APIAScholarsSpider.parse_scholarship tests -----------------------

def test_parse_scholarship_extracts_data(mock_response):
    """Test parse_scholarship method extracts scholarship data."""
    spider = APIAScholarsSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <h1 class="scholarship-title">APIA STEM Scholarship</h1>
            <div class="scholarship-description">
                <p>This scholarship is for Asian American and Pacific Islander students.</p>
                <p>It provides financial assistance for STEM education.</p>
            </div>
            <div class="award-amount">$7,500</div>
            <div class="deadline">May 15, 2026</div>
            <ul class="eligibility-criteria">
                <li>Must be of Asian or Pacific Islander heritage</li>
                <li>GPA of 3.0 or higher</li>
                <li>Pursuing STEM degree</li>
            </ul>
            <ul class="requirements">
                <li>Application form</li>
                <li>Essay</li>
                <li>Transcripts</li>
            </ul>
            <a href="https://example.com/apply-apia" class="apply-button">Apply Now</a>
            <div class="provider">APIA Scholars</div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.apiascholars.org/scholarship/stem',
        body=html
    )
    
    with patch.object(spider, 'extract_amount_from_text', return_value='$7,500'):
        with patch.object(spider, 'extract_deadline_from_text', return_value='2026-05-15'):
            with patch.object(spider, 'create_scholarship_item') as mock_create_item:
                mock_create_item.return_value = {'title': 'APIA STEM Scholarship'}
                
                results = list(spider.parse_scholarship(response))
                
                assert len(results) == 1
                assert results[0] == {'title': 'APIA STEM Scholarship'}
                
                mock_create_item.assert_called_once()
                call_kwargs = mock_create_item.call_args[1]
                
                assert call_kwargs['title'] == 'APIA STEM Scholarship'
                assert 'Asian American and Pacific Islander' in call_kwargs['description']
                assert 'STEM education' in call_kwargs['description']
                assert call_kwargs['amount'] == '$7,500'
                assert call_kwargs['deadline'] == '2026-05-15'
                assert 'Asian or Pacific Islander heritage' in call_kwargs['eligibility']
                assert 'Application form' in call_kwargs['requirements']
                assert call_kwargs['application_url'] == 'https://example.com/apply-apia'
                assert call_kwargs['provider'] == 'APIA Scholars'
                assert 'Asian Pacific Islander American' in call_kwargs['tags']


def test_parse_scholarship_alternative_title_selectors(mock_response):
    """Test parse_scholarship uses alternative title selectors."""
    spider = APIAScholarsSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <!-- No scholarship-title class -->
            <h1 class="page-title">APIA Graduate Scholarship</h1>
            <div class="program-description">
                <p>This scholarship is for graduate students.</p>
            </div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.apiascholars.org/scholarship/graduate',
        body=html
    )
    
    with patch.object(spider, 'extract_with_selectors') as mock_extract:
        mock_extract.side_effect = lambda resp, field, selectors=None: {
            'title': 'APIA Graduate Scholarship',
            'amount': '$10,000',
            'deadline': 'June 30, 2026'
        }.get(field, '')
        
        with patch.object(spider, 'extract_amount_from_text', return_value='$10,000'):
            with patch.object(spider, 'extract_deadline_from_text', return_value='2026-06-30'):
                with patch.object(spider, 'create_scholarship_item') as mock_create_item:
                    mock_create_item.return_value = {'title': 'APIA Graduate Scholarship'}
                    
                    results = list(spider.parse_scholarship(response))
                    
                    assert len(results) == 1
                    call_kwargs = mock_create_item.call_args[1]
                    
                    assert call_kwargs['title'] == 'APIA Graduate Scholarship'
                    # Should have called extract_with_selectors with title field
                    mock_extract.assert_any_call(response, 'title', [
                        'h1.scholarship-title::text',
                        'h1.page-title::text',
                        'h1::text',
                        '.program-name::text',
                    ])


def test_parse_scholarship_no_title_found(mock_response):
    """Test parse_scholarship method when no title is found."""
    spider = APIAScholarsSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <!-- No title element -->
            <div class="content">
                <p>This scholarship has no title.</p>
            </div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.apiascholars.org/scholarship/notitle',
        body=html
    )
    
    with patch.object(spider, 'extract_with_selectors', return_value=None):
        results = list(spider.parse_scholarship(response))
        
        assert len(results) == 0  # Should not yield an item
        spider.logger.warning.assert_called_once()  # Should log a warning


def test_parse_scholarship_default_eligibility(mock_response):
    """Test parse_scholarship fills default eligibility when none found."""
    spider = APIAScholarsSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <h1 class="scholarship-title">APIA Scholarship</h1>
            <div class="scholarship-description">
                <p>A scholarship for APIA students.</p>
            </div>
            <!-- No eligibility section -->
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.apiascholars.org/scholarship/general',
        body=html
    )
    
    with patch.object(spider, 'extract_with_selectors') as mock_extract:
        mock_extract.side_effect = lambda resp, field, selectors=None: {
            'title': 'APIA Scholarship'
        }.get(field, None)
        
        with patch.object(spider, 'create_scholarship_item') as mock_create_item:
            mock_create_item.return_value = {'title': 'APIA Scholarship'}
            
            results = list(spider.parse_scholarship(response))
            
            assert len(results) == 1
            call_kwargs = mock_create_item.call_args[1]
            
            # Should have default eligibility text
            assert 'Asian Pacific Islander American heritage' in call_kwargs['eligibility']
            assert 'US citizenship or legal residency' in call_kwargs['eligibility']


# ----------------------- Integration tests -----------------------

def test_integration_full_page_parsing(mock_response):
    """Test full page parsing integration."""
    from urllib.parse import urljoin
    
    spider = APIAScholarsSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    # Sample HTML for a listing page
    listing_html = """
    <html>
        <body>
            <div class="scholarship-card">
                <a href="/scholarship/detail1">Scholarship 1</a>
            </div>
            
            <div class="pagination">
                <a href="/scholarships?page=2">Next Page</a>
            </div>
        </body>
    </html>
    """
    
    listing_response = mock_response(
        url='https://www.apiascholars.org/scholarships',
        body=listing_html
    )
    
    # Create patches for all relevant methods
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch('scrapy.Request') as mock_request:
                results = list(spider.parse(listing_response))
                
                # Should have made 2 requests: 1 detail page, 1 pagination
                assert mock_request.call_count >= 2


def test_integration_scholarship_detail_parsing(mock_response):
    """Test integration of parsing a scholarship detail page."""
    spider = APIAScholarsSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    # Sample HTML for a detail page
    detail_html = """
    <html>
        <body>
            <h1 class="scholarship-title">APIA STEM Scholarship</h1>
            <div class="scholarship-description">
                <p>This scholarship is for Asian American and Pacific Islander students.</p>
                <p>It provides financial assistance for STEM education.</p>
            </div>
            <div class="award-amount">$7,500</div>
            <div class="deadline">May 15, 2026</div>
            <ul class="eligibility-criteria">
                <li>Must be of Asian or Pacific Islander heritage</li>
                <li>GPA of 3.0 or higher</li>
            </ul>
            <a href="https://example.com/apply-apia" class="apply-button">Apply Now</a>
        </body>
    </html>
    """
    
    detail_response = mock_response(
        url='https://www.apiascholars.org/scholarship/stem',
        body=detail_html
    )
    
    with patch.object(spider, 'extract_amount_from_text', return_value='$7,500'):
        with patch.object(spider, 'extract_deadline_from_text', return_value='2026-05-15'):
            with patch.object(spider, 'clean_url', return_value='https://example.com/apply-apia'):
                with patch.object(spider, 'create_scholarship_item') as mock_create_item:
                    mock_create_item.return_value = {'title': 'APIA STEM Scholarship'}
                    
                    results = list(spider.parse_scholarship(detail_response))
                    
                    # Verify the expected scholarship item is created
                    assert len(results) == 1
                    assert results[0] == {'title': 'APIA STEM Scholarship'}
