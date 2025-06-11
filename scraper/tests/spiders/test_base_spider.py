"""
Tests for the base spider module.

This module contains tests for the BaseScholarshipSpider class and its methods.
Test coverage includes:
- URL cleaning and normalization
- Text extraction methods
- Scholarship item creation
- URL filtering
- Pagination handling
"""

import pytest
import scrapy
import re
from unittest.mock import MagicMock, patch
from urllib.parse import urljoin

from scraper.spiders.base import BaseScholarshipSpider
from scraper.items import ScholarshipItem
from tests.utils.test_response import TestHtmlResponse
from tests.spiders.mock_spider import patch_spider_logger


# ----------------------- BaseScholarshipSpider initialization tests -----------------------

def test_base_spider_initialization():
    """Test BaseScholarshipSpider initialization."""
    spider = BaseScholarshipSpider()
    
    assert spider.name == 'base_scholarship'
    assert hasattr(spider, 'COMMON_SELECTORS')
    assert isinstance(spider.COMMON_SELECTORS, dict)
    assert spider.items_scraped == 0
    assert spider.pages_visited == 0

def test_base_spider_common_selectors():
    """Test BaseScholarshipSpider common selectors."""
    spider = BaseScholarshipSpider()
    
    # Check that common selectors exist
    assert 'title' in spider.COMMON_SELECTORS
    assert 'description' in spider.COMMON_SELECTORS
    assert 'amount' in spider.COMMON_SELECTORS
    assert 'deadline' in spider.COMMON_SELECTORS
    assert 'requirements' in spider.COMMON_SELECTORS
    
    # Check that selectors are lists
    assert isinstance(spider.COMMON_SELECTORS['title'], list)
    assert isinstance(spider.COMMON_SELECTORS['description'], list)
    assert isinstance(spider.COMMON_SELECTORS['amount'], list)
    assert isinstance(spider.COMMON_SELECTORS['deadline'], list)
    assert isinstance(spider.COMMON_SELECTORS['requirements'], list)


# ----------------------- start_requests method tests -----------------------

def test_start_requests_method():
    """Test start_requests method."""
    spider = BaseScholarshipSpider()
    spider.start_urls = ['https://example.com/scholarships']
    
    requests = list(spider.start_requests())
    
    assert len(requests) == 1
    assert requests[0].url == 'https://example.com/scholarships'
    assert requests[0].callback == spider.parse
    assert requests[0].meta == {'page_number': 1}

def test_start_requests_with_multiple_urls():
    """Test start_requests with multiple URLs."""
    spider = BaseScholarshipSpider()
    spider.start_urls = [
        'https://example.com/scholarships/page1',
        'https://example.com/scholarships/page2'
    ]
    
    requests = list(spider.start_requests())
    
    assert len(requests) == 2
    assert requests[0].url == 'https://example.com/scholarships/page1'
    assert requests[1].url == 'https://example.com/scholarships/page2'
    assert requests[0].meta == {'page_number': 1}
    assert requests[1].meta == {'page_number': 1}


# ----------------------- parse method tests -----------------------

def test_parse_method_returns_empty_list():
    """Test parse method returns empty list."""
    spider = BaseScholarshipSpider()
    response = MagicMock()
    
    results = list(spider.parse(response))
    
    assert len(results) == 0


# ----------------------- extract_with_selectors method tests -----------------------

def test_extract_with_selectors_first_selector_works(mock_response):
    """Test extract_with_selectors when first selector works."""
    spider = BaseScholarshipSpider()
    html = '<div class="title">Test Scholarship</div>'
    response = mock_response(body=html)
    
    selectors = ['.title::text', '.scholarship-title::text']
    result = spider.extract_with_selectors(response, 'title', selectors)
    
    assert result == 'Test Scholarship'

def test_extract_with_selectors_second_selector_works(mock_response):
    """Test extract_with_selectors when second selector works."""
    spider = BaseScholarshipSpider()
    html = '<div class="scholarship-title">Test Scholarship</div>'
    response = mock_response(body=html)
    
    selectors = ['.title::text', '.scholarship-title::text']
    result = spider.extract_with_selectors(response, 'title', selectors)
    
    assert result == 'Test Scholarship'

