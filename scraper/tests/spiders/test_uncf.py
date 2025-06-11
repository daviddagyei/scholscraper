"""
Tests for the UNCF (United Negro College Fund) spider.

This module contains tests for the UNCFSpider class and its methods.
"""

import pytest
from unittest.mock import MagicMock, patch
import scrapy
from urllib.parse import urljoin

from scraper.spiders.uncf import UNCFSpider
from tests.spiders.mock_spider import patch_spider_logger


# ----------------------- UNCFSpider initialization tests -----------------------

def test_uncf_spider_initialization():
    """Test UNCFSpider initialization."""
    spider = UNCFSpider()
    
    assert spider.name == 'uncf'
    assert 'uncf.org' in spider.allowed_domains
    assert len(spider.start_urls) == 4
    assert 'https://uncf.org/scholarships' in spider.start_urls
    assert 'https://uncf.org/scholarships/undergraduate-scholarships' in spider.start_urls
    assert 'https://uncf.org/scholarships/graduate-scholarships' in spider.start_urls
    assert 'https://uncf.org/scholarships/high-school-scholarships' in spider.start_urls


def test_uncf_spider_custom_settings():
    """Test UNCFSpider custom settings."""
    spider = UNCFSpider()
    
    assert 'DOWNLOAD_DELAY' in spider.custom_settings
    assert spider.custom_settings['DOWNLOAD_DELAY'] == 4
    assert 'CONCURRENT_REQUESTS_PER_DOMAIN' in spider.custom_settings
    assert spider.custom_settings['CONCURRENT_REQUESTS_PER_DOMAIN'] == 1
    assert 'RANDOMIZE_DOWNLOAD_DELAY' in spider.custom_settings


# ----------------------- UNCFSpider.parse tests -----------------------

def test_parse_extracts_scholarship_card_links(mock_response):
    """Test parse method extracts scholarship card links."""
    spider = UNCFSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <div class="scholarship-cards">
                <div class="scholarship-card">
                    <a href="/scholarship/detail-page-1">Scholarship 1</a>
                </div>
                <div class="scholarship-card">
                    <a href="/scholarship/detail-page-2">Scholarship 2</a>
                </div>
            </div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://uncf.org/scholarships',
        body=html
    )
    
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch.object(spider, 'parse_pagination', return_value=[]):
                results = list(spider.parse(response))
                
                assert len(results) == 2  # 2 scholarship links should be followed
                
                for request in results:
                    assert isinstance(request, scrapy.Request)
                    assert '/scholarship/detail-page-' in request.url
                    assert request.callback == spider.parse_scholarship


def test_parse_alternative_scholarship_link_selectors(mock_response):
    """Test parse method uses alternative selectors when primary ones fail."""
    spider = UNCFSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <!-- No scholarship-card class -->
            <div class="program-cards">
                <div class="program-card">
                    <a href="/scholarship/detail-page-1">Scholarship 1</a>
                </div>
            </div>
            <a href="/scholarship/detail-page-2">Generic link to scholarship</a>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://uncf.org/scholarships',
        body=html
    )
    
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch.object(spider, 'parse_pagination', return_value=[]):
                results = list(spider.parse(response))
                
                assert len(results) == 2  # Both links should be followed
                
                for request in results:
                    assert isinstance(request, scrapy.Request)
                    assert '/scholarship/detail-page-' in request.url
                    assert request.callback == spider.parse_scholarship


def test_parse_ajax_loaded_content_links(mock_response):
    """Test parse method handles AJAX-loaded content."""
    spider = UNCFSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <div data-ajax-url="/ajax/scholarships"></div>
            <div data-ajax-url="/ajax/more-scholarships"></div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://uncf.org/scholarships',
        body=html
    )
    
    with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
        with patch.object(spider, 'parse_pagination', return_value=[]):
            results = list(spider.parse(response))
            
            assert len(results) == 2  # Both AJAX URLs should be followed
            
            for request in results:
                assert isinstance(request, scrapy.Request)
                assert '/ajax/' in request.url
                assert request.callback == spider.parse


