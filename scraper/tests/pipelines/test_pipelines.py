"""
Tests for the scraper pipelines module.

This module contains tests for all data processing pipelines including:
- ValidationPipeline
- DeduplicationPipeline
- DataCleaningPipeline 
- FirebasePipeline
- GoogleSheetsPipeline

Tests cover validation, deduplication, data cleaning, and export functionality.
"""

import pytest
import hashlib
from datetime import datetime
from unittest.mock import MagicMock, patch
from scrapy.exceptions import DropItem
from itemadapter import ItemAdapter

# Import the pipelines
from scraper.pipelines.pipelines import (
    ValidationPipeline,
    DeduplicationPipeline,
    DataCleaningPipeline,
    FirebasePipeline,
    GoogleSheetsPipeline
)


# ----------------------- ValidationPipeline tests -----------------------

def test_validation_pipeline_init():
    """Test ValidationPipeline initializat    spider.logger.info.assert_called_once_with(
        'GoogleSheetsPipeline: Saved 42 items to Google Sheets'
    )."""
    pipeline = ValidationPipeline()
    assert pipeline.required_fields == ['title', 'description', 'amount', 'deadline', 'application_url']
    assert pipeline.dropped_items == 0
    assert pipeline.processed_items == 0


def test_validation_all_fields_valid():
    """Test ValidationPipeline with all valid fields."""
    pipeline = ValidationPipeline()
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'description': 'A scholarship for testing',
        'amount': '$5,000',
        'deadline': '2023-12-31',
        'application_url': 'https://example.com/apply',
    }
    
    result = pipeline.process_item(item, spider)
    assert result == item
    assert pipeline.processed_items == 1
    assert pipeline.dropped_items == 0


def test_validation_missing_required_field():
    """Test ValidationPipeline with missing required field."""
    pipeline = ValidationPipeline()
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'description': 'A scholarship for testing',
        'amount': '$5,000',
        # Missing deadline
        'application_url': 'https://example.com/apply',
    }
    
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item, spider)
    
    assert "Missing required field: deadline" in str(excinfo.value)
    assert pipeline.processed_items == 1
    assert pipeline.dropped_items == 1


def test_validation_empty_required_field():
    """Test ValidationPipeline with empty required field."""
    pipeline = ValidationPipeline()
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'description': '',  # Empty description
        'amount': '$5,000',
        'deadline': '2023-12-31',
        'application_url': 'https://example.com/apply',
    }
    
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item, spider)
    
    assert "Missing required field: description" in str(excinfo.value)
    assert pipeline.processed_items == 1
    assert pipeline.dropped_items == 1


def test_validation_invalid_url_format():
    """Test ValidationPipeline with invalid URL format."""
    pipeline = ValidationPipeline()
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'description': 'A scholarship for testing',
        'amount': '$5,000',
        'deadline': '2023-12-31',
        'application_url': 'example.com/apply',  # Missing protocol
    }
    
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item, spider)
    
    assert "Invalid URL format" in str(excinfo.value)
    assert pipeline.processed_items == 1
    assert pipeline.dropped_items == 1


def test_validation_amount_without_digits():
    """Test ValidationPipeline with amount having no digits."""
    pipeline = ValidationPipeline()
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'description': 'A scholarship for testing',
        'amount': 'Full tuition',  # No digits
        'deadline': '2023-12-31',
        'application_url': 'https://example.com/apply',
    }
    
    # Should not drop but log warning
    result = pipeline.process_item(item, spider)
    assert result == item
    assert pipeline.processed_items == 1
    assert pipeline.dropped_items == 0
    spider.logger.warning.assert_called_once()


def test_validation_close_spider():
    """Test ValidationPipeline close_spider method."""
    pipeline = ValidationPipeline()
    pipeline.processed_items = 100
    pipeline.dropped_items = 10
    spider = MagicMock()
    
    pipeline.close_spider(spider)
    spider.logger.info.assert_called_once_with(
        "ValidationPipeline: Processed 100, Dropped 10"
    )


# ----------------------- DeduplicationPipeline tests -----------------------

def test_deduplication_pipeline_init():
    """Test DeduplicationPipeline initialization."""
    pipeline = DeduplicationPipeline()
    assert pipeline.seen_items == set()
    assert pipeline.duplicate_count == 0