def test_extract_with_selectors_no_selector_works(mock_response):
    """Test extract_with_selectors when no selector works."""
    spider = BaseScholarshipSpider()
    html = '<div class="other">Test Scholarship</div>'
    response = mock_response(body=html)
    
    selectors = ['.title::text', '.scholarship-title::text']
    result = spider.extract_with_selectors(response, 'title', selectors)
    
    assert result == ""

def test_extract_with_selectors_default_selectors(mock_response):
    """Test extract_with_selectors using default selectors."""
    spider = BaseScholarshipSpider()
    html = '<h1>Test Scholarship</h1>'
    response = mock_response(body=html)
    
    # Use default selector from COMMON_SELECTORS
    result = spider.extract_with_selectors(response, 'title')
    
    assert result == 'Test Scholarship'

def test_extract_with_selectors_empty_html(mock_response):
    """Test extract_with_selectors with empty HTML."""
    spider = BaseScholarshipSpider()
    response = mock_response(body="")
    
    result = spider.extract_with_selectors(response, 'title')
    
    assert result == ""

def test_extract_with_selectors_error_handling(mock_response):
    """Test extract_with_selectors error handling."""
    spider = BaseScholarshipSpider()
    html = '<div class="title">Test Scholarship</div>'
    response = mock_response(body=html)
    
    # Intentionally cause an error with invalid selector
    selectors = ['::invalid::']
    
    # Should not raise exception and return empty string
    result = spider.extract_with_selectors(response, 'title', selectors)
    assert result == ""


# ----------------------- extract_multiple_with_selectors method tests -----------------------

def test_extract_multiple_with_selectors_first_selector_works(mock_response):
    """Test extract_multiple_with_selectors when first selector works."""
    spider = BaseScholarshipSpider()
    html = """
    <ul class="requirements">
        <li>Requirement 1</li>
        <li>Requirement 2</li>
        <li>Requirement 3</li>
    </ul>
    """
    response = mock_response(body=html)
    
    selectors = ['.requirements li::text', '.eligibility li::text']
    result = spider.extract_multiple_with_selectors(response, 'requirements', selectors)
    
    assert result == ['Requirement 1', 'Requirement 2', 'Requirement 3']

def test_extract_multiple_with_selectors_second_selector_works(mock_response):
    """Test extract_multiple_with_selectors when second selector works."""
    spider = BaseScholarshipSpider()
    html = """
    <ul class="eligibility">
        <li>Requirement 1</li>
        <li>Requirement 2</li>
    </ul>
    """
    response = mock_response(body=html)
    
    selectors = ['.requirements li::text', '.eligibility li::text']
    result = spider.extract_multiple_with_selectors(response, 'requirements', selectors)
    
    assert result == ['Requirement 1', 'Requirement 2']

def test_extract_multiple_with_selectors_no_selector_works(mock_response):
    """Test extract_multiple_with_selectors when no selector works."""
    spider = BaseScholarshipSpider()
    html = """
    <ul class="other">
        <li>Requirement 1</li>
    </ul>
    """
    response = mock_response(body=html)
    
    selectors = ['.requirements li::text', '.eligibility li::text']
    result = spider.extract_multiple_with_selectors(response, 'requirements', selectors)
    
    assert result == []

def test_extract_multiple_with_selectors_default_selectors(mock_response):
    """Test extract_multiple_with_selectors using default selectors."""
    spider = BaseScholarshipSpider()
    html = """
    <div class="requirements">Requirement 1</div>
    """
    response = mock_response(body=html)
    
    # Use default selector from COMMON_SELECTORS
    result = spider.extract_multiple_with_selectors(response, 'requirements')
    
    assert len(result) > 0
    assert 'Requirement 1' in result[0]

def test_extract_multiple_with_selectors_empty_html(mock_response):
    """Test extract_multiple_with_selectors with empty HTML."""
    spider = BaseScholarshipSpider()
    response = mock_response(body="")
    
    result = spider.extract_multiple_with_selectors(response, 'requirements')
    
    assert result == []


# ----------------------- clean_url method tests -----------------------

