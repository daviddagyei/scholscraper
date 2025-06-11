"""
Provides mock utilities for spider testing.

This module contains utility functions for mocking spiders and their components
to facilitate easier testing without directly modifying immutable properties.
"""

from unittest.mock import MagicMock
import logging
from scrapy import Spider
import types

def patch_spider_logger(spider):
    """
    Patch a spider's logger with a mock without setting the property directly.
    
    Args:
        spider: The spider instance to patch
        
    Returns:
        tuple: (patched_spider, mock_logger)
    """
    mock_logger = MagicMock(spec=logging.Logger)
    
    # Store the original logger
    original_logger = spider.logger
    
    # Create a property descriptor that returns our mock
    def get_mock_logger(self):
        return mock_logger
    
    # Monkey patch the class to use our getter
    cls = spider.__class__
    spider_type = type(cls.__name__, (cls,), {})
    spider_type.logger = property(get_mock_logger)
    
    # Change the spider's class to our modified class
    spider.__class__ = spider_type
    
    return spider, mock_logger