def test_deduplication_unique_item():
    """Test DeduplicationPipeline with unique item."""
    pipeline = DeduplicationPipeline()
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'provider': 'Test Provider',
        'application_url': 'https://example.com/apply',
    }
    
    result = pipeline.process_item(item, spider)
    
    # Check that hash was created and added
    unique_string = "test scholarship|test provider|https://example.com/apply"
    item_hash = hashlib.md5(unique_string.encode()).hexdigest()
    
    assert result['item_id'] == item_hash
    assert item_hash in pipeline.seen_items
    assert pipeline.duplicate_count == 0


def test_deduplication_duplicate_item():
    """Test DeduplicationPipeline with duplicate item."""
    pipeline = DeduplicationPipeline()
    spider = MagicMock()
    
    # First item
    item1 = {
        'title': 'Test Scholarship',
        'provider': 'Test Provider',
        'application_url': 'https://example.com/apply',
    }
    
    pipeline.process_item(item1, spider)
    
    # Duplicate item
    item2 = {
        'title': 'Test Scholarship',
        'provider': 'Test Provider',
        'application_url': 'https://example.com/apply',
    }
    
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item2, spider)
    
    assert "Duplicate item" in str(excinfo.value)
    assert pipeline.duplicate_count == 1


def test_deduplication_case_insensitive():
    """Test DeduplicationPipeline with case insensitive comparison."""
    pipeline = DeduplicationPipeline()
    spider = MagicMock()
    
    # First item
    item1 = {
        'title': 'Test Scholarship',
        'provider': 'Test Provider',
        'application_url': 'https://example.com/apply',
    }
    
    pipeline.process_item(item1, spider)
    
    # Same item with different case
    item2 = {
        'title': 'TEST SCHOLARSHIP',
        'provider': 'test PROVIDER',
        'application_url': 'https://example.com/apply',
    }
    
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item2, spider)
    
    assert "Duplicate item" in str(excinfo.value)
    assert pipeline.duplicate_count == 1


def test_deduplication_whitespace_handled():
    """Test DeduplicationPipeline handles extra whitespace."""
    pipeline = DeduplicationPipeline()
    spider = MagicMock()
    
    # First item
    item1 = {
        'title': 'Test Scholarship',
        'provider': 'Test Provider',
        'application_url': 'https://example.com/apply',
    }
    
    pipeline.process_item(item1, spider)
    
    # Same item with extra whitespace
    item2 = {
        'title': '  Test Scholarship  ',
        'provider': ' Test Provider ',
        'application_url': 'https://example.com/apply',
    }
    
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item2, spider)
    
    assert "Duplicate item" in str(excinfo.value)
    assert pipeline.duplicate_count == 1


def test_deduplication_missing_fields():
    """Test DeduplicationPipeline with missing fields."""
    pipeline = DeduplicationPipeline()
    spider = MagicMock()
    
    # Item with missing fields
    item = {
        'title': 'Test Scholarship',
        # Missing provider
        # Missing application_url
    }
    
    result = pipeline.process_item(item, spider)
    
    # Hash should be created from available fields
    unique_string = "test scholarship||"
    item_hash = hashlib.md5(unique_string.encode()).hexdigest()
    
    assert result['item_id'] == item_hash
    assert item_hash in pipeline.seen_items


def test_deduplication_close_spider():
    """Test DeduplicationPipeline close_spider method."""
    pipeline = DeduplicationPipeline()
    pipeline.duplicate_count = 5
    spider = MagicMock()
    
    pipeline.close_spider(spider)
    spider.logger.info.assert_called_once_with(
        "DeduplicationPipeline: Found 5 duplicates"
    )


# ----------------------- DataCleaningPipeline tests -----------------------

def test_data_cleaning_metadata_added():
    """Test DataCleaningPipeline adds metadata."""
    pipeline = DataCleaningPipeline()
    spider = MagicMock()
    spider.name = "test_spider"
    
    item = {
        'title': 'Test Scholarship',
    }
    
    result = pipeline.process_item(item, spider)
    
    assert 'scraped_date' in result
    assert 'last_updated' in result
    assert result['is_active'] is True
    assert result['source'] == "test_spider"


def test_data_cleaning_empty_category():
    """Test DataCleaningPipeline handles empty category."""
    pipeline = DataCleaningPipeline()
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        # No category
    }
    
    result = pipeline.process_item(item, spider)
    assert result['category'] == 'General'