def test_clean_url_absolute_url():
    """Test clean_url with absolute URL."""
    spider = BaseScholarshipSpider()
    url = 'https://example.com/scholarships'
    response_url = 'https://example.com'
    
    result = spider.clean_url(url, response_url)
    
    assert result == 'https://example.com/scholarships'

def test_clean_url_root_relative_url():
    """Test clean_url with root-relative URL."""
    spider = BaseScholarshipSpider()
    url = '/scholarships'
    response_url = 'https://example.com'
    
    result = spider.clean_url(url, response_url)
    
    assert result == 'https://example.com/scholarships'

def test_clean_url_relative_url():
    """Test clean_url with relative URL."""
    spider = BaseScholarshipSpider()
    url = 'scholarships'
    response_url = 'https://example.com/'
    
    result = spider.clean_url(url, response_url)
    
    assert result == 'https://example.com/scholarships'

def test_clean_url_empty_url():
    """Test clean_url with empty URL."""
    spider = BaseScholarshipSpider()
    url = ''
    response_url = 'https://example.com'
    
    result = spider.clean_url(url, response_url)
    
    assert result == ""

def test_clean_url_none_url():
    """Test clean_url with None URL."""
    spider = BaseScholarshipSpider()
    url = None
    response_url = 'https://example.com'
    
    result = spider.clean_url(url, response_url)
    
    assert result == ""

def test_clean_url_with_whitespace():
    """Test clean_url with whitespace."""
    spider = BaseScholarshipSpider()
    url = '  https://example.com/scholarships  '
    response_url = 'https://example.com'
    
    result = spider.clean_url(url, response_url)
    
    assert result == 'https://example.com/scholarships'

def test_clean_url_with_complex_path():
    """Test clean_url with complex path."""
    spider = BaseScholarshipSpider()
    url = '../scholarships/science'
    response_url = 'https://example.com/categories/'
    
    result = spider.clean_url(url, response_url)
    
    assert result == 'https://example.com/scholarships/science'


# ----------------------- extract_amount_from_text method tests -----------------------

def test_extract_amount_from_text_with_dollar_sign():
    """Test extract_amount_from_text with dollar sign."""
    spider = BaseScholarshipSpider()
    text = 'The scholarship amount is $5,000.'
    
    result = spider.extract_amount_from_text(text)
    
    assert result == '$5,000'

def test_extract_amount_from_text_with_dollars_word():
    """Test extract_amount_from_text with 'dollars' word."""
    spider = BaseScholarshipSpider()
    text = 'The scholarship amount is 5,000 dollars.'
    
    result = spider.extract_amount_from_text(text)
    
    assert result == '5,000 dollars'

def test_extract_amount_from_text_with_up_to():
    """Test extract_amount_from_text with 'up to'."""
    spider = BaseScholarshipSpider()
    text = 'The scholarship awards up to $5,000.'
    
    result = spider.extract_amount_from_text(text)
    
    assert result == 'up to $5,000'

def test_extract_amount_from_text_with_maximum():
    """Test extract_amount_from_text with 'maximum'."""
    spider = BaseScholarshipSpider()
    text = 'The scholarship has a maximum $5,000 award.'
    
    result = spider.extract_amount_from_text(text)
    
    assert result == 'maximum $5,000'

def test_extract_amount_from_text_with_usd():
    """Test extract_amount_from_text with 'USD'."""
    spider = BaseScholarshipSpider()
    text = 'The scholarship amount is 5,000 USD.'
    
    result = spider.extract_amount_from_text(text)
    
    assert result == '5,000 USD'

def test_extract_amount_from_text_with_no_pattern():
    """Test extract_amount_from_text with no pattern match."""
    spider = BaseScholarshipSpider()
    text = 'The scholarship amount varies.'
    
    result = spider.extract_amount_from_text(text)
    
    # Should try to find any number
    assert result == text.strip()

def test_extract_amount_from_text_with_number_only():
    """Test extract_amount_from_text with number only."""
    spider = BaseScholarshipSpider()
    text = 'The scholarship amount is 5000.'
    
    result = spider.extract_amount_from_text(text)
    
    assert result == '$5000'

def test_extract_amount_from_text_empty():
    """Test extract_amount_from_text with empty text."""
    spider = BaseScholarshipSpider()
    text = ''
    
    result = spider.extract_amount_from_text(text)
    
    assert result == ""

