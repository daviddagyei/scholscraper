"""
Tests for the scrapy items module.

This module contains tests for scrapy item classes and their processors.
Test coverage includes:
- clean_text function
- clean_amount function
- parse_deadline function
- ScholarshipItem class and fields
"""

import pytest
import re
from datetime import datetime
from scrapy.item import Item
from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, Join, Identity, MapCompose
from w3lib.html import remove_tags

from scraper.items import clean_text, clean_amount, parse_deadline, ScholarshipItem


# ----------------------- clean_text function tests -----------------------

def test_clean_text_with_empty_string():
    """Test clean_text with empty string."""
    assert clean_text('') == ''
    assert clean_text(None) == ''

def test_clean_text_with_whitespace():
    """Test clean_text with whitespace."""
    assert clean_text('  test  ') == 'test'
    assert clean_text('\t\ttest\t\t') == 'test'
    assert clean_text('\n\ntest\n\n') == 'test'
    
def test_clean_text_with_multiple_spaces():
    """Test clean_text with multiple spaces."""
    assert clean_text('hello  world') == 'hello world'
    
def test_clean_text_with_newlines():
    """Test clean_text with newlines."""
    assert clean_text('hello\nworld') == 'hello world'
    
def test_clean_text_with_tabs():
    """Test clean_text with tabs."""
    assert clean_text('hello\tworld') == 'hello world'
    
def test_clean_text_with_mixed_whitespace():
    """Test clean_text with mixed whitespace."""
    assert clean_text('hello\n\t  world  \n') == 'hello world'
    
def test_clean_text_preserves_punctuation():
    """Test clean_text preserves punctuation."""
    assert clean_text('Hello, world!') == 'Hello, world!'
    
def test_clean_text_with_special_characters():
    """Test clean_text with special characters."""
    assert clean_text('$5,000 award!') == '$5,000 award!'
    
def test_clean_text_with_unicode_characters():
    """Test clean_text with unicode characters."""
    assert clean_text('Café au lait') == 'Café au lait'
    
def test_clean_text_with_html_entities():
    """Test clean_text with HTML entities."""
    assert clean_text('&lt;div&gt;Hello&lt;/div&gt;') == '&lt;div&gt;Hello&lt;/div&gt;'
    
def test_clean_text_multiple_paragraphs():
    """Test clean_text with multiple paragraphs."""
    text = '''First paragraph.
    
    Second paragraph.
    
    Third paragraph.'''
    expected = 'First paragraph. Second paragraph. Third paragraph.'
    assert clean_text(text) == expected


# ----------------------- clean_amount function tests -----------------------

def test_clean_amount_with_empty_string():
    """Test clean_amount with empty string."""
    assert clean_amount('') == ''
    assert clean_amount(None) == ''
    
def test_clean_amount_with_valid_dollar_amount():
    """Test clean_amount with valid dollar amount."""
    assert clean_amount('$5,000') == '$5,000'
    
def test_clean_amount_with_decimal():
    """Test clean_amount with decimal."""
    assert clean_amount('$5,000.50') == '$5,000.50'
    
def test_clean_amount_with_text_and_amount():
    """Test clean_amount with text and amount."""
    assert clean_amount('Award: $5,000') == '$5,000'
    
def test_clean_amount_with_multiple_amounts():
    """Test clean_amount with multiple amounts."""
    assert clean_amount('$1,000 - $5,000') == '$1,000-$5,000'
    
def test_clean_amount_without_dollar_sign():
    """Test clean_amount without dollar sign."""
    assert clean_amount('5000') == '5000'
    
def test_clean_amount_with_text_around_digits():
    """Test clean_amount with text around digits."""
    assert clean_amount('Up to 5,000 dollars') == '5,000'
    
def test_clean_amount_with_mixed_characters():
    """Test clean_amount with mixed characters."""
    assert clean_amount('Award$5,000!') == '$5,000'
    
def test_clean_amount_with_range():
    """Test clean_amount with range."""
    assert clean_amount('$1,000-$5,000') == '$1,000-$5,000'
    
def test_clean_amount_with_word_amount():
    """Test clean_amount with word amount."""
    assert clean_amount('five thousand dollars') == ''
    

# ----------------------- parse_deadline function tests -----------------------

def test_parse_deadline_with_empty_string():
    """Test parse_deadline with empty string."""
    assert parse_deadline('') == ''
    assert parse_deadline(None) == ''
    
def test_parse_deadline_with_iso_format():
    """Test parse_deadline with ISO format."""
    assert parse_deadline('2026-01-15') == '2026-01-15'
    
def test_parse_deadline_with_us_format():
    """Test parse_deadline with US format."""
    assert parse_deadline('01/15/2026') == '2026-01-15'
    
