"""
Tests for the Native American scholarship spider.

This module contains tests for the NativeAmericanSpider class and its methods.
"""

import pytest
from unittest.mock import MagicMock, patch
import scrapy
from urllib.parse import urljoin

from scraper.spiders.native_american import NativeAmericanSpider
from tests.spiders.mock_spider import patch_spider_logger


# ----------------------- NativeAmericanSpider initialization tests -----------------------

def test_native_american_spider_initialization():
    """Test NativeAmericanSpider initialization."""
    spider = NativeAmericanSpider()
    
    assert spider.name == 'native_american'
    assert set(spider.allowed_domains) == {'aises.org', 'naja.com', 'collegefund.org', 'aianta.org'}
    assert len(spider.start_urls) == 4
    assert 'https://www.aises.org/scholarships' in spider.start_urls
    assert 'https://www.naja.com/scholarships' in spider.start_urls
    assert 'https://collegefund.org/students/scholarships/' in spider.start_urls
    assert 'https://www.aianta.org/scholarships/' in spider.start_urls


def test_native_american_spider_custom_settings():
    """Test NativeAmericanSpider custom settings."""
    spider = NativeAmericanSpider()
    
    assert 'DOWNLOAD_DELAY' in spider.custom_settings
    assert spider.custom_settings['DOWNLOAD_DELAY'] == 4
    assert 'CONCURRENT_REQUESTS_PER_DOMAIN' in spider.custom_settings
    assert spider.custom_settings['CONCURRENT_REQUESTS_PER_DOMAIN'] == 1
    assert 'RANDOMIZE_DOWNLOAD_DELAY' in spider.custom_settings


# ----------------------- NativeAmericanSpider.parse tests -----------------------

def test_parse_extracts_scholarship_links(mock_response):
    """Test parse method extracts scholarship links using different selectors."""
    spider = NativeAmericanSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <div class="scholarship-item">
                <a href="/scholarship/aises-scholarship">AISES Scholarship</a>
            </div>
            <div class="scholarship-item">
                <a href="/scholarship/another-scholarship">Another Scholarship</a>
            </div>
            <a href="/not-scholarship/detail">Not a scholarship</a>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.aises.org/scholarships',
        body=html
    )
    
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch.object(spider, 'parse_pagination', return_value=[]):
                results = list(spider.parse(response))
                
                assert len(results) == 2  # 2 scholarship links should be followed
                
                for request in results:
                    assert isinstance(request, scrapy.Request)
                    assert '/scholarship/' in request.url
                    assert request.callback == spider.parse_scholarship
                    # Check that source domain is passed in meta
                    assert 'source_domain' in request.meta
                    assert request.meta['source_domain'] == 'www.aises.org'


def test_parse_alternative_scholarship_selectors(mock_response):
    """Test parse method tries different selectors for different sites."""
    spider = NativeAmericanSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    # HTML with the second selector pattern
    html = """
    <html>
        <body>
            <div class="program-card">
                <a href="/scholarship/program1">Program 1</a>
            </div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://collegefund.org/students/scholarships/',
        body=html
    )
    
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch.object(spider, 'parse_pagination', return_value=[]):
                results = list(spider.parse(response))
                
                assert len(results) == 1
                assert '/scholarship/program1' in results[0].url
                assert results[0].meta['source_domain'] == 'collegefund.org'


def test_parse_third_selector_pattern(mock_response):
    """Test parse method with third selector pattern."""
    spider = NativeAmericanSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    # HTML with the third selector pattern
    html = """
    <html>
        <body>
            <a href="/scholarship/native-scholarship">Native Scholarship</a>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.naja.com/scholarships',
        body=html
    )
    
    with patch.object(spider, 'should_follow_link', return_value=True):
        with patch.object(spider, 'clean_url', side_effect=lambda url, base: urljoin(base, url)):
            with patch.object(spider, 'parse_pagination', return_value=[]):
                results = list(spider.parse(response))
                
                assert len(results) == 1
                assert '/scholarship/native-scholarship' in results[0].url


def test_parse_calls_pagination_method(mock_response):
    """Test parse method calls parse_pagination."""
    spider = NativeAmericanSpider()
    spider.pages_visited = 0
    spider, mock_logger = patch_spider_logger(spider)
    
    html = "<html><body></body></html>"
    
    response = mock_response(
        url='https://www.aises.org/scholarships',
        body=html
    )
    
    pagination_result = [
        scrapy.Request(url='https://www.aises.org/scholarships?page=2')
    ]
    
    with patch.object(spider, 'parse_pagination', return_value=pagination_result):
        results = list(spider.parse(response))
        
        assert len(results) == 1
        assert results[0].url == 'https://www.aises.org/scholarships?page=2'