def test_extract_amount_from_text_none():
    """Test extract_amount_from_text with None."""
    spider = BaseScholarshipSpider()
    text = None
    
    result = spider.extract_amount_from_text(text)
    
    assert result == ""


# ----------------------- extract_deadline_from_text method tests -----------------------

def test_extract_deadline_from_text_mm_dd_yyyy():
    """Test extract_deadline_from_text with MM/DD/YYYY format."""
    spider = BaseScholarshipSpider()
    text = 'Application deadline: 01/15/2026'
    
    result = spider.extract_deadline_from_text(text)
    
    assert result == '01/15/2026'

def test_extract_deadline_from_text_yyyy_mm_dd():
    """Test extract_deadline_from_text with YYYY-MM-DD format."""
    spider = BaseScholarshipSpider()
    text = 'Application deadline: 2026-01-15'
    
    result = spider.extract_deadline_from_text(text)
    
    assert result == '2026-01-15'

def test_extract_deadline_from_text_month_dd_yyyy():
    """Test extract_deadline_from_text with Month DD, YYYY format."""
    spider = BaseScholarshipSpider()
    text = 'Application deadline: January 15, 2026'
    
    result = spider.extract_deadline_from_text(text)
    
    assert result == 'January 15, 2026'

def test_extract_deadline_from_text_dd_month_yyyy():
    """Test extract_deadline_from_text with DD Month YYYY format."""
    spider = BaseScholarshipSpider()
    text = 'Application deadline: 15 January 2026'
    
    result = spider.extract_deadline_from_text(text)
    
    assert result == '15 January 2026'

def test_extract_deadline_from_text_no_pattern():
    """Test extract_deadline_from_text with no pattern match."""
    spider = BaseScholarshipSpider()
    text = 'Application deadline: TBA'
    
    result = spider.extract_deadline_from_text(text)
    
    assert result == text.strip()

def test_extract_deadline_from_text_empty():
    """Test extract_deadline_from_text with empty text."""
    spider = BaseScholarshipSpider()
    text = ''
    
    result = spider.extract_deadline_from_text(text)
    
    assert result == ""

def test_extract_deadline_from_text_none():
    """Test extract_deadline_from_text with None."""
    spider = BaseScholarshipSpider()
    text = None
    
    result = spider.extract_deadline_from_text(text)
    
    assert result == ""


# ----------------------- create_scholarship_item method tests -----------------------

def test_create_scholarship_item_basic():
    """Test create_scholarship_item with basic fields."""
    spider = BaseScholarshipSpider()
    response = MagicMock()
    response.url = 'https://example.com/scholarship'
    
    item = spider.create_scholarship_item(
        response,
        title='Test Scholarship',
        amount='$5,000',
        deadline='2026-01-15'
    )
    
    assert item['title'] == 'Test Scholarship'
    assert item['amount'] == '$5,000'
    assert item['deadline'] == '2026-01-15'
    assert item['source_url'] == 'https://example.com/scholarship'
    assert item['source'] == 'base_scholarship'
    assert spider.items_scraped == 1

def test_create_scholarship_item_all_fields():
    """Test create_scholarship_item with all fields."""
    spider = BaseScholarshipSpider()
    response = MagicMock()
    response.url = 'https://example.com/scholarship'
    
    item = spider.create_scholarship_item(
        response,
        title='Test Scholarship',
        description='Scholarship description',
        amount='$5,000',
        deadline='2026-01-15',
        eligibility='Full-time student | GPA 3.0+',
        requirements='Application | Essay | Recommendations',
        application_url='https://example.com/apply',
        provider='Test Provider',
        category='STEM',
        tags=['Science', 'Technology']
    )
    
    assert item['title'] == 'Test Scholarship'
    assert item['description'] == 'Scholarship description'
    assert item['amount'] == '$5,000'
    assert item['deadline'] == '2026-01-15'
    assert item['eligibility'] == 'Full-time student | GPA 3.0+'
    assert item['requirements'] == 'Application | Essay | Recommendations'
    assert item['application_url'] == 'https://example.com/apply'
    assert item['provider'] == 'Test Provider'
    assert item['category'] == 'STEM'
    assert item['tags'] == ['Science', 'Technology']
    assert item['source_url'] == 'https://example.com/scholarship'
    assert item['source'] == 'base_scholarship'
    assert spider.items_scraped == 1