def test_data_cleaning_stem_category_normalization():
    """Test DataCleaningPipeline normalizes STEM categories."""
    pipeline = DataCleaningPipeline()
    spider = MagicMock()
    
    categories = [
        'stem', 'Science', 'TECHNOLOGY', 'Engineering', 'Mathematics'
    ]
    
    for cat in categories:
        item = {'title': 'Test', 'category': cat}
        result = pipeline.process_item(item, spider)
        assert result['category'] == 'STEM'


def test_data_cleaning_arts_category_normalization():
    """Test DataCleaningPipeline normalizes Arts categories."""
    pipeline = DataCleaningPipeline()
    spider = MagicMock()
    
    categories = ['arts', 'liberal arts', 'humanities']
    
    for cat in categories:
        item = {'title': 'Test', 'category': cat}
        result = pipeline.process_item(item, spider)
        assert result['category'] == 'Arts'


def test_data_cleaning_healthcare_category_normalization():
    """Test DataCleaningPipeline normalizes Healthcare categories."""
    pipeline = DataCleaningPipeline()
    spider = MagicMock()
    
    categories = ['health', 'medical', 'nursing']
    
    for cat in categories:
        item = {'title': 'Test', 'category': cat}
        result = pipeline.process_item(item, spider)
        assert result['category'] == 'Healthcare'


def test_data_cleaning_tags_string_to_list():
    """Test DataCleaningPipeline converts tags string to list."""
    pipeline = DataCleaningPipeline()
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'tags': 'stem, engineering, women',
    }
    
    result = pipeline.process_item(item, spider)
    assert result['tags'] == ['stem', 'engineering', 'women']


def test_data_cleaning_tags_empty():
    """Test DataCleaningPipeline handles empty tags."""
    pipeline = DataCleaningPipeline()
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'tags': '',
    }
    
    result = pipeline.process_item(item, spider)
    assert result['tags'] == []


def test_data_cleaning_tags_non_list_non_string():
    """Test DataCleaningPipeline handles non-list, non-string tags."""
    pipeline = DataCleaningPipeline()
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'tags': 123,  # Non-string, non-list
    }
    
    result = pipeline.process_item(item, spider)
    assert result['tags'] == []


# ----------------------- FirebasePipeline tests -----------------------

def test_firebase_pipeline_init():
    """Test FirebasePipeline initialization."""
    pipeline = FirebasePipeline(project_id='test_project', credentials_path='path/to/credentials.json')
    assert pipeline.project_id == 'test_project'
    assert pipeline.credentials_path == 'path/to/credentials.json'
    assert pipeline.db is None
    assert pipeline.collection_name == 'scholarships'
    assert pipeline.items_saved == 0


def test_firebase_pipeline_from_crawler():
    """Test FirebasePipeline from_crawler method."""
    crawler = MagicMock()
    crawler.settings.get.side_effect = lambda key, default=None: {
        'FIREBASE_PROJECT_ID': 'test_project',
        'FIREBASE_CREDENTIALS_PATH': 'path/to/credentials.json',
    }.get(key, default)
    
    pipeline = FirebasePipeline.from_crawler(crawler)
    
    assert pipeline.project_id == 'test_project'
    assert pipeline.credentials_path == 'path/to/credentials.json'


@patch('scraper.pipelines.pipelines.FIREBASE_AVAILABLE', False)
def test_firebase_pipeline_open_spider_dependencies_not_available():
    """Test FirebasePipeline open_spider when dependencies not available."""
    pipeline = FirebasePipeline(project_id='test_project', credentials_path='path/to/credentials.json')
    spider = MagicMock()
    
    pipeline.open_spider(spider)
    
    assert pipeline.db is None
    spider.logger.warning.assert_called_once_with("Firebase pipeline disabled - dependencies not available")


@patch('scraper.pipelines.pipelines.FIREBASE_AVAILABLE', True)
def test_firebase_pipeline_open_spider_missing_config():
    """Test FirebasePipeline open_spider with missing configuration."""
    pipeline = FirebasePipeline()  # No project_id or credentials_path
    spider = MagicMock()
    
    pipeline.open_spider(spider)
    
    assert pipeline.db is None
    spider.logger.warning.assert_called_once_with("Firebase pipeline disabled - missing configuration")


