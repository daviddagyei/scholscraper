"""
Tests for the HSF (Hispanic Scholarship Fund) spider.

This module contains tests for the HSFSpider class and its methods.
"""

import pytest
from unittest.mock import MagicMock, patch
import scrapy
from urllib.parse import urljoin

from scraper.spiders.hsf import HSFSpider
from tests.spiders.mock_spider import patch_spider_logger


# ----------------------- HSFSpider initialization tests -----------------------

def test_hsf_spider_initialization():
    """Test HSFSpider initialization."""
    spider = HSFSpider()
    
    assert spider.name == 'hsf'
    assert 'hsf.net' in spider.allowed_domains
    assert len(spider.start_urls) == 4
    assert 'https://www.hsf.net/scholarship' in spider.start_urls
    assert 'https://www.hsf.net/scholarship/high-school' in spider.start_urls
    assert 'https://www.hsf.net/scholarship/undergraduate' in spider.start_urls
    assert 'https://www.hsf.net/scholarship/graduate' in spider.start_urls


def test_hsf_spider_custom_settings():
    """Test HSFSpider custom settings."""
    spider = HSFSpider()
    
    assert 'DOWNLOAD_DELAY' in spider.custom_settings
    assert spider.custom_settings['DOWNLOAD_DELAY'] == 3
    assert 'CONCURRENT_REQUESTS_PER_DOMAIN' in spider.custom_settings
    assert spider.custom_settings['CONCURRENT_REQUESTS_PER_DOMAIN'] == 1
    assert 'RANDOMIZE_DOWNLOAD_DELAY' in spider.custom_settings


# ----------------------- HSFSpider.parse tests -----------------------

def test_parse_extracts_scholarship_links(mock_response):
    """Test parse method extracts scholarship links."""
    spider = HSFSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <div class="scholarship-item">
                <a href="/scholarship/detail/scholarship1">Scholarship 1</a>
            </div>
            <div class="scholarship-item">
                <a href="/scholarship/detail/scholarship2">Scholarship 2</a>
            </div>
            <a href="/not-scholarship/detail">Not a scholarship</a>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.hsf.net/scholarship',
        body=html
    )
    
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch.object(spider, 'parse_pagination', return_value=[]):
                results = list(spider.parse(response))
                
                assert len(results) == 2  # 2 scholarship links should be followed
                
                for request in results:
                    assert isinstance(request, scrapy.Request)
                    assert '/scholarship/detail/' in request.url
                    assert request.callback == spider.parse_scholarship


def test_parse_alternative_scholarship_link_selectors(mock_response):
    """Test parse method uses alternative selectors when primary ones fail."""
    spider = HSFSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <!-- No scholarship-item class -->
            <div class="program-link">
                <a href="/scholarship/detail/program1">Program 1</a>
            </div>
            <a href="/scholarship/detail/generic">Generic link to scholarship</a>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.hsf.net/scholarship',
        body=html
    )
    
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch.object(spider, 'parse_pagination', return_value=[]):
                results = list(spider.parse(response))
                
                assert len(results) == 2  # Both links should be followed
                
                for request in results:
                    assert isinstance(request, scrapy.Request)
                    assert '/scholarship/detail/' in request.url
                    assert request.callback == spider.parse_scholarship


def test_parse_scholarship_cards(mock_response):
    """Test parse method processes scholarship cards directly."""
    spider = HSFSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <div class="scholarship-card">
                <div class="scholarship-title">HSF General Scholarship</div>
                <div class="scholarship-description">A general scholarship for Hispanic students.</div>
                <div class="amount">$5,000</div>
                <div class="deadline">March 30, 2026</div>
                <a href="https://example.com/apply">Apply</a>
            </div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.hsf.net/scholarship',
        body=html
    )
    
    with patch.object(spider, 'parse_scholarship_card') as mock_parse_card:
        mock_parse_card.return_value = {'title': 'HSF General Scholarship'}
        
        with patch.object(spider, 'parse_pagination', return_value=[]):
            results = list(spider.parse(response))
            
            assert len(results) == 1  # Card should be processed
            assert results[0] == {'title': 'HSF General Scholarship'}
            
            # Verify card parser was called with correct selector
            mock_parse_card.assert_called_once()
            selector_arg = mock_parse_card.call_args[0][0]
            assert selector_arg.css('.scholarship-title::text').get() == 'HSF General Scholarship'