def test_create_scholarship_item_invalid_field():
    """Test create_scholarship_item with invalid field."""
    spider = BaseScholarshipSpider()
    response = MagicMock()
    response.url = 'https://example.com/scholarship'
    
    item = spider.create_scholarship_item(
        response,
        title='Test Scholarship',
        invalid_field='Invalid'  # This field doesn't exist in ScholarshipItem
    )
    
    assert item['title'] == 'Test Scholarship'
    assert 'invalid_field' not in item
    assert item['source_url'] == 'https://example.com/scholarship'
    assert item['source'] == 'base_scholarship'
    assert spider.items_scraped == 1


# ----------------------- should_follow_link method tests -----------------------

def test_should_follow_link_valid_url():
    """Test should_follow_link with valid URL."""
    spider = BaseScholarshipSpider()
    url = 'https://example.com/scholarship'
    
    result = spider.should_follow_link(url)
    
    assert result == True

def test_should_follow_link_empty_url():
    """Test should_follow_link with empty URL."""
    spider = BaseScholarshipSpider()
    url = ''
    
    result = spider.should_follow_link(url)
    
    assert result == False

def test_should_follow_link_none_url():
    """Test should_follow_link with None URL."""
    spider = BaseScholarshipSpider()
    url = None
    
    result = spider.should_follow_link(url)
    
    assert result == False

def test_should_follow_link_pdf_url():
    """Test should_follow_link with PDF URL."""
    spider = BaseScholarshipSpider()
    url = 'https://example.com/document.pdf'
    
    result = spider.should_follow_link(url)
    
    assert result == False

def test_should_follow_link_doc_url():
    """Test should_follow_link with DOC URL."""
    spider = BaseScholarshipSpider()
    url = 'https://example.com/document.docx'
    
    result = spider.should_follow_link(url)
    
    assert result == False

def test_should_follow_link_login_url():
    """Test should_follow_link with login URL."""
    spider = BaseScholarshipSpider()
    url = 'https://example.com/login'
    
    result = spider.should_follow_link(url)
    
    assert result == False

def test_should_follow_link_register_url():
    """Test should_follow_link with register URL."""
    spider = BaseScholarshipSpider()
    url = 'https://example.com/register'
    
    result = spider.should_follow_link(url)
    
    assert result == False

def test_should_follow_link_contact_url():
    """Test should_follow_link with contact URL."""
    spider = BaseScholarshipSpider()
    url = 'https://example.com/contact'
    
    result = spider.should_follow_link(url)
    
    assert result == False

def test_should_follow_link_privacy_url():
    """Test should_follow_link with privacy URL."""
    spider = BaseScholarshipSpider()
    url = 'https://example.com/privacy'
    
    result = spider.should_follow_link(url)
    
    assert result == False

def test_should_follow_link_terms_url():
    """Test should_follow_link with terms URL."""
    spider = BaseScholarshipSpider()
    url = 'https://example.com/terms'
    
    result = spider.should_follow_link(url)
    
    assert result == False

def test_should_follow_link_javascript_url():
    """Test should_follow_link with javascript URL."""
    spider = BaseScholarshipSpider()
    url = 'javascript:void(0)'
    
    result = spider.should_follow_link(url)
    
    assert result == False

def test_should_follow_link_mailto_url():
    """Test should_follow_link with mailto URL."""
    spider = BaseScholarshipSpider()
    url = 'mailto:info@example.com'
    
    result = spider.should_follow_link(url)
    
    assert result == False

def test_should_follow_link_tel_url():
    """Test should_follow_link with tel URL."""
    spider = BaseScholarshipSpider()
    url = 'tel:1234567890'
    
    result = spider.should_follow_link(url)
    
    assert result == False


# ----------------------- parse_pagination method tests -----------------------

def test_parse_pagination_no_links(mock_response):
    """Test parse_pagination with no links."""
    spider = BaseScholarshipSpider()
    html = '<div>No pagination links</div>'
    response = TestHtmlResponse(
        url='https://example.com',
        body=html.encode('utf-8'),
        encoding='utf-8',
        meta={'page_number': 1}
    )
    
    results = list(spider.parse_pagination(response))
    
    assert len(results) == 0