def test_parse_deadline_with_hyphenated_format():
    """Test parse_deadline with hyphenated format."""
    assert parse_deadline('01-15-2026') == '2026-01-15'
    
def test_parse_deadline_with_long_month_format():
    """Test parse_deadline with long month format."""
    assert parse_deadline('January 15, 2026') == '2026-01-15'
    
def test_parse_deadline_with_short_month_format():
    """Test parse_deadline with short month format."""
    assert parse_deadline('Jan 15, 2026') == '2026-01-15'
    
def test_parse_deadline_with_day_first_long_month():
    """Test parse_deadline with day first long month."""
    assert parse_deadline('15 January 2026') == '2026-01-15'
    
def test_parse_deadline_with_day_first_short_month():
    """Test parse_deadline with day first short month."""
    assert parse_deadline('15 Jan 2026') == '2026-01-15'
    
def test_parse_deadline_with_whitespace():
    """Test parse_deadline with whitespace."""
    assert parse_deadline('  2026-01-15  ') == '2026-01-15'
    
def test_parse_deadline_with_text_and_date():
    """Test parse_deadline with text and date."""
    assert parse_deadline('Deadline: January 15, 2026') == 'Deadline: January 15, 2026'
    
def test_parse_deadline_with_invalid_date():
    """Test parse_deadline with invalid date."""
    assert parse_deadline('Not a date') == 'Not a date'
    
def test_parse_deadline_month_out_of_range():
    """Test parse_deadline with month out of range."""
    assert parse_deadline('13/15/2026') == '13/15/2026'
    
def test_parse_deadline_day_out_of_range():
    """Test parse_deadline with day out of range."""
    assert parse_deadline('01/32/2026') == '01/32/2026'
    
def test_parse_deadline_feb_29_leap_year():
    """Test parse_deadline with Feb 29 in leap year."""
    assert parse_deadline('02/29/2024') == '2024-02-29'
    
def test_parse_deadline_feb_29_non_leap_year():
    """Test parse_deadline with Feb 29 in non-leap year."""
    assert parse_deadline('02/29/2025') == '02/29/2025'
    

# ----------------------- ScholarshipItem tests -----------------------

def test_scholarship_item_fields_existence():
    """Test that ScholarshipItem has all required fields."""
    item = ScholarshipItem()
    expected_fields = [
        'title', 'description', 'amount', 'deadline', 'eligibility', 'requirements',
        'application_url', 'provider', 'category', 'source', 'source_url',
        'scraped_date', 'last_updated', 'tags', 'is_active', 'item_id'
    ]
    
    for field in expected_fields:
        assert field in item.fields, f"Field {field} is missing"

def test_scholarship_item_processors_title():
    """Test ScholarshipItem title field processors."""
    field = ScholarshipItem.fields['title']
    
    # Check input processor
    assert MapCompose in field.get('input_processor', []).__class__.__mro__
    
    # Check output processor
    assert isinstance(field.get('output_processor', None), TakeFirst)

def test_scholarship_item_processors_description():
    """Test ScholarshipItem description field processors."""
    field = ScholarshipItem.fields['description']
    
    # Check input processor
    assert MapCompose in field.get('input_processor', []).__class__.__mro__
    
    # Check output processor
    assert isinstance(field.get('output_processor', None), Join)
    
def test_scholarship_item_processors_amount():
    """Test ScholarshipItem amount field processors."""
    field = ScholarshipItem.fields['amount']
    
    # Check input processor
    assert MapCompose in field.get('input_processor', []).__class__.__mro__
    
    # Check output processor
    assert isinstance(field.get('output_processor', None), TakeFirst)
    
def test_scholarship_item_processors_deadline():
    """Test ScholarshipItem deadline field processors."""
    field = ScholarshipItem.fields['deadline']
    
    # Check input processor
    assert MapCompose in field.get('input_processor', []).__class__.__mro__
    
    # Check output processor
    assert isinstance(field.get('output_processor', None), TakeFirst)
    
def test_create_and_populate_scholarship_item():
    """Test creating and populating a ScholarshipItem."""
    item = ScholarshipItem(
        title='Test Scholarship',
        amount='$5,000',
        deadline='2026-01-15',
        source='test'
    )
    
    assert item['title'] == 'Test Scholarship'
    assert item['amount'] == '$5,000'
    assert item['deadline'] == '2026-01-15'
    assert item['source'] == 'test'
    
def test_scholarship_item_with_html_in_title():
    """Test ScholarshipItem with HTML in title."""
    # Create a test loader
    class TestItemLoader(ItemLoader):
        default_item_class = ScholarshipItem
    
    loader = TestItemLoader()
    loader.add_value('title', '<b>Test Scholarship</b>')
    item = loader.load_item()
    
    assert item['title'] == 'Test Scholarship'
    