def test_parse_calls_pagination_method(mock_response):
    """Test parse method calls parse_pagination."""
    spider = HSFSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = "<html><body></body></html>"
    
    response = mock_response(
        url='https://www.hsf.net/scholarship',
        body=html
    )
    
    pagination_result = [
        scrapy.Request(url='https://www.hsf.net/scholarship?page=2')
    ]
    
    with patch.object(spider, 'parse_pagination', return_value=pagination_result):
        results = list(spider.parse(response))
        
        assert len(results) == 1
        assert results[0].url == 'https://www.hsf.net/scholarship?page=2'


# ----------------------- HSFSpider.parse_scholarship_card tests -----------------------

def test_parse_scholarship_card_extracts_data():
    """Test parse_scholarship_card extracts data from card."""
    spider = HSFSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    # Create a mock card selector
    card = MagicMock()
    card.css.side_effect = lambda selector: {
        '.scholarship-title::text': MagicMock(get=lambda: 'HSF General Scholarship'),
        'h3::text': MagicMock(get=lambda: None),
        'h4::text': MagicMock(get=lambda: None),
        '.scholarship-description::text': MagicMock(get=lambda: 'A scholarship for Hispanic students.'),
        '.description::text': MagicMock(get=lambda: None),
        '.amount::text': MagicMock(get=lambda: '$5,000'),
        '.deadline::text': MagicMock(get=lambda: 'March 30, 2026'),
        'a::attr(href)': MagicMock(get=lambda: 'https://example.com/apply'),
    }.get(selector, MagicMock(get=lambda: None))
    
    response = MagicMock()
    response.url = 'https://www.hsf.net/scholarship'
    
    with patch.object(spider, 'clean_url', return_value='https://example.com/apply'):
        with patch.object(spider, 'extract_amount_from_text', return_value='$5,000'):
            with patch.object(spider, 'extract_deadline_from_text', return_value='2026-03-30'):
                with patch.object(spider, 'determine_category', return_value='General'):
                    with patch.object(spider, 'create_scholarship_item') as mock_create_item:
                        mock_create_item.return_value = {'title': 'HSF General Scholarship'}
                        
                        result = spider.parse_scholarship_card(card, response)
                        
                        assert result == {'title': 'HSF General Scholarship'}
                        mock_create_item.assert_called_once()
                        
                        call_kwargs = mock_create_item.call_args[1]
                        assert call_kwargs['title'] == 'HSF General Scholarship'
                        assert call_kwargs['description'] == 'A scholarship for Hispanic students.'
                        assert call_kwargs['amount'] == '$5,000'
                        assert call_kwargs['deadline'] == '2026-03-30'
                        assert 'Hispanic/Latino heritage' in call_kwargs['eligibility']
                        assert 'Varies by scholarship' in call_kwargs['requirements']
                        assert call_kwargs['application_url'] == 'https://example.com/apply'
                        assert call_kwargs['provider'] == 'Hispanic Scholarship Fund (HSF)'
                        assert 'Hispanic' in call_kwargs['tags']
                        assert 'Latino' in call_kwargs['tags']


def test_parse_scholarship_card_alternative_title_selectors():
    """Test parse_scholarship_card falls back to alternative title selectors."""
    spider = HSFSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    # Create a mock card selector with primary title selector missing
    card = MagicMock()
    card.css.side_effect = lambda selector: {
        '.scholarship-title::text': MagicMock(get=lambda: None),  # Primary selector returns None
        'h3::text': MagicMock(get=lambda: 'HSF Engineering Scholarship'),  # Use this instead
        'h4::text': MagicMock(get=lambda: None),
        '.scholarship-description::text': MagicMock(get=lambda: None),
        '.description::text': MagicMock(get=lambda: 'A scholarship for Hispanic engineering students.'),
        '.amount::text': MagicMock(get=lambda: '$10,000'),
        '.deadline::text': MagicMock(get=lambda: 'April 15, 2026'),
        'a::attr(href)': MagicMock(get=lambda: 'https://example.com/apply-engineering'),
    }.get(selector, MagicMock(get=lambda: None))
    
    response = MagicMock()
    response.url = 'https://www.hsf.net/scholarship'
    
    with patch.object(spider, 'clean_url', return_value='https://example.com/apply-engineering'):
        with patch.object(spider, 'extract_amount_from_text', return_value='$10,000'):
            with patch.object(spider, 'extract_deadline_from_text', return_value='2026-04-15'):
                with patch.object(spider, 'determine_category', return_value='STEM'):
                    with patch.object(spider, 'create_scholarship_item') as mock_create_item:
                        mock_create_item.return_value = {'title': 'HSF Engineering Scholarship'}
                        
                        result = spider.parse_scholarship_card(card, response)
                        
                        assert result == {'title': 'HSF Engineering Scholarship'}
                        
                        call_kwargs = mock_create_item.call_args[1]
                        assert call_kwargs['title'] == 'HSF Engineering Scholarship'