def test_parse_pagination_with_page_links(mock_response):
    """Test parse_pagination with page links."""
    spider = BaseScholarshipSpider()
    html = """
    <div class="pagination">
        <a href="/page/1">1</a>
        <a href="/page/2">2</a>
        <a href="/page/3">3</a>
    </div>
    """
    response = mock_response(body=html, url='https://example.com')
    response.meta = {'page_number': 1}
    
    results = list(spider.parse_pagination(response))
    
    # Should only follow the first link (avoid too many requests in test)
    assert len(results) == 1
    assert results[0].url == 'https://example.com/page/1'
    assert results[0].callback == spider.parse
    assert results[0].meta == {'page_number': 2}

def test_parse_pagination_with_next_link(mock_response):
    """Test parse_pagination with next link."""
    spider = BaseScholarshipSpider()
    html = """
    <div class="pagination">
        <a href="/page/1">1</a>
        <a href="/page/2">2</a>
        <a href="/page/3">Next</a>
    </div>
    """
    response = mock_response(body=html, url='https://example.com')
    response.meta = {'page_number': 1}
    
    results = list(spider.parse_pagination(response))
    
    # Should only follow the first link (avoid too many requests in test)
    assert len(results) == 1
    assert results[0].url == 'https://example.com/page/1'
    assert results[0].callback == spider.parse
    assert results[0].meta == {'page_number': 2}


# ----------------------- closed method tests -----------------------

def test_closed_method_logs_statistics():
    """Test closed method logs statistics."""
    spider = BaseScholarshipSpider()
    spider.pages_visited = 10
    spider.items_scraped = 20
    
    # Use patch_spider_logger to mock the logger
    spider, mock_logger = patch_spider_logger(spider)
    
    # Create mock crawler with stats
    spider.crawler = MagicMock()
    spider.crawler.stats.get_stats.return_value = {
        'downloader/request_count': 30,
        'downloader/response_status_count/200': 28,
        'downloader/response_status_count/404': 2,
        'item_scraped_count': 20,
        'item_dropped_count': 1
    }
    
    spider.closed('finished')
    
    # Check that logger was called with appropriate messages
    mock_logger.info.assert_any_call("Spider closed: finished")
    mock_logger.info.assert_any_call("Pages visited: 10")
    mock_logger.info.assert_any_call("Items scraped: 20")


# ----------------------- Integration tests -----------------------

def test_integration_extract_with_response(mock_response, sample_html):
    """Test integration of extraction methods with response."""
    spider = BaseScholarshipSpider()
    response = mock_response(body=sample_html)
    
    # Extract fields
    title = spider.extract_with_selectors(response, 'title', ['h1::text'])
    amount = spider.extract_with_selectors(response, 'amount', ['.amount::text'])
    deadline = spider.extract_with_selectors(response, 'deadline', ['.deadline::text'])
    eligibility = spider.extract_multiple_with_selectors(response, 'eligibility', ['.eligibility li::text'])
    requirements = spider.extract_multiple_with_selectors(response, 'requirements', ['.requirements li::text'])
    
    # Create item
    item = spider.create_scholarship_item(
        response,
        title=title,
        amount=amount,
        deadline=deadline,
        eligibility=' | '.join(eligibility),
        requirements=' | '.join(requirements)
    )
    
    # Validate
    assert title == 'Sample Scholarship'
    assert amount == '$5,000'
    assert deadline == 'January 15, 2026'
    assert 'Must be a full-time student' in eligibility
    assert 'GPA of 3.0 or higher' in eligibility
    assert 'Application form' in requirements
    assert 'Essay' in requirements
    assert 'Letters of recommendation' in requirements
    
    assert item['title'] == 'Sample Scholarship'
    assert item['amount'] == '$5,000'
    assert item['deadline'] == 'January 15, 2026'
    assert 'Must be a full-time student' in item['eligibility']
    assert 'GPA of 3.0 or higher' in item['eligibility']
    assert 'Application form' in item['requirements']
    assert 'Essay' in item['requirements']
    assert 'Letters of recommendation' in item['requirements']