@patch('scraper.pipelines.pipelines.FIREBASE_AVAILABLE', True)
@patch('firebase_admin.initialize_app')
@patch('firebase_admin.credentials.Certificate')
@patch('firebase_admin.firestore.client')
@patch('firebase_admin._apps', [])
def test_firebase_pipeline_open_spider_success(mock_firestore, mock_certificate, mock_initialize):
    """Test FirebasePipeline open_spider successful initialization."""
    pipeline = FirebasePipeline(project_id='test_project', credentials_path='path/to/credentials.json')
    spider = MagicMock()
    
    mock_firestore.return_value = MagicMock()
    
    pipeline.open_spider(spider)
    
    assert pipeline.db is not None
    mock_certificate.assert_called_once_with('path/to/credentials.json')
    mock_initialize.assert_called_once()
    spider.logger.info.assert_called_once_with("Firebase pipeline initialized successfully")


@patch('firebase_admin.initialize_app')
@patch('firebase_admin.credentials.Certificate')
def test_firebase_pipeline_open_spider_exception(mock_certificate, mock_initialize):
    """Test FirebasePipeline open_spider exception handling."""
    mock_certificate.side_effect = Exception('Test error')
    
    pipeline = FirebasePipeline(project_id='test_project', credentials_path='path/to/credentials.json')
    spider = MagicMock()
    
    # Force FIREBASE_AVAILABLE to True for this test
    with patch('scraper.pipelines.pipelines.FIREBASE_AVAILABLE', True):
        pipeline.open_spider(spider)
    
    assert pipeline.db is None
    spider.logger.error.assert_called_once_with("Failed to initialize Firebase: Test error")


def test_firebase_pipeline_process_item_no_db():
    """Test FirebasePipeline process_item when db is None."""
    pipeline = FirebasePipeline()
    pipeline.db = None
    spider = MagicMock()
    
    item = {'title': 'Test Scholarship'}
    
    result = pipeline.process_item(item, spider)
    assert result == item  # Item passes through unchanged


@patch('scraper.pipelines.pipelines.FIREBASE_AVAILABLE', True)
def test_firebase_pipeline_process_item_success():
    """Test FirebasePipeline process_item success."""
    pipeline = FirebasePipeline()
    mock_db = MagicMock()
    pipeline.db = mock_db
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'item_id': '123456',
    }
    
    mock_doc = MagicMock()
    mock_collection = MagicMock()
    mock_collection.document.return_value = mock_doc
    mock_db.collection.return_value = mock_collection
    
    result = pipeline.process_item(item, spider)
    
    assert result == item
    mock_db.collection.assert_called_once_with('scholarships')
    mock_collection.document.assert_called_once_with('123456')
    mock_doc.set.assert_called_once_with(item)
    assert pipeline.items_saved == 1


@patch('scraper.pipelines.pipelines.FIREBASE_AVAILABLE', True)
def test_firebase_pipeline_process_item_missing_id():
    """Test FirebasePipeline process_item with missing item_id."""
    pipeline = FirebasePipeline()
    mock_db = MagicMock()
    pipeline.db = mock_db
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        # Missing item_id
    }
    
    result = pipeline.process_item(item, spider)
    
    assert result == item
    mock_db.collection.assert_not_called()
    spider.logger.warning.assert_called_once()
    assert pipeline.items_saved == 0


@patch('scraper.pipelines.pipelines.FIREBASE_AVAILABLE', True)
def test_firebase_pipeline_process_item_exception():
    """Test FirebasePipeline process_item exception handling."""
    pipeline = FirebasePipeline()
    mock_db = MagicMock()
    pipeline.db = mock_db
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'item_id': '123456',
    }
    
    mock_db.collection.side_effect = Exception('Test error')
    
    result = pipeline.process_item(item, spider)
    
    assert result == item
    mock_db.collection.assert_called_once_with('scholarships')
    spider.logger.error.assert_called_once_with("Failed to save item to Firebase: Test error")


def test_firebase_pipeline_close_spider():
    """Test FirebasePipeline close_spider method."""
    pipeline = FirebasePipeline()
    pipeline.db = MagicMock()
    pipeline.items_saved = 42
    spider = MagicMock()
    
    pipeline.close_spider(spider)
    
    spider.logger.info.assert_called_once_with(
        "FirebasePipeline: Saved 42 items to Firestore"
    )


# ----------------------- GoogleSheetsPipeline tests -----------------------