# ----------------------- NativeAmericanSpider.parse_scholarship tests -----------------------

def test_parse_scholarship_calls_extract_by_source(mock_response):
    """Test parse_scholarship calls the extract_*_by_source methods."""
    spider = NativeAmericanSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <h1 class="scholarship-title">AISES Engineering Scholarship</h1>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.aises.org/scholarship/engineering',
        body=html
    )
    response.meta['source_domain'] = 'www.aises.org'
    
    with patch.object(spider, 'extract_with_selectors', return_value='AISES Engineering Scholarship'):
        with patch.object(spider, 'extract_description_by_source', return_value='Description text'):
            with patch.object(spider, 'extract_amount_by_source', return_value='$5,000'):
                with patch.object(spider, 'extract_deadline_by_source', return_value='April 30, 2026'):
                    with patch.object(spider, 'extract_eligibility_by_source', return_value='Eligibility text'):
                        with patch.object(spider, 'extract_requirements_by_source', return_value='Requirements text'):
                            with patch.object(spider, 'extract_amount_from_text', return_value='$5,000'):
                                with patch.object(spider, 'extract_deadline_from_text', return_value='2026-04-30'):
                                    with patch.object(spider, 'determine_provider_by_domain', return_value='AISES'):
                                        with patch.object(spider, 'create_scholarship_item') as mock_create_item:
                                            mock_create_item.return_value = {'title': 'AISES Engineering Scholarship'}
                                            
                                            results = list(spider.parse_scholarship(response))
                                            
                                            assert len(results) == 1
                                            
                                            # Verify that all extraction methods were called with the source_domain
                                            spider.extract_description_by_source.assert_called_once_with(response, 'www.aises.org')
                                            spider.extract_amount_by_source.assert_called_once_with(response, 'www.aises.org')
                                            spider.extract_deadline_by_source.assert_called_once_with(response, 'www.aises.org')
                                            spider.extract_eligibility_by_source.assert_called_once_with(response, 'www.aises.org')
                                            spider.extract_requirements_by_source.assert_called_once_with(response, 'www.aises.org')
                                            spider.determine_provider_by_domain.assert_called_once_with('www.aises.org')


def test_parse_scholarship_no_title_found(mock_response):
    """Test parse_scholarship method when no title is found."""
    spider = NativeAmericanSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <!-- No title element -->
            <div class="description">
                <p>This scholarship has no title.</p>
            </div>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.aises.org/scholarship/notitle',
        body=html
    )
    response.meta['source_domain'] = 'www.aises.org'
    
    with patch.object(spider, 'extract_with_selectors', return_value=None):
        results = list(spider.parse_scholarship(response))
        
        assert len(results) == 0  # Should not yield an item
        spider.logger.warning.assert_called_once()  # Should log a warning


def test_parse_scholarship_extracts_tags(mock_response):
    """Test parse_scholarship adds appropriate tags."""
    spider = NativeAmericanSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    html = """
    <html>
        <body>
            <h1>Native American Scholarship</h1>
        </body>
    </html>
    """
    
    response = mock_response(
        url='https://www.aises.org/scholarship/general',
        body=html
    )
    response.meta['source_domain'] = 'www.aises.org'
    
    with patch.object(spider, 'extract_with_selectors', return_value='Native American Scholarship'):
        with patch.object(spider, 'extract_description_by_source', return_value='Description'):
            with patch.object(spider, 'extract_amount_by_source', return_value='$3,000'):
                with patch.object(spider, 'extract_deadline_by_source', return_value='May 1, 2026'):
                    with patch.object(spider, 'extract_eligibility_by_source', return_value='Eligibility'):
                        with patch.object(spider, 'extract_requirements_by_source', return_value='Requirements'):
                            with patch.object(spider, 'extract_amount_from_text', return_value='$3,000'):
                                with patch.object(spider, 'extract_deadline_from_text', return_value='2026-05-01'):
                                    with patch.object(spider, 'determine_provider_by_domain', return_value='AISES'):
                                        with patch.object(spider, 'create_scholarship_item') as mock_create_item:
                                            mock_create_item.return_value = {'title': 'Native American Scholarship'}
                                            
                                            list(spider.parse_scholarship(response))
                                            
                                            # Verify tags were included
                                            call_kwargs = mock_create_item.call_args[1]
                                            assert 'tags' in call_kwargs
                                            assert 'Native American' in call_kwargs['tags']
                                            assert 'Indigenous' in call_kwargs['tags']
                                            assert 'Tribal' in call_kwargs['tags']