def test_parse_calls_pagination_method(mock_response):
    """Test parse method calls parse_pagination."""
    spider = UNCFSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = "<html><body></body></html>"
    
    response = mock_response(
        url='https://uncf.org/scholarships',
        body=html
    )
    
    pagination_result = [
        scrapy.Request(url='https://uncf.org/scholarships?page=2')
    ]
    
    with patch.object(spider, 'parse_pagination', return_value=pagination_result):
        results = list(spider.parse(response))
        
        assert len(results) == 1
        assert results[0].url == 'https://uncf.org/scholarships?page=2'


# ----------------------- UNCFSpider.parse_scholarship tests -----------------------

def test_parse_scholarship_extracts_data(mock_response):
    """Test parse_scholarship method extracts scholarship data."""
    spider = UNCFSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <h1 class="page-title">UNCF Engineering Scholarship</h1>
            <div class="program-description">
                <p>This scholarship is for African American students pursuing engineering.</p>
                <p>It provides financial assistance for tuition and books.</p>
            </div>
            <div class="award-amount">$10,000</div>
            <div class="due-date">March 31, 2026</div>
            <ul class="eligibility-criteria">
                <li>Must be African American</li>
                <li>GPA of 3.0 or higher</li>
                <li>Engineering major</li>
            </ul>
            <ul class="application-process">
                <li>Application form</li>
                <li>Essay</li>
                <li>Transcripts</li>
            </ul>
            <a href="https://example.com/apply" class="apply-now-button">Apply Now</a>
            <div class="organization-name">UNCF</div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://uncf.org/scholarship/engineering-scholarship',
        body=html
    )
    
    with patch.object(spider, 'create_scholarship_item') as mock_create_item:
        mock_create_item.return_value = {'title': 'UNCF Engineering Scholarship'}
        
        results = list(spider.parse_scholarship(response))
        
        assert len(results) == 1
        assert results[0] == {'title': 'UNCF Engineering Scholarship'}
        
        mock_create_item.assert_called_once()
        call_kwargs = mock_create_item.call_args[1]
        
        assert call_kwargs['title'] == 'UNCF Engineering Scholarship'
        assert 'African American' in call_kwargs['description']
        assert call_kwargs['amount'] == '$10,000'
        assert call_kwargs['deadline'] == 'March 31, 2026'
        assert 'Must be African American' in call_kwargs['eligibility']
        assert 'Application form' in call_kwargs['requirements']
        assert call_kwargs['application_url'] == 'https://example.com/apply'
        assert call_kwargs['provider'] == 'UNCF'
        assert call_kwargs['category'] == 'STEM'


def test_parse_scholarship_no_title_found(mock_response):
    """Test parse_scholarship method when no title is found."""
    spider = UNCFSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <!-- No title element -->
            <div class="program-description">
                <p>This scholarship is for African American students.</p>
            </div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://uncf.org/scholarship/missing-title',
        body=html
    )
    
    with patch.object(spider, 'extract_with_selectors', return_value=None):
        results = list(spider.parse_scholarship(response))
        
        assert len(results) == 0  # Should not yield an item
        spider.logger.warning.assert_called_once()  # Should log a warning


def test_parse_scholarship_with_limited_description_parts(mock_response):
    """Test parse_scholarship method with limited description parts."""
    spider = UNCFSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <h1 class="page-title">UNCF Engineering Scholarship</h1>
            <div class="program-description">
                <p>This scholarship is for African American students.</p>
                <p>It provides financial assistance.</p>
                <p>Must be enrolled in engineering program.</p>
                <p>Additional details that shouldn't be included in limited description.</p>
            </div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://uncf.org/scholarship/engineering-scholarship',
        body=html
    )
    
    def mock_extract_with_selectors(resp, field_name, selectors):
        if field_name == 'title':
            return 'UNCF Engineering Scholarship'
        return None
    
    with patch.object(spider, 'extract_with_selectors', side_effect=mock_extract_with_selectors):
        with patch.object(spider, 'create_scholarship_item') as mock_create_item:
            mock_create_item.return_value = {'title': 'UNCF Engineering Scholarship'}
            
            results = list(spider.parse_scholarship(response))
            
            assert len(results) == 1
            
            call_kwargs = mock_create_item.call_args[1]
            description = call_kwargs['description']
            
            # Should contain only first 3 paragraphs
            assert 'This scholarship is for African American students' in description
            assert 'It provides financial assistance' in description
            assert 'Must be enrolled in engineering program' in description
            assert 'Additional details' not in description