def test_google_sheets_pipeline_init():
    """Test GoogleSheetsPipeline initialization."""
    pipeline = GoogleSheetsPipeline(
        credentials_path='path/to/credentials.json',
        spreadsheet_id='test_spreadsheet_id'
    )
    assert pipeline.credentials_path == 'path/to/credentials.json'
    assert pipeline.spreadsheet_id == 'test_spreadsheet_id'
    assert pipeline.worksheet is None
    assert pipeline.items_saved == 0
    assert len(pipeline.headers) > 0


def test_google_sheets_pipeline_from_crawler():
    """Test GoogleSheetsPipeline from_crawler method."""
    crawler = MagicMock()
    crawler.settings.get.side_effect = lambda key, default=None: {
        'GOOGLE_SHEETS_CREDENTIALS_PATH': 'path/to/credentials.json',
        'GOOGLE_SHEETS_SPREADSHEET_ID': 'test_spreadsheet_id',
    }.get(key, default)
    
    pipeline = GoogleSheetsPipeline.from_crawler(crawler)
    
    assert pipeline.credentials_path == 'path/to/credentials.json'
    assert pipeline.spreadsheet_id == 'test_spreadsheet_id'


@patch('scraper.pipelines.pipelines.GSHEETS_AVAILABLE', False)
def test_google_sheets_pipeline_open_spider_dependencies_not_available():
    """Test GoogleSheetsPipeline open_spider when dependencies not available."""
    pipeline = GoogleSheetsPipeline(
        credentials_path='path/to/credentials.json',
        spreadsheet_id='test_spreadsheet_id'
    )
    spider = MagicMock()
    
    pipeline.open_spider(spider)
    
    assert pipeline.worksheet is None
    spider.logger.warning.assert_called_once_with("Google Sheets pipeline disabled - dependencies not available")


@patch('scraper.pipelines.pipelines.GSHEETS_AVAILABLE', True)
def test_google_sheets_pipeline_open_spider_missing_config():
    """Test GoogleSheetsPipeline open_spider with missing configuration."""
    pipeline = GoogleSheetsPipeline()  # No credentials_path or spreadsheet_id
    spider = MagicMock()
    
    pipeline.open_spider(spider)
    
    assert pipeline.worksheet is None
    spider.logger.warning.assert_called_once_with("Google Sheets pipeline disabled - missing configuration")


@patch('scraper.pipelines.pipelines.GSHEETS_AVAILABLE', True)
@patch('gspread.authorize')
@patch('scraper.pipelines.pipelines.Credentials')
def test_google_sheets_pipeline_open_spider_worksheet_exists(mock_credentials, mock_authorize):
    """Test GoogleSheetsPipeline open_spider when worksheet exists."""
    pipeline = GoogleSheetsPipeline(
        credentials_path='path/to/credentials.json',
        spreadsheet_id='test_spreadsheet_id'
    )
    spider = MagicMock()
    
    # Mock gspread objects
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    
    mock_authorize.return_value = mock_client
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_spreadsheet.worksheet.return_value = mock_worksheet
    
    pipeline.open_spider(spider)
    
    assert pipeline.worksheet == mock_worksheet
    mock_credentials.from_service_account_file.assert_called_once()
    mock_authorize.assert_called_once()
    mock_client.open_by_key.assert_called_once_with('test_spreadsheet_id')
    mock_spreadsheet.worksheet.assert_called_once_with('scholarships')
    mock_spreadsheet.add_worksheet.assert_not_called()
    spider.logger.info.assert_called_once_with("Google Sheets pipeline initialized successfully")


@patch('scraper.pipelines.pipelines.GSHEETS_AVAILABLE', True)
@patch('gspread.authorize')
@patch('scraper.pipelines.pipelines.Credentials')
@patch('gspread.WorksheetNotFound', Exception)
def test_google_sheets_pipeline_open_spider_worksheet_not_found(mock_credentials, mock_authorize):
    """Test GoogleSheetsPipeline open_spider when worksheet doesn't exist."""
    pipeline = GoogleSheetsPipeline(
        credentials_path='path/to/credentials.json',
        spreadsheet_id='test_spreadsheet_id'
    )
    spider = MagicMock()
    
    # Mock gspread objects
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    
    mock_authorize.return_value = mock_client
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_spreadsheet.worksheet.side_effect = Exception("Worksheet not found")
    mock_spreadsheet.add_worksheet.return_value = mock_worksheet
    
    pipeline.open_spider(spider)
    
    assert pipeline.worksheet == mock_worksheet
    mock_spreadsheet.add_worksheet.assert_called_once_with(title='scholarships', rows=1000, cols=20)
    mock_worksheet.append_row.assert_called_once_with(pipeline.headers)