# ----------------------- Extract by source method tests -----------------------

def test_extract_description_by_source_aises():
    """Test extract_description_by_source for AISES website."""
    spider = NativeAmericanSpider()
    
    # Mock response for AISES
    response = MagicMock()
    response.css.side_effect = lambda selector: {
        '.scholarship-description p::text': MagicMock(getall=lambda: ['Description paragraph 1', 'Description paragraph 2']),
        '.program-content p::text': MagicMock(getall=lambda: []),
        '.content-area p::text': MagicMock(getall=lambda: []),
    }.get(selector, MagicMock(getall=lambda: []))
    
    description = spider.extract_description_by_source(response, 'www.aises.org')
    
    assert description == 'Description paragraph 1 Description paragraph 2'


def test_extract_description_by_source_collegefund():
    """Test extract_description_by_source for collegefund website."""
    spider = NativeAmericanSpider()
    
    # Mock response for collegefund
    response = MagicMock()
    response.css.side_effect = lambda selector: {
        '.scholarship-description p::text': MagicMock(getall=lambda: []),
        '.program-content p::text': MagicMock(getall=lambda: ['Program content paragraph']),
        '.content-area p::text': MagicMock(getall=lambda: []),
    }.get(selector, MagicMock(getall=lambda: []))
    
    description = spider.extract_description_by_source(response, 'collegefund.org')
    
    assert description == 'Program content paragraph'


def test_extract_amount_by_source():
    """Test extract_amount_by_source with different sources."""
    spider = NativeAmericanSpider()
    
    # Test for different domains
    domains = ['www.aises.org', 'collegefund.org', 'www.naja.com']
    selectors = ['.award-amount::text', '.scholarship-amount::text', '.value::text']
    
    for i, domain in enumerate(domains):
        response = MagicMock()
        response.css.side_effect = lambda selector: {
            selectors[i]: MagicMock(get=lambda: '$5,000'),
        }.get(selector, MagicMock(get=lambda: None))
        
        amount = spider.extract_amount_by_source(response, domain)
        
        assert amount == '$5,000'


def test_determine_provider_by_domain():
    """Test get_provider_by_domain with different domains."""
    spider = NativeAmericanSpider()
    
    assert spider.get_provider_by_domain('www.aises.org') == 'American Indian Science and Engineering Society'
    assert spider.get_provider_by_domain('www.naja.com') == 'Native American Journalists Association'
    assert spider.get_provider_by_domain('collegefund.org') == 'American Indian College Fund'
    assert spider.get_provider_by_domain('www.aianta.org') == 'American Indian Alaska Native Tourism Association'
    assert spider.get_provider_by_domain('unknown.org') == 'Native American Scholarship Organization'


# ----------------------- Integration tests -----------------------

def test_integration_scholarship_extraction_by_domain(mock_response):
    """Test integration of domain-specific extraction methods."""
    # Test with AISES domain
    html = """
    <html>
        <body>
            <h1 class="scholarship-title">AISES STEM Scholarship</h1>
            <div class="scholarship-description">
                <p>This is a scholarship for Native American students in STEM fields.</p>
            </div>
            <div class="award-amount">$5,000</div>
            <div class="application-deadline">April 30, 2026</div>
            <div class="eligibility">
                <p>Must be enrolled in a federally recognized tribe</p>
            </div>
        </body>
    </html>
    """
    
    spider = NativeAmericanSpider()
    spider, mock_logger = patch_spider_logger(spider)
    
    response = mock_response(
        url='https://www.aises.org/scholarship/stem',
        body=html
    )
    response.meta['source_domain'] = 'www.aises.org'
    
    with patch.object(spider, 'extract_amount_from_text', return_value='$5,000'):
        with patch.object(spider, 'extract_deadline_from_text', return_value='2026-04-30'):
            with patch.object(spider, 'create_scholarship_item') as mock_create_item:
                mock_create_item.return_value = {'title': 'AISES STEM Scholarship'}
                
                results = list(spider.parse_scholarship(response))
                
                assert len(results) == 1
                
                # Verify that the correct provider was determined
                call_kwargs = mock_create_item.call_args[1]
                assert call_kwargs['provider'] == 'American Indian Science and Engineering Society'
