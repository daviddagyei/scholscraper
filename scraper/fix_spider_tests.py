"""
Fix all spider tests by using our patch_spider_logger utility.
This script updates all spider test files to use the new logger mocking approach.
"""

import os
import re

test_files = [
    '/home/iamdankwa/scholscraper/scraper/tests/spiders/test_apia.py',
    '/home/iamdankwa/scholscraper/scraper/tests/spiders/test_base_spider.py',
    '/home/iamdankwa/scholscraper/scraper/tests/spiders/test_collegescholarships.py',
    '/home/iamdankwa/scholscraper/scraper/tests/spiders/test_hsf.py',
    '/home/iamdankwa/scholscraper/scraper/tests/spiders/test_native_american.py',
    '/home/iamdankwa/scholscraper/scraper/tests/spiders/test_uncf.py',
]

for file_path in test_files:
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if file already has the import
        if 'from tests.spiders.mock_spider import patch_spider_logger' not in content:
            # Add import after existing imports
            content = re.sub(
                r'(from scraper\.spiders\.[a-z_]+ import [A-Za-z]+)\n',
                r'\1\nfrom tests.spiders.mock_spider import patch_spider_logger\n',
                content,
                count=1
            )
        
        # Replace logger assignment patterns
        content = re.sub(
            r'spider\.logger = MagicMock\(\)',
            'spider, mock_logger = patch_spider_logger(spider)',
            content
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Updated {file_path}")

print("All spider test files have been updated.")
