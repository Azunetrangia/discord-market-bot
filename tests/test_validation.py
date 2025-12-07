"""
Unit tests for input validation
"""

import pytest
from cogs.news.views import AddRSSModal


class TestRSSURLValidation:
    """Test RSS URL validation"""
    
    def test_valid_https_url(self):
        """Test valid HTTPS URLs"""
        assert AddRSSModal._validate_rss_url('https://vnexpress.net/rss.xml')
        assert AddRSSModal._validate_rss_url('https://feeds.bbci.co.uk/news/rss.xml')
        assert AddRSSModal._validate_rss_url('https://cointelegraph.com/rss')
    
    def test_valid_http_url(self):
        """Test valid HTTP URLs"""
        assert AddRSSModal._validate_rss_url('http://example.com/rss.xml')
    
    def test_invalid_no_protocol(self):
        """Test URLs without protocol"""
        assert not AddRSSModal._validate_rss_url('vnexpress.net/rss.xml')
        assert not AddRSSModal._validate_rss_url('www.example.com/rss')
    
    def test_invalid_localhost(self):
        """Test that localhost is blocked"""
        assert not AddRSSModal._validate_rss_url('http://localhost/rss.xml')
        assert not AddRSSModal._validate_rss_url('https://localhost:8080/feed')
    
    def test_invalid_loopback_ip(self):
        """Test that loopback IPs are blocked"""
        assert not AddRSSModal._validate_rss_url('http://127.0.0.1/rss.xml')
        assert not AddRSSModal._validate_rss_url('https://127.0.0.1:8000/feed')
    
    def test_invalid_zero_ip(self):
        """Test that 0.0.0.0 is blocked"""
        assert not AddRSSModal._validate_rss_url('http://0.0.0.0/rss.xml')
    
    def test_invalid_too_short(self):
        """Test that too short URLs are rejected"""
        assert not AddRSSModal._validate_rss_url('http://a')
        assert not AddRSSModal._validate_rss_url('https://b')
    
    def test_invalid_no_domain(self):
        """Test URLs without proper domain"""
        assert not AddRSSModal._validate_rss_url('http://nodot')
        assert not AddRSSModal._validate_rss_url('https://alsonodot')
    
    def test_edge_cases(self):
        """Test edge cases"""
        assert not AddRSSModal._validate_rss_url('')
        assert not AddRSSModal._validate_rss_url('not-a-url')
        assert not AddRSSModal._validate_rss_url('ftp://example.com/rss')