def test_parse_scholarship_card_no_title():
    """Test parse_scholarship_card returns None when no title found."""
    spider = HSFSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    # Create a mock card selector with no title
    card = MagicMock()
    card.css.side_effect = lambda selector: {
        '.scholarship-title::text': MagicMock(get=lambda: None),
        'h3::text': MagicMock(get=lambda: None),
        'h4::text': MagicMock(get=lambda: None),
    }.get(selector, MagicMock(get=lambda: None))
    
    response = MagicMock()
    
    result = spider.parse_scholarship_card(card, response)
    
    assert result is None  # Should return None when no title found


def test_parse_scholarship_card_without_application_url():
    """Test parse_scholarship_card falls back to response URL when application URL missing."""
    spider = HSFSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    # Create a mock card selector without application URL
    card = MagicMock()
    card.css.side_effect = lambda selector: {
        '.scholarship-title::text': MagicMock(get=lambda: 'HSF Scholarship'),
        '.scholarship-description::text': MagicMock(get=lambda: 'Description'),
        '.amount::text': MagicMock(get=lambda: '$5,000'),
        '.deadline::text': MagicMock(get=lambda: 'June 1, 2026'),
        'a::attr(href)': MagicMock(get=lambda: None),  # No application URL
    }.get(selector, MagicMock(get=lambda: None))
    
    response = MagicMock()
    response.url = 'https://www.hsf.net/scholarship/default'
    
    with patch.object(spider, 'extract_amount_from_text', return_value='$5,000'):
        with patch.object(spider, 'extract_deadline_from_text', return_value='2026-06-01'):
            with patch.object(spider, 'determine_category', return_value='General'):
                with patch.object(spider, 'create_scholarship_item') as mock_create_item:
                    mock_create_item.return_value = {'title': 'HSF Scholarship'}
                    
                    result = spider.parse_scholarship_card(card, response)
                    
                    assert result == {'title': 'HSF Scholarship'}
                    
                    call_kwargs = mock_create_item.call_args[1]
                    assert call_kwargs['application_url'] == 'https://www.hsf.net/scholarship/default'


# ----------------------- Integration tests -----------------------

def test_integration_scholarship_card_parsing(mock_response):
    """Test integration of parsing scholarship cards from a page."""
    spider = HSFSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    # Sample HTML for a page with scholarship cards
    html = """
    <html>
        <body>
            <div class="scholarship-card">
                <div class="scholarship-title">HSF General Scholarship</div>
                <div class="scholarship-description">A general scholarship for Hispanic students.</div>
                <div class="amount">$5,000</div>
                <div class="deadline">March 30, 2026</div>
                <a href="https://example.com/apply">Apply</a>
            </div>
            
            <div class="scholarship-card">
                <div class="scholarship-title">HSF STEM Scholarship</div>
                <div class="scholarship-description">For Hispanic students in STEM fields.</div>
                <div class="amount">$10,000</div>
                <div class="deadline">April 15, 2026</div>
                <a href="https://example.com/apply-stem">Apply</a>
            </div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.hsf.net/scholarship',
        body=html
    )
    
    # Mock methods called by parse_scholarship_card
    with patch.object(spider, 'clean_url', return_value='https://example.com/apply'):
        with patch.object(spider, 'extract_amount_from_text', return_value='$5,000'):
            with patch.object(spider, 'extract_deadline_from_text', return_value='2026-03-30'):
                with patch.object(spider, 'determine_category', return_value='General'):
                    with patch.object(spider, 'create_scholarship_item') as mock_create_item:
                        # Return different values for each call
                        mock_create_item.side_effect = [
                            {'title': 'HSF General Scholarship'},
                            {'title': 'HSF STEM Scholarship'}
                        ]
                        
                        with patch.object(spider, 'parse_pagination', return_value=[]):
                            results = list(spider.parse(response))
                            
                            assert len(results) == 2
                            assert results[0]['title'] == 'HSF General Scholarship'
                            assert results[1]['title'] == 'HSF STEM Scholarship'
