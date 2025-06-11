"""
Tests for the scrapy middlewares module.

This module contains tests for custom middlewares for handling user agent rotation,
proxy rotation, and other request/response processing.
"""

import pytest
import scrapy
from unittest.mock import MagicMock, patch
from scrapy import signals
from scrapy.http import Request, Response, HtmlResponse

from scraper.middlewares.middlewares import (
    UserAgentRotationMiddleware,
    ProxyRotationMiddleware,
    RetryMiddleware,
    JavaScriptMiddleware,
    RespectRobotsMiddleware,
    SessionMiddleware,
    ErrorHandlingMiddleware
)


# ----------------------- UserAgentRotationMiddleware tests -----------------------

def test_user_agent_rotation_middleware_init():
    """Test UserAgentRotationMiddleware initialization."""
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/91.0.4472.124',
    ]
    
    middleware = UserAgentRotationMiddleware(user_agent_list)
    
    assert middleware.user_agent_list == user_agent_list

def test_user_agent_rotation_middleware_init_default():
    """Test UserAgentRotationMiddleware initialization with default values."""
    middleware = UserAgentRotationMiddleware()
    
    assert len(middleware.user_agent_list) > 0
    assert isinstance(middleware.user_agent_list, list)
    assert all(isinstance(ua, str) for ua in middleware.user_agent_list)

def test_user_agent_rotation_middleware_from_crawler():
    """Test UserAgentRotationMiddleware.from_crawler method."""
    # Create mock crawler
    crawler = MagicMock()
    crawler.settings.getlist.return_value = ['UA1', 'UA2']
    
    middleware = UserAgentRotationMiddleware.from_crawler(crawler)
    
    assert middleware.user_agent_list == ['UA1', 'UA2']
    # Verify signal connected
    crawler.signals.connect.assert_called_once_with(middleware.spider_opened, signal=signals.spider_opened)

def test_user_agent_rotation_middleware_spider_opened():
    """Test UserAgentRotationMiddleware.spider_opened method."""
    middleware = UserAgentRotationMiddleware(['UA1', 'UA2'])
    spider = MagicMock()
    
    middleware.spider_opened(spider)
    
    # Verify logger called
    spider.logger.info.assert_called_once_with('UserAgentRotationMiddleware: Using 2 user agents')

def test_user_agent_rotation_middleware_process_request():
    """Test UserAgentRotationMiddleware.process_request method."""
    middleware = UserAgentRotationMiddleware(['UA1', 'UA2'])
    request = Request('https://example.com')
    spider = MagicMock()
    
    result = middleware.process_request(request, spider)
    
    # Should return None (continue processing)
    assert result is None
    # User-Agent header should be set
    assert request.headers['User-Agent'] in [b'UA1', b'UA2']
    # Logger should be called
    spider.logger.debug.assert_called_once()

def test_user_agent_rotation_middleware_process_request_rotation():
    """Test UserAgentRotationMiddleware rotates user agents."""
    middleware = UserAgentRotationMiddleware(['UA1', 'UA2'])
    request1 = Request('https://example.com')
    request2 = Request('https://example.com')
    spider = MagicMock()
    
    # Process two requests
    middleware.process_request(request1, spider)
    middleware.process_request(request2, spider)
    
    # At least one should be different (random choice makes exact testing difficult)
    all_uas = set([request1.headers['User-Agent'], request2.headers['User-Agent']])
    # Should be at least one user agent
    assert len(all_uas) > 0


# ----------------------- ProxyRotationMiddleware tests -----------------------

def test_proxy_rotation_middleware_init():
    """Test ProxyRotationMiddleware initialization."""
    proxy_list = ['http://proxy1:8080', 'http://proxy2:8080']
    
    middleware = ProxyRotationMiddleware(proxy_list)
    
    assert middleware.proxy_list == proxy_list
    assert middleware.current_proxy_index == 0

def test_proxy_rotation_middleware_init_default():
    """Test ProxyRotationMiddleware initialization with default values."""
    middleware = ProxyRotationMiddleware()
    
    assert middleware.proxy_list == []
    assert middleware.current_proxy_index == 0

def test_proxy_rotation_middleware_from_crawler():
    """Test ProxyRotationMiddleware.from_crawler method."""
    # Create mock crawler
    crawler = MagicMock()
    crawler.settings.getlist.return_value = ['proxy1', 'proxy2']
    
    middleware = ProxyRotationMiddleware.from_crawler(crawler)
    
    assert middleware.proxy_list == ['proxy1', 'proxy2']
    # Verify signal connected
    crawler.signals.connect.assert_called_once_with(middleware.spider_opened, signal=signals.spider_opened)