@patch('scraper.pipelines.pipelines.GSHEETS_AVAILABLE', True)
@patch('gspread.authorize')
@patch('scraper.pipelines.pipelines.Credentials')
def test_google_sheets_pipeline_open_spider_exception(mock_credentials, mock_authorize):
    """Test GoogleSheetsPipeline open_spider exception handling."""
    mock_authorize.side_effect = Exception('Test error')
    
    pipeline = GoogleSheetsPipeline(
        credentials_path='path/to/credentials.json',
        spreadsheet_id='test_spreadsheet_id'
    )
    spider = MagicMock()
    
    pipeline.open_spider(spider)
    
    assert pipeline.worksheet is None
    spider.logger.error.assert_called_once_with("Failed to initialize Google Sheets: Test error")


def test_google_sheets_pipeline_process_item_no_worksheet():
    """Test GoogleSheetsPipeline process_item when worksheet is None."""
    pipeline = GoogleSheetsPipeline()
    pipeline.worksheet = None
    spider = MagicMock()
    
    item = {'title': 'Test Scholarship'}
    
    result = pipeline.process_item(item, spider)
    assert result == item  # Item passes through unchanged


def test_google_sheets_pipeline_process_item_success():
    """Test GoogleSheetsPipeline process_item success."""
    pipeline = GoogleSheetsPipeline()
    pipeline.worksheet = MagicMock()
    pipeline.headers = ['title', 'description', 'amount']
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'description': 'Test Description',
        'amount': '$5,000',
    }
    
    result = pipeline.process_item(item, spider)
    
    assert result == item
    pipeline.worksheet.append_row.assert_called_once_with(['Test Scholarship', 'Test Description', '$5,000'])
    assert pipeline.items_saved == 1


def test_google_sheets_pipeline_process_item_missing_fields():
    """Test GoogleSheetsPipeline process_item with missing fields."""
    pipeline = GoogleSheetsPipeline()
    pipeline.worksheet = MagicMock()
    pipeline.headers = ['title', 'description', 'amount']
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        # Missing description
        'amount': '$5,000',
    }
    
    result = pipeline.process_item(item, spider)
    
    assert result == item
    pipeline.worksheet.append_row.assert_called_once_with(['Test Scholarship', '', '$5,000'])
    assert pipeline.items_saved == 1


def test_google_sheets_pipeline_process_item_list_conversion():
    """Test GoogleSheetsPipeline process_item handles list conversion."""
    pipeline = GoogleSheetsPipeline()
    pipeline.worksheet = MagicMock()
    pipeline.headers = ['title', 'tags']
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
        'tags': ['STEM', 'Engineering', 'Women'],
    }
    
    result = pipeline.process_item(item, spider)
    
    assert result == item
    pipeline.worksheet.append_row.assert_called_once_with(['Test Scholarship', 'STEM, Engineering, Women'])
    assert pipeline.items_saved == 1


def test_google_sheets_pipeline_process_item_exception():
    """Test GoogleSheetsPipeline process_item exception handling."""
    pipeline = GoogleSheetsPipeline()
    pipeline.worksheet = MagicMock()
    pipeline.worksheet.append_row.side_effect = Exception('Test error')
    pipeline.headers = ['title']
    spider = MagicMock()
    
    item = {
        'title': 'Test Scholarship',
    }
    
    result = pipeline.process_item(item, spider)
    
    assert result == item
    pipeline.worksheet.append_row.assert_called_once()
    spider.logger.error.assert_called_once_with("Failed to save item to Google Sheets: Test error")
    assert pipeline.items_saved == 0


def test_google_sheets_pipeline_close_spider():
    """Test GoogleSheetsPipeline close_spider method."""
    pipeline = GoogleSheetsPipeline()
    pipeline.worksheet = MagicMock()
    pipeline.items_saved = 42
    spider = MagicMock()
    
    pipeline.close_spider(spider)
    
    spider.logger.info.assert_called_once_with(
        "GoogleSheetsPipeline: Saved 42 items to Sheet"
    )
