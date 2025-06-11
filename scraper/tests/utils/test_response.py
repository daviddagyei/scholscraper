"""
Custom response class for testing.

This module provides a custom response class that allows setting meta
information for testing purposes.
"""

import scrapy


class TestHtmlResponse(scrapy.http.HtmlResponse):
    """Custom HtmlResponse class for testing with settable meta."""
    
    def __init__(self, *args, **kwargs):
        self._meta = kwargs.pop('meta', {})
        super().__init__(*args, **kwargs)
    
    @property
    def meta(self):
        return self._meta
    
    @meta.setter
    def meta(self, value):
        self._meta = value
