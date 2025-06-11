"""
Scrapy settings for scholarship scraping project.

For simplicity, this file contains only the most important settings
for production use. For the full list of available settings and their 
values, see: https://docs.scrapy.org/en/latest/topics/settings.html
"""

BOT_NAME = 'scholarship_scraper'

SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure pipelines
ITEM_PIPELINES = {
    'pipelines.pipelines.ValidationPipeline': 100,
    'pipelines.pipelines.DeduplicationPipeline': 200,
    'pipelines.pipelines.DataCleaningPipeline': 300,
    'pipelines.pipelines.FirebasePipeline': 400,
    'pipelines.pipelines.GoogleSheetsPipeline': 500,
}

# Configure delays and concurrent requests
DOWNLOAD_DELAY = 2  # 2 seconds delay between requests
RANDOMIZE_DOWNLOAD_DELAY = 0.5  # 0.5 * to 1.5 * DOWNLOAD_DELAY
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Configure AutoThrottle for adaptive delays
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# User agent rotation
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Rotate user agents to avoid detection
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
]

# Enable and configure middlewares
DOWNLOADER_MIDDLEWARES = {
    'middlewares.middlewares.UserAgentRotationMiddleware': 400,
    'middlewares.middlewares.ProxyRotationMiddleware': 410,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

# Configure caching for development
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # 1 hour
HTTPCACHE_DIR = 'httpcache'

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'scraper.log'

# Request timeout settings
DOWNLOAD_TIMEOUT = 30

# Configure feeds for data export
FEEDS = {
    'output/scholarships_%(time)s.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'indent': 2,
    },
    'output/scholarships_%(time)s.csv': {
        'format': 'csv',
        'encoding': 'utf8',
        'store_empty': False,
    },
}

# Custom settings for specific spiders can be defined here
SPIDER_SETTINGS = {
    'collegescholarships': {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    },
    'uncf': {
        'DOWNLOAD_DELAY': 4,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    },
    'hsf': {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    },
}

# Firebase configuration (will be loaded from environment)
FIREBASE_PROJECT_ID = None  # Set via environment variable
FIREBASE_CREDENTIALS_PATH = None  # Set via environment variable

# Google Sheets configuration (will be loaded from environment)
GOOGLE_SHEETS_CREDENTIALS_PATH = None  # Set via environment variable
GOOGLE_SHEETS_SPREADSHEET_ID = None  # Set via environment variable
