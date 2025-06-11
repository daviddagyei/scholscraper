"""
Data processing pipelines for scholarship scraping.

This module contains all the data processing pipelines that clean,
validate, deduplicate, and export scholarship data.
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Set
from itemadapter import ItemAdapter

# Third-party imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("Firebase dependencies not available. FirebasePipeline will be disabled.")

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False
    logging.warning("Google Sheets dependencies not available. GoogleSheetsPipeline will be disabled.")


class ValidationPipeline:
    """Validates scraped scholarship items."""
    
    def __init__(self):
        self.required_fields = ['title', 'description', 'amount', 'deadline', 'application_url']
        self.dropped_items = 0
        self.processed_items = 0
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        self.processed_items += 1
        
        # Check required fields
        for field in self.required_fields:
            if not adapter.get(field):
                self.dropped_items += 1
                spider.logger.warning(f"Item missing required field '{field}': {adapter.get('title', 'Unknown')}")
                raise DropItem(f"Missing required field: {field}")
        
        # Validate URL format
        url = adapter.get('application_url', '')
        if not (url.startswith('http://') or url.startswith('https://')):
            self.dropped_items += 1
            spider.logger.warning(f"Invalid URL format: {url}")
            raise DropItem(f"Invalid URL format: {url}")
            
        # Validate amount format (should contain digits)
        amount = adapter.get('amount', '')
        if not any(char.isdigit() for char in amount):
            spider.logger.warning(f"Invalid amount format: {amount}")
            # Don't drop, just log warning
            
        spider.logger.info(f"Validated item: {adapter.get('title')}")
        return item
    
    def close_spider(self, spider):
        spider.logger.info(f"ValidationPipeline: Processed {self.processed_items}, Dropped {self.dropped_items}")


class DeduplicationPipeline:
    """Removes duplicate scholarship items based on title and provider."""
    
    def __init__(self):
        self.seen_items: Set[str] = set()
        self.duplicate_count = 0
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Create unique identifier based on title and provider
        title = adapter.get('title', '').lower().strip()
        provider = adapter.get('provider', '').lower().strip()
        url = adapter.get('application_url', '').strip()
        
        # Create hash for deduplication
        unique_string = f"{title}|{provider}|{url}"
        item_hash = hashlib.md5(unique_string.encode()).hexdigest()
        
        if item_hash in self.seen_items:
            self.duplicate_count += 1
            spider.logger.warning(f"Duplicate item found: {title}")
            raise DropItem(f"Duplicate item: {title}")
        
        self.seen_items.add(item_hash)
        adapter['item_id'] = item_hash
        
        spider.logger.debug(f"Unique item processed: {title}")
        return item
    
    def close_spider(self, spider):
        spider.logger.info(f"DeduplicationPipeline: Found {self.duplicate_count} duplicates")


class DataCleaningPipeline:
    """Additional data cleaning and normalization."""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Add metadata
        adapter['scraped_date'] = datetime.now().isoformat()
        adapter['last_updated'] = datetime.now().isoformat()
        adapter['is_active'] = True
        adapter['source'] = spider.name
        
        # Clean and normalize category
        category = adapter.get('category', '')
        if category:
            # Normalize category names
            category_mapping = {
                'stem': 'STEM',
                'science': 'STEM',
                'technology': 'STEM',
                'engineering': 'STEM',
                'math': 'STEM',
                'mathematics': 'STEM',
                'business': 'Business',
                'arts': 'Arts',
                'liberal arts': 'Arts',
                'humanities': 'Arts',
                'health': 'Healthcare',
                'medical': 'Healthcare',
                'nursing': 'Healthcare',
                'general': 'General',
                'need-based': 'Need-Based',
                'merit': 'Merit-Based',
            }
            
            category_lower = category.lower()
            for key, value in category_mapping.items():
                if key in category_lower:
                    adapter['category'] = value
                    break
            else:
                adapter['category'] = 'General'
        else:
            adapter['category'] = 'General'
        
        # Ensure tags is a list
        tags = adapter.get('tags', [])
        if isinstance(tags, str):
            adapter['tags'] = [tag.strip() for tag in tags.split(',') if tag.strip()]
        elif not isinstance(tags, list):
            adapter['tags'] = []
            
        spider.logger.debug(f"Cleaned item: {adapter.get('title')}")
        return item


class FirebasePipeline:
    """Exports items to Firebase Firestore."""
    
    def __init__(self, project_id=None, credentials_path=None):
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.db = None
        self.collection_name = 'scholarships'
        self.items_saved = 0
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            project_id=crawler.settings.get('FIREBASE_PROJECT_ID'),
            credentials_path=crawler.settings.get('FIREBASE_CREDENTIALS_PATH'),
        )
    
    def open_spider(self, spider):
        if not FIREBASE_AVAILABLE:
            spider.logger.warning("Firebase pipeline disabled - dependencies not available")
            return
            
        if not self.project_id or not self.credentials_path:
            spider.logger.warning("Firebase pipeline disabled - missing configuration")
            return
            
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': self.project_id,
                })
            
            self.db = firestore.client()
            spider.logger.info("Firebase pipeline initialized successfully")
            
        except Exception as e:
            spider.logger.error(f"Failed to initialize Firebase: {e}")
            self.db = None
    
    def process_item(self, item, spider):
        if not self.db:
            return item
            
        try:
            adapter = ItemAdapter(item)
            item_dict = dict(adapter)
            
            # Use item_id as document ID for easy updates
            doc_id = item_dict.get('item_id', '')
            if doc_id:
                self.db.collection(self.collection_name).document(doc_id).set(item_dict)
                self.items_saved += 1
                spider.logger.debug(f"Saved to Firebase: {item_dict.get('title')}")
            else:
                spider.logger.warning("Item missing item_id, skipping Firebase save")
                
        except Exception as e:
            spider.logger.error(f"Failed to save item to Firebase: {e}")
            
        return item
    
    def close_spider(self, spider):
        if self.db:
            spider.logger.info(f"FirebasePipeline: Saved {self.items_saved} items to Firestore")


class GoogleSheetsPipeline:
    """Exports items to Google Sheets."""
    
    def __init__(self, credentials_path=None, spreadsheet_id=None):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.worksheet = None
        self.items_saved = 0
        self.headers = [
            'title', 'description', 'amount', 'deadline', 'eligibility',
            'requirements', 'application_url', 'provider', 'category',
            'source', 'scraped_date', 'is_active'
        ]
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            credentials_path=crawler.settings.get('GOOGLE_SHEETS_CREDENTIALS_PATH'),
            spreadsheet_id=crawler.settings.get('GOOGLE_SHEETS_SPREADSHEET_ID'),
        )
    
    def open_spider(self, spider):
        if not GSHEETS_AVAILABLE:
            spider.logger.warning("Google Sheets pipeline disabled - dependencies not available")
            return
            
        if not self.credentials_path or not self.spreadsheet_id:
            spider.logger.warning("Google Sheets pipeline disabled - missing configuration")
            return
            
        try:
            # Authenticate with Google Sheets
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(self.credentials_path, scopes=scope)
            client = gspread.authorize(creds)
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(self.spreadsheet_id)
            
            # Create or get worksheet
            try:
                self.worksheet = spreadsheet.worksheet('scholarships')
            except gspread.WorksheetNotFound:
                self.worksheet = spreadsheet.add_worksheet(title='scholarships', rows=1000, cols=20)
                # Add headers
                self.worksheet.append_row(self.headers)
                
            spider.logger.info("Google Sheets pipeline initialized successfully")
            
        except Exception as e:
            spider.logger.error(f"Failed to initialize Google Sheets: {e}")
            self.worksheet = None
    
    def process_item(self, item, spider):
        if not self.worksheet:
            return item
            
        try:
            adapter = ItemAdapter(item)
            
            # Prepare row data
            row_data = []
            for header in self.headers:
                value = adapter.get(header, '')
                # Convert lists to string representation
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                row_data.append(str(value))
            
            # Append row to worksheet
            self.worksheet.append_row(row_data)
            self.items_saved += 1
            spider.logger.debug(f"Saved to Google Sheets: {adapter.get('title')}")
            
        except Exception as e:
            spider.logger.error(f"Failed to save item to Google Sheets: {e}")
            
        return item
    
    def close_spider(self, spider):
        if self.worksheet:
            spider.logger.info(f"GoogleSheetsPipeline: Saved {self.items_saved} items to Google Sheets")


# Import DropItem at the end to avoid circular imports
from scrapy.exceptions import DropItem