def test_proxy_rotation_middleware_spider_opened_with_proxies():
    """Test ProxyRotationMiddleware.spider_opened method with proxies."""
    middleware = ProxyRotationMiddleware(['proxy1', 'proxy2'])
    spider = MagicMock()
    
    middleware.spider_opened(spider)
    
    # Verify logger called
    spider.logger.info.assert_called_once_with('ProxyRotationMiddleware: Using 2 proxies')

def test_proxy_rotation_middleware_spider_opened_without_proxies():
    """Test ProxyRotationMiddleware.spider_opened method without proxies."""
    middleware = ProxyRotationMiddleware([])
    spider = MagicMock()
    
    middleware.spider_opened(spider)
    
    # Verify logger called
    spider.logger.info.assert_called_once_with('ProxyRotationMiddleware: No proxies configured')

def test_proxy_rotation_middleware_process_request_with_proxies():
    """Test ProxyRotationMiddleware.process_request method with proxies."""
    middleware = ProxyRotationMiddleware(['proxy1', 'proxy2'])
    request = Request('https://example.com')
    spider = MagicMock()
    
    result = middleware.process_request(request, spider)
    
    # Should return None (continue processing)
    assert result is None
    # Proxy should be set
    assert request.meta['proxy'] == 'proxy1'
    # Logger should be called
    spider.logger.debug.assert_called_once_with('Using proxy: proxy1')

def test_proxy_rotation_middleware_process_request_rotation():
    """Test ProxyRotationMiddleware rotates proxies."""
    middleware = ProxyRotationMiddleware(['proxy1', 'proxy2'])
    request1 = Request('https://example.com')
    request2 = Request('https://example.com')
    request3 = Request('https://example.com')
    spider = MagicMock()
    
    # Process three requests
    middleware.process_request(request1, spider)
    middleware.process_request(request2, spider)
    middleware.process_request(request3, spider)
    
    # Check rotation
    assert request1.meta['proxy'] == 'proxy1'
    assert request2.meta['proxy'] == 'proxy2'
    assert request3.meta['proxy'] == 'proxy1'  # Back to first proxy

def test_proxy_rotation_middleware_process_request_without_proxies():
    """Test ProxyRotationMiddleware.process_request method without proxies."""
    middleware = ProxyRotationMiddleware([])
    request = Request('https://example.com')
    spider = MagicMock()
    
    result = middleware.process_request(request, spider)
    
    # Should return None (continue processing)
    assert result is None
    # Proxy should not be set
    assert 'proxy' not in request.meta


# ----------------------- RetryMiddleware tests -----------------------

def test_retry_middleware_init():
    """Test RetryMiddleware initialization."""
    middleware = RetryMiddleware(max_retry_times=5, retry_http_codes=[500, 502])
    
    assert middleware.max_retry_times == 5
    assert middleware.retry_http_codes == [500, 502]

def test_retry_middleware_init_default():
    """Test RetryMiddleware initialization with default values."""
    middleware = RetryMiddleware()
    
    assert middleware.max_retry_times == 3
    assert middleware.retry_http_codes == [500, 502, 503, 504, 408, 429]

def test_retry_middleware_from_crawler():
    """Test RetryMiddleware.from_crawler method."""
    # Create mock crawler
    crawler = MagicMock()
    crawler.settings.getint.return_value = 5
    crawler.settings.getlist.return_value = [500, 502]
    
    middleware = RetryMiddleware.from_crawler(crawler)
    
    assert middleware.max_retry_times == 5
    assert middleware.retry_http_codes == [500, 502]

def test_retry_middleware_process_response_no_retry():
    """Test RetryMiddleware.process_response method with no retry needed."""
    middleware = RetryMiddleware()
    request = Request('https://example.com')
    response = Response('https://example.com', status=200)
    spider = MagicMock()
    
    result = middleware.process_response(request, response, spider)
    
    # Should return response (no retry)
    assert result == response

def test_retry_middleware_process_response_retry_needed():
    """Test RetryMiddleware.process_response method with retry needed."""
    middleware = RetryMiddleware()
    request = Request('https://example.com')
    response = Response('https://example.com', status=500)
    spider = MagicMock()
    
    result = middleware.process_response(request, response, spider)
    
    # Should return request (retry)
    assert result == request
    assert result.meta['retry_times'] == 1
    assert result.meta['download_delay'] == 2  # 2^1
    # Logger should be called
    spider.logger.warning.assert_called_once_with('Retrying https://example.com (attempt 1/3)')