def test_scholarship_item_with_multiple_description_paragraphs():
    """Test ScholarshipItem with multiple description paragraphs."""
    # Create a test loader
    class TestItemLoader(ItemLoader):
        default_item_class = ScholarshipItem
    
    loader = TestItemLoader()
    loader.add_value('description', '<p>First paragraph.</p>')
    loader.add_value('description', '<p>Second paragraph.</p>')
    item = loader.load_item()
    
    assert item['description'] == 'First paragraph. Second paragraph.'
    
def test_scholarship_item_with_html_in_eligibility():
    """Test ScholarshipItem with HTML in eligibility."""
    # Create a test loader
    class TestItemLoader(ItemLoader):
        default_item_class = ScholarshipItem
    
    loader = TestItemLoader()
    loader.add_value('eligibility', '<li>Requirement 1</li>')
    loader.add_value('eligibility', '<li>Requirement 2</li>')
    item = loader.load_item()
    
    assert item['eligibility'] == 'Requirement 1 | Requirement 2'
    
def test_scholarship_item_with_empty_fields():
    """Test ScholarshipItem with empty fields."""
    item = ScholarshipItem()
    
    assert not item.get('title')
    assert not item.get('amount')
    assert not item.get('deadline')
    

# ----------------------- Combined processor tests -----------------------

def test_combined_processors_with_html_and_whitespace():
    """Test combined processors with HTML and whitespace."""
    html = '<div>  Test   \n  Scholarship  </div>'
    
    # Create a test loader
    class TestItemLoader(ItemLoader):
        default_item_class = ScholarshipItem
    
    loader = TestItemLoader()
    loader.add_value('title', html)
    item = loader.load_item()
    
    assert item['title'] == 'Test Scholarship'
    
def test_combined_processors_with_html_and_amount():
    """Test combined processors with HTML and amount."""
    html = '<div>Award: $5,000!</div>'
    
    # Create a test loader
    class TestItemLoader(ItemLoader):
        default_item_class = ScholarshipItem
    
    loader = TestItemLoader()
    loader.add_value('amount', html)
    item = loader.load_item()
    
    assert item['amount'] == '$5,000'
    
def test_combined_processors_with_html_and_deadline():
    """Test combined processors with HTML and deadline."""
    html = '<div>January 15, 2026</div>'
    
    # Create a test loader
    class TestItemLoader(ItemLoader):
        default_item_class = ScholarshipItem
    
    loader = TestItemLoader()
    loader.add_value('deadline', html)
    item = loader.load_item()
    
    assert item['deadline'] == '2026-01-15'

# ----------------------- Complete item creation tests -----------------------

def test_complete_scholarship_item_creation():
    """Test creating a complete scholarship item with all fields."""
    item = ScholarshipItem(
        title='STEM Excellence Scholarship',
        description='Scholarship for students pursuing STEM fields',
        amount='$5,000',
        deadline='2026-01-15',
        eligibility='Full-time student | GPA 3.0+',
        requirements='Application | Essay | Recommendations',
        application_url='https://example.com/apply',
        provider='STEM Foundation',
        category='STEM',
        source='test_spider',
        source_url='https://example.com/scholarship',
        scraped_date='2025-06-10',
        last_updated='2025-06-10',
        tags=['STEM', 'Engineering', 'Technology'],
        is_active=True,
        item_id='12345'
    )
    
    assert item['title'] == 'STEM Excellence Scholarship'
    assert item['description'] == 'Scholarship for students pursuing STEM fields'
    assert item['amount'] == '$5,000'
    assert item['deadline'] == '2026-01-15'
    assert item['eligibility'] == 'Full-time student | GPA 3.0+'
    assert item['requirements'] == 'Application | Essay | Recommendations'
    assert item['application_url'] == 'https://example.com/apply'
    assert item['provider'] == 'STEM Foundation'
    assert item['category'] == 'STEM'
    assert item['source'] == 'test_spider'
    assert item['source_url'] == 'https://example.com/scholarship'
    assert item['scraped_date'] == '2025-06-10'
    assert item['last_updated'] == '2025-06-10'
    assert item['tags'] == ['STEM', 'Engineering', 'Technology']
    assert item['is_active'] == True
    assert item['item_id'] == '12345'

