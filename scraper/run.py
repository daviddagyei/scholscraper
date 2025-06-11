#!/usr/bin/env python3
"""
Main runner script for the scholarship scraper.
"""

from scrapy.cmdline import execute
import sys
import os

if __name__ == '__main__':
    # Add the current directory to Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Execute scrapy command
    execute(sys.argv)
