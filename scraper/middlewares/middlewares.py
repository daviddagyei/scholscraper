"""
Scrapy middlewares for scholarship scraping.

This module contains custom middlewares for handling user agent rotation,
proxy rotation, and other request/response processing.
"""

import random
import logging
from typing import List, Optional
from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class UserAgentRotationMiddleware(UserAgentMiddleware):
    """
    Rotates user agents to avoid detection.
    """
    
    def __init__(self, user_agent_list: Optional[List[str]] = None):
        super().__init__()
        
        self.user_agent_list = user_agent_list or [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(
            user_agent_list=crawler.settings.getlist('USER_AGENT_LIST')
        )
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
    
    def spider_opened(self, spider):
        spider.logger.info(f'UserAgentRotationMiddleware: Using {len(self.user_agent_list)} user agents')
    
    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        request.headers['User-Agent'] = user_agent
        spider.logger.debug(f'Using User-Agent: {user_agent[:50]}...')
        return None


class ProxyRotationMiddleware:
    """
    Rotates proxies to avoid IP-based blocking.
    Note: This requires a list of working proxies to be effective.
    """
    
    def __init__(self, proxy_list: Optional[List[str]] = None):
        self.proxy_list = proxy_list or []
        self.current_proxy_index = 0
        
    @classmethod
    def from_crawler(cls, crawler):
        proxy_list = crawler.settings.getlist('PROXY_LIST', [])
        middleware = cls(proxy_list=proxy_list)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
    
    def spider_opened(self, spider):
        if self.proxy_list:
            spider.logger.info(f'ProxyRotationMiddleware: Using {len(self.proxy_list)} proxies')
        else:
            spider.logger.info('ProxyRotationMiddleware: No proxies configured')
    
    def process_request(self, request, spider):
        if not self.proxy_list:
            return None
            
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        
        request.meta['proxy'] = proxy
        spider.logger.debug(f'Using proxy: {proxy}')
        return None


class RetryMiddleware:
    """
    Custom retry middleware with exponential backoff.
    """
    
    def __init__(self, max_retry_times=3, retry_http_codes=None):
        self.max_retry_times = max_retry_times
        self.retry_http_codes = retry_http_codes or [500, 502, 503, 504, 408, 429]
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            max_retry_times=crawler.settings.getint('RETRY_TIMES', 3),
            retry_http_codes=crawler.settings.getlist('RETRY_HTTP_CODES', [500, 502, 503, 504, 408, 429])
        )
    
    def process_response(self, request, response, spider):
        if response.status in self.retry_http_codes:
            retry_times = request.meta.get('retry_times', 0) + 1
            
            if retry_times <= self.max_retry_times:
                spider.logger.warning(f'Retrying {request.url} (attempt {retry_times}/{self.max_retry_times})')
                
                # Exponential backoff
                delay = 2 ** retry_times
                request.meta['retry_times'] = retry_times
                request.meta['download_delay'] = delay
                
                return request
            else:
                spider.logger.error(f'Max retries exceeded for {request.url}')
                
        return response


class JavaScriptMiddleware:
    """
    Middleware to handle JavaScript-rendered pages.
    This is a placeholder - in production, you might want to use Splash or Selenium.
    """
    
    def __init__(self):
        self.js_keywords = ['javascript:', 'onclick=', 'document.', 'window.']
        
    def process_response(self, request, response, spider):
        # Simple check for JavaScript content
        if isinstance(response, HtmlResponse):
            body_text = response.text.lower()
            has_js = any(keyword in body_text for keyword in self.js_keywords)
            
            if has_js:
                spider.logger.debug(f'JavaScript detected in {request.url}')
                # In a real implementation, you might:
                # 1. Use Splash/Selenium to render the page
                # 2. Extract data from the rendered HTML
                # 3. Return a new response with the rendered content
                
        return response


class RespectRobotsMiddleware:
    """
    Enhanced robots.txt compliance middleware.
    """
    
    def __init__(self):
        self.robots_cache = {}
        
    def process_request(self, request, spider):
        # Basic robots.txt respect - Scrapy handles this by default
        # This middleware can be extended for custom robots.txt handling
        spider.logger.debug(f'Processing request: {request.url}')
        return None


class SessionMiddleware:
    """
    Maintains session cookies for sites that require login.
    """
    
    def __init__(self):
        self.sessions = {}
        
    def process_request(self, request, spider):
        # Maintain session cookies per domain
        domain = request.url.split('/')[2]
        
        if domain in self.sessions:
            request.cookies = self.sessions[domain]
            spider.logger.debug(f'Using cached session for {domain}')
            
        return None
    
    def process_response(self, request, response, spider):
        # Store session cookies
        domain = request.url.split('/')[2]
        
        if response.cookies:
            self.sessions[domain] = dict(response.cookies)
            spider.logger.debug(f'Cached session for {domain}')
            
        return response


class ErrorHandlingMiddleware:
    """
    Enhanced error handling and logging.
    """
    
    def __init__(self):
        self.error_count = 0
        
    def process_exception(self, request, exception, spider):
        self.error_count += 1
        spider.logger.error(f'Exception processing {request.url}: {exception}')
        
        # Log additional context
        if hasattr(exception, 'response'):
            spider.logger.error(f'Response status: {exception.response.status}')
            
        return None
    
    def spider_closed(self, spider):
        spider.logger.info(f'ErrorHandlingMiddleware: Total errors encountered: {self.error_count}')
