"""
Shared fixtures and configuration for pytest.

This module contains shared fixtures and configuration used across multiple test modules.
"""

import pytest
import os
import sys
import scrapy
import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Fixture for sample HTML content
@pytest.fixture
def sample_html():
    """Sample HTML content for testing text extraction."""
    return """
    <html>
        <body>
            <h1>Sample Scholarship</h1>
            <div class="description">
                <p>This is a scholarship for students.</p>
                <p>It provides financial assistance.</p>
            </div>
            <div class="amount">$5,000</div>
            <div class="deadline">January 15, 2026</div>
            <div class="eligibility">
                <ul>
                    <li>Must be a full-time student</li>
                    <li>GPA of 3.0 or higher</li>
                </ul>
            </div>
            <div class="requirements">
                <ul>
                    <li>Application form</li>
                    <li>Essay</li>
                    <li>Letters of recommendation</li>
                </ul>
            </div>
            <a href="https://example.com/apply" class="apply-button">Apply Now</a>
        </body>
    </html>
    """

# Fixture for sample scholarship data
@pytest.fixture
def sample_scholarship_data():
    """Sample scholarship data for testing item processing."""
    return {
        'title': 'STEM Excellence Scholarship',
        'description': 'Scholarship for students pursuing STEM fields',
        'amount': '$5,000',
        'deadline': '2026-01-15',
        'eligibility': 'Full-time student | GPA 3.0+',
        'requirements': 'Application | Essay | Recommendations',
        'application_url': 'https://example.com/apply',
        'provider': 'STEM Foundation',
        'category': 'STEM',
        'source': 'test_spider',
        'source_url': 'https://example.com/scholarship',
        'tags': ['STEM', 'Engineering', 'Technology']
    }

# Fixture for mock response
@pytest.fixture
def mock_response():
    """Mock Scrapy Response object."""
    
    def _create_response(url="https://example.com", body="", request=None, status=200):
        if isinstance(body, str):
            body = body.encode('utf-8')
        
        request = request or scrapy.Request(url=url)
        return scrapy.http.HtmlResponse(
            url=url,
            body=body,
            encoding='utf-8',
            request=request,
            status=status
        )
    
    return _create_response

# Fixture for current date
@pytest.fixture
def current_date():
    """Current date for testing."""
    return datetime.datetime.now().strftime("%Y-%m-%d")

# Fixture for mock spider
@pytest.fixture
def mock_spider():
    """Mock spider for testing."""
    spider = scrapy.Spider('test_spider')
    spider.start_urls = ['https://example.com']
    spider.logger = scrapy.utils.log.create_logger(spider)
    return spider