def test_itemloader_integration_with_sample_html(sample_html, mock_response):
    """Test integrating ItemLoader with sample HTML."""
    response = mock_response(body=sample_html)
    
    # Create a test loader
    class ScholarshipItemLoader(ItemLoader):
        default_item_class = ScholarshipItem
    
    loader = ScholarshipItemLoader(selector=response)
    loader.add_css('title', 'h1::text')
    loader.add_css('description', '.description p::text')
    loader.add_css('amount', '.amount::text')
    loader.add_css('deadline', '.deadline::text')
    loader.add_css('eligibility', '.eligibility li::text')
    loader.add_css('requirements', '.requirements li::text')
    loader.add_css('application_url', '.apply-button::attr(href)')
    
    item = loader.load_item()
    
    assert item['title'] == 'Sample Scholarship'
    assert 'This is a scholarship for students' in item['description']
    assert 'It provides financial assistance' in item['description']
    assert item['amount'] == '$5,000'
    assert item['deadline'] == '2026-01-15'
    assert 'Must be a full-time student' in item['eligibility']
    assert 'GPA of 3.0 or higher' in item['eligibility']
    assert 'Application form' in item['requirements']
    assert 'Essay' in item['requirements']
    assert 'Letters of recommendation' in item['requirements']
    assert item['application_url'] == 'https://example.com/apply'


# ----------------------- Edge case tests -----------------------

def test_parse_deadline_with_various_formats():
    """Test parse_deadline with various date formats."""
    test_cases = [
        ('2026-01-15', '2026-01-15'),
        ('01/15/2026', '2026-01-15'),
        ('01-15-2026', '2026-01-15'),
        ('January 15, 2026', '2026-01-15'),
        ('Jan 15, 2026', '2026-01-15'),
        ('15 January 2026', '2026-01-15'),
        ('15 Jan 2026', '2026-01-15'),
    ]
    
    for input_date, expected in test_cases:
        assert parse_deadline(input_date) == expected
        
def test_parse_deadline_with_unusual_formats():
    """Test parse_deadline with unusual formats."""
    test_cases = [
        ('2026.01.15', '2026.01.15'),  # Should return as is
        ('15.01.2026', '15.01.2026'),  # Should return as is
        ('Jan. 15, 2026', 'Jan. 15, 2026'),  # Should return as is (period after month abbreviation)
    ]
    
    for input_date, expected in test_cases:
        assert parse_deadline(input_date) == expected

def test_clean_amount_variations():
    """Test clean_amount with various formats."""
    test_cases = [
        ('$5,000', '$5,000'),
        ('5,000 USD', '5,000'),  # USD removed by clean_amount function
        ('$5000', '$5000'),
        ('$5,000.00', '$5,000.00'),
        ('5000 dollars', '5000'),
        ('Award amount: $5,000', '$5,000'),
        ('$1,000 to $5,000', '$1,000$5,000'),
        ('full tuition ($50,000)', '$50,000'),
    ]
    
    for input_amount, expected in test_cases:
        assert clean_amount(input_amount) == expected


# ----------------------- Additional processor tests -----------------------

def test_clean_text_with_html():
    """Test clean_text function with HTML input."""
    html = '<p>This is <b>formatted</b> text.</p>'
    # clean_text doesn't handle HTML directly
    assert clean_text(html) == '<p>This is <b>formatted</b> text.</p>'
    
    # But when combined with remove_tags
    assert clean_text(remove_tags(html)) == 'This is formatted text.'


def test_clean_text_with_various_whitespace():
    """Test clean_text with various whitespace combinations."""
    test_cases = [
        ('  leading spaces', 'leading spaces'),
        ('trailing spaces  ', 'trailing spaces'),
        ('  both  ', 'both'),
        ('multiple    spaces', 'multiple spaces'),
        ('tabs\t\tbetween', 'tabs between'),
        ('newlines\n\nbetween', 'newlines between'),
        ('mixed\n \t whitespace', 'mixed whitespace'),
    ]
    
    for input_text, expected in test_cases:
        assert clean_text(input_text) == expected


def test_clean_amount_various_characters():
    """Test clean_amount with various characters."""
    test_cases = [
        ('$5,000*', '$5,000'),
        ('~$5,000~', '$5,000'),
        ('$5,000+', '$5,000'),  # Plus sign removed
        ('$5,000 (USD)', '$5,000USD'),
        ('approximately $5,000', '$5,000'),
    ]
    
    for input_amount, expected in test_cases:
        assert clean_amount(input_amount) == expected


def test_clean_amount_with_special_characters():
    """Test clean_amount with special characters."""
    test_cases = [
        ('$5,000€', '$5,000'),
        ('£5,000', '5,000'),
        ('¥5,000', '5,000'),
        ('€5,000', '5,000'),
    ]
    
    for input_amount, expected in test_cases:
        assert clean_amount(input_amount) == expected


def test_parse_deadline_invalid_dates():
    """Test parse_deadline with invalid dates."""
    test_cases = [
        ('Tomorrow', 'Tomorrow'),
        ('Next week', 'Next week'),
        ('End of semester', 'End of semester'),
        ('TBA', 'TBA'),
        ('Ongoing', 'Ongoing'),
        ('Contact for details', 'Contact for details'),
    ]
    
    for input_date, expected in test_cases:
        assert parse_deadline(input_date) == expected