# ----------------------- Integration tests -----------------------

def test_integration_full_page_parsing(mock_response):
    """Test full page parsing integration."""
    from urllib.parse import urljoin
    
    spider = UNCFSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    # Sample HTML for a listing page
    listing_html = """
    <html>
        <body>
            <div class="scholarship-cards">
                <div class="scholarship-card">
                    <a href="/scholarship/detail-1">Scholarship 1</a>
                </div>
            </div>
            <div data-ajax-url="/ajax/scholarships"></div>
            <div class="pagination">
                <a href="/scholarships?page=2">Next Page</a>
            </div>
        </body>
    </html>
    """
    
    listing_response = mock_response(
        url='https://uncf.org/scholarships',
        body=listing_html
    )
    
    # Sample HTML for a scholarship detail page
    detail_html = """
    <html>
        <body>
            <h1 class="page-title">Engineering Scholarship</h1>
            <div class="program-description">
                <p>This is a scholarship for engineering students.</p>
            </div>
            <div class="award-amount">$7,500</div>
            <div class="due-date">May 15, 2026</div>
            <a href="https://example.com/apply" class="apply-now">Apply</a>
        </body>
    </html>
    """
    
    # Create patches for all relevant methods
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch('scrapy.Request') as mock_request:
                results = list(spider.parse(listing_response))
                
                # Should have made 3 requests: 1 detail page, 1 AJAX URL, 1 pagination
                assert mock_request.call_count >= 3


def test_integration_ajax_content_handling(mock_response):
    """Test handling of AJAX content."""
    from urllib.parse import urljoin
    
    spider = UNCFSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    # Sample HTML for an AJAX response
    ajax_html = """
    <html>
        <body>
            <div class="scholarship-card">
                <a href="/scholarship/ajax-scholarship-1">Ajax Scholarship 1</a>
            </div>
            <div class="scholarship-card">
                <a href="/scholarship/ajax-scholarship-2">Ajax Scholarship 2</a>
            </div>
        </body>
    </html>
    """
    
    ajax_response = mock_response(
        url='https://uncf.org/ajax/scholarships',
        body=ajax_html
    )
    
    # Create patches for all relevant methods
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch('scrapy.Request') as mock_request:
                results = list(spider.parse(ajax_response))
                
                # Should have made 2 requests for the scholarship detail pages
                assert mock_request.call_count >= 2
                
                # Check that the URLs are correctly formed
                call_args_list = mock_request.call_args_list
                urls = [call[1]['url'] for call in call_args_list]
                
                assert any('ajax-scholarship-1' in url for url in urls)
                assert any('ajax-scholarship-2' in url for url in urls)


def test_integration_multiple_selectors(mock_response):
    """Test that multiple selectors are tried until one works."""
    spider = UNCFSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    # Sample HTML with different selectors than the primary ones
    html = """
    <html>
        <body>
            <h1 class="program-title">Program Title (not page-title)</h1>
            <div class="content-body">
                <p>This scholarship uses alternative selectors.</p>
            </div>
            <div class="program-amount">$5,000</div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://uncf.org/scholarship/alternative-selectors',
        body=html
    )
    
    with patch.object(spider, 'create_scholarship_item') as mock_create_item:
        mock_create_item.return_value = {'title': 'Program Title (not page-title)'}
        
        results = list(spider.parse_scholarship(response))
        
        assert len(results) == 1
        mock_create_item.assert_called_once()
        call_kwargs = mock_create_item.call_args[1]
        
        assert call_kwargs['title'] == 'Program Title (not page-title)'