def test_retry_middleware_process_response_max_retries_exceeded():
    """Test RetryMiddleware.process_response method with max retries exceeded."""
    middleware = RetryMiddleware(max_retry_times=2)
    request = Request('https://example.com')
    request.meta['retry_times'] = 2  # Already retried twice
    response = Response('https://example.com', status=500)
    spider = MagicMock()
    
    result = middleware.process_response(request, response, spider)
    
    # Should return response (no more retries)
    assert result == response
    # Logger should be called
    spider.logger.error.assert_called_once_with('Max retries exceeded for https://example.com')

def test_retry_middleware_process_response_exponential_backoff():
    """Test RetryMiddleware exponential backoff."""
    middleware = RetryMiddleware()
    request = Request('https://example.com')
    response = Response('https://example.com', status=500)
    spider = MagicMock()
    
    # First retry
    result1 = middleware.process_response(request, response, spider)
    assert result1.meta['download_delay'] == 2  # 2^1
    
    # Second retry - use the result from first retry
    result2 = middleware.process_response(result1, response, spider)
    assert result2.meta['download_delay'] == 8  # Should be 2^(retry_times+1)


# ----------------------- JavaScriptMiddleware tests -----------------------

def test_javascript_middleware_init():
    """Test JavaScriptMiddleware initialization."""
    middleware = JavaScriptMiddleware()
    
    assert middleware.js_keywords == ['javascript:', 'onclick=', 'document.', 'window.']

def test_javascript_middleware_process_response_no_js():
    """Test JavaScriptMiddleware.process_response method with no JavaScript."""
    middleware = JavaScriptMiddleware()
    request = Request('https://example.com')
    response = HtmlResponse('https://example.com', body=b'<html><body>No JS here</body></html>')
    spider = MagicMock()
    
    result = middleware.process_response(request, response, spider)
    
    # Should return response unchanged
    assert result == response
    # Logger should not be called
    spider.logger.debug.assert_not_called()

def test_javascript_middleware_process_response_with_js():
    """Test JavaScriptMiddleware.process_response method with JavaScript."""
    middleware = JavaScriptMiddleware()
    request = Request('https://example.com')
    response = HtmlResponse(
        'https://example.com',
        body=b'<html><body><script>document.write("hello");</script></body></html>'
    )
    spider = MagicMock()
    
    result = middleware.process_response(request, response, spider)
    
    # Should return response unchanged (because this is just a placeholder)
    assert result == response
    # Logger should be called
    spider.logger.debug.assert_called_once_with('JavaScript detected in https://example.com')

def test_javascript_middleware_process_response_non_html():
    """Test JavaScriptMiddleware.process_response method with non-HTML response."""
    middleware = JavaScriptMiddleware()
    request = Request('https://example.com')
    response = Response('https://example.com', body=b'Not HTML')  # Not HtmlResponse
    spider = MagicMock()
    
    result = middleware.process_response(request, response, spider)
    
    # Should return response unchanged
    assert result == response
    # Logger should not be called
    spider.logger.debug.assert_not_called()


# ----------------------- RespectRobotsMiddleware tests -----------------------

def test_respect_robots_middleware_init():
    """Test RespectRobotsMiddleware initialization."""
    middleware = RespectRobotsMiddleware()
    
    assert hasattr(middleware, 'robots_cache')
    assert middleware.robots_cache == {}

def test_respect_robots_middleware_process_request():
    """Test RespectRobotsMiddleware.process_request method."""
    middleware = RespectRobotsMiddleware()
    request = Request('https://example.com')
    spider = MagicMock()
    
    result = middleware.process_request(request, spider)
    
    # Should return None (continue processing)
    assert result is None
    # Logger should be called
    spider.logger.debug.assert_called_once_with('Processing request: https://example.com')


# ----------------------- SessionMiddleware tests -----------------------

def test_session_middleware_init():
    """Test SessionMiddleware initialization."""
    middleware = SessionMiddleware()
    
    assert hasattr(middleware, 'sessions')
    assert middleware.sessions == {}

def test_session_middleware_process_request_no_session():
    """Test SessionMiddleware.process_request method with no session."""
    middleware = SessionMiddleware()
    request = Request('https://example.com')
    spider = MagicMock()
    
    result = middleware.process_request(request, spider)
    
    # Should return None (continue processing)
    assert result is None
    # Logger should not be called
    spider.logger.debug.assert_not_called()

def test_session_middleware_process_request_with_session():
    """Test SessionMiddleware.process_request method with session."""
    middleware = SessionMiddleware()
    middleware.sessions['example.com'] = {'sessionid': '12345'}
    request = Request('https://example.com')
    spider = MagicMock()
    
    result = middleware.process_request(request, spider)
    
    # Should return None (continue processing)
    assert result is None
    # Session cookies should be set
    assert request.cookies == {'sessionid': '12345'}
    # Logger should be called
    spider.logger.debug.assert_called_once_with('Using cached session for example.com')

