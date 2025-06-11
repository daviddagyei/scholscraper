"""
Tests for the base spider pagination functionality.

This module contains tests for the BaseScholarshipSpider pagination methods.
"""

import scrapy
from unittest.mock import MagicMock

from scraper.spiders.base import BaseScholarshipSpider
from tests.spiders.mock_spider import patch_spider_logger
from tests.utils.test_response import TestHtmlResponse

def test_parse_pagination_no_links():
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

def test_parse_pagination_with_page_links():
    """Test parse_pagination with page links."""
    spider = BaseScholarshipSpider()
    html = """
    <div class="pagination">
        <a href="/page/1">1</a>
        <a href="/page/2">2</a>
        <a href="/page/3">3</a>
    </div>
    """
    response = TestHtmlResponse(
        url='https://example.com',
        body=html.encode('utf-8'),
        encoding='utf-8',
        meta={'page_number': 1}
    )
    
    results = list(spider.parse_pagination(response))
    
    assert len(results) > 0

def test_parse_pagination_with_next_link():
    """Test parse_pagination with next link."""
    spider = BaseScholarshipSpider()
    html = """
    <div class="pagination">
        <a href="/page/1">1</a>
        <a href="/page/2">2</a>
        <a href="/page/3">Next</a>
    </div>
    """
    response = TestHtmlResponse(
        url='https://example.com',
        body=html.encode('utf-8'),
        encoding='utf-8',
        meta={'page_number': 1}
    )
    
    results = list(spider.parse_pagination(response))
    
    assert len(results) > 0