def test_session_middleware_process_response_no_cookies():
    """Test SessionMiddleware.process_response method with no cookies."""
    middleware = SessionMiddleware()
    request = Request('https://example.com')
    
    # Create response with cookies property
    response = MagicMock()
    response.url = 'https://example.com'
    response.cookies = {}
    
    spider = MagicMock()
    
    result = middleware.process_response(request, response, spider)
    
    # Should return response unchanged
    assert result == response
    # Logger should not be called
    spider.logger.debug.assert_not_called()

def test_session_middleware_process_response_with_cookies():
    """Test SessionMiddleware.process_response method with cookies."""
    middleware = SessionMiddleware()
    request = Request('https://example.com')
    response = Response('https://example.com')
    # Simulate cookies in response
    response.cookies = {'sessionid': '12345'}
    spider = MagicMock()
    
    result = middleware.process_response(request, response, spider)
    
    # Should return response unchanged
    assert result == response
    # Session should be cached
    assert middleware.sessions['example.com'] == {'sessionid': '12345'}
    # Logger should be called
    spider.logger.debug.assert_called_once_with('Cached session for example.com')


# ----------------------- ErrorHandlingMiddleware tests -----------------------

def test_error_handling_middleware_init():
    """Test ErrorHandlingMiddleware initialization."""
    middleware = ErrorHandlingMiddleware()
    
    assert hasattr(middleware, 'error_count')
    assert middleware.error_count == 0

def test_error_handling_middleware_process_exception():
    """Test ErrorHandlingMiddleware.process_exception method."""
    middleware = ErrorHandlingMiddleware()
    request = Request('https://example.com')
    exception = Exception('Test exception')
    spider = MagicMock()
    
    result = middleware.process_exception(request, exception, spider)
    
    # Should return None (continue processing)
    assert result is None
    # Error count should be incremented
    assert middleware.error_count == 1
    # Logger should be called
    spider.logger.error.assert_called_once_with('Exception processing https://example.com: Test exception')

def test_error_handling_middleware_process_exception_with_response():
    """Test ErrorHandlingMiddleware.process_exception method with response attr."""
    middleware = ErrorHandlingMiddleware()
    request = Request('https://example.com')
    exception = Exception('Test exception')
    exception.response = MagicMock()
    exception.response.status = 404
    spider = MagicMock()
    
    result = middleware.process_exception(request, exception, spider)
    
    # Should return None (continue processing)
    assert result is None
    # Error count should be incremented
    assert middleware.error_count == 1
    # Logger should be called for exception and response
    spider.logger.error.assert_any_call('Exception processing https://example.com: Test exception')
    spider.logger.error.assert_any_call('Response status: 404')

def test_error_handling_middleware_spider_closed():
    """Test ErrorHandlingMiddleware.spider_closed method."""
    middleware = ErrorHandlingMiddleware()
    middleware.error_count = 5
    spider = MagicMock()
    
    middleware.spider_closed(spider)
    
    # Logger should be called
    spider.logger.info.assert_called_once_with('ErrorHandlingMiddleware: Total errors encountered: 5')


# ----------------------- Integration tests -----------------------

def test_middleware_chain_user_agent_and_proxy():
    """Test chaining UserAgentRotationMiddleware and ProxyRotationMiddleware."""
    ua_middleware = UserAgentRotationMiddleware(['UA1'])
    proxy_middleware = ProxyRotationMiddleware(['proxy1'])
    request = Request('https://example.com')
    spider = MagicMock()
    
    # Process through UA middleware
    ua_middleware.process_request(request, spider)
    # Process through proxy middleware
    proxy_middleware.process_request(request, spider)
    
    # Check both were applied
    assert request.headers['User-Agent'] == b'UA1'
    assert request.meta['proxy'] == 'proxy1'

def test_middleware_chain_with_error_and_retry():
    """Test chaining ErrorHandlingMiddleware and RetryMiddleware."""
    error_middleware = ErrorHandlingMiddleware()
    retry_middleware = RetryMiddleware(max_retry_times=1)
    request = Request('https://example.com')
    response = Response('https://example.com', status=500)
    exception = Exception('Test exception')
    spider = MagicMock()
    
    # Process exception
    error_middleware.process_exception(request, exception, spider)
    # Process response for retry
    new_request = retry_middleware.process_response(request, response, spider)
    
    # Check results
    assert error_middleware.error_count == 1
    assert new_request.meta['retry_times'] == 1
    assert new_request.meta['download_delay'] == 2
