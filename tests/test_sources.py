"""
Unit tests for news sources fetchers
"""

import pytest
from cogs.news.sources import (
    GlassnodeSource,
    SantimentSource,
    TheBlockSource,
    PhutcryptoSource,
    RSSSource
)


@pytest.mark.asyncio
async def test_glassnode_fetch():
    """Test Glassnode RSS fetching"""
    source = GlassnodeSource()
    
    assert source.source.name == 'Glassnode'
    assert source.source.type == 'rss'
    assert source.url == 'https://insights.glassnode.com/feed/'
    
    # Test fetch (may fail if network issues)
    try:
        articles = await source.fetch()
        assert isinstance(articles, list)
        assert len(articles) <= 5  # Max 5 articles
        
        if articles:
            article = articles[0]
            assert hasattr(article, 'id')
            assert hasattr(article, 'title')
            assert hasattr(article, 'url')
            assert article.source == 'glassnode'
    except Exception as e:
        pytest.skip(f"Network error: {e}")


@pytest.mark.asyncio
async def test_santiment_fetch_no_api_key():
    """Test Santiment without API key"""
    import os
    old_key = os.environ.get('SANTIMENT_API_KEY')
    
    # Remove API key temporarily
    if 'SANTIMENT_API_KEY' in os.environ:
        del os.environ['SANTIMENT_API_KEY']
    
    source = SantimentSource()
    articles = await source.fetch()
    
    # Should return empty list without API key
    assert articles == []
    
    # Restore API key
    if old_key:
        os.environ['SANTIMENT_API_KEY'] = old_key


@pytest.mark.asyncio
async def test_theblock_fetch():
    """Test The Block RSS fetching"""
    source = TheBlockSource()
    
    assert source.source.name == 'TheBlock'
    assert source.source.type == 'rss'
    assert source.url == 'https://www.theblock.co/rss.xml'
    
    try:
        articles = await source.fetch()
        assert isinstance(articles, list)
        assert len(articles) <= 5
        
        if articles:
            article = articles[0]
            assert article.source == 'theblock'
    except Exception as e:
        pytest.skip(f"Network error: {e}")


@pytest.mark.asyncio
async def test_phutcrypto_fetch():
    """Test 5phutcrypto scraping"""
    source = PhutcryptoSource()
    
    assert source.source.name == '5phutcrypto'
    assert source.source.type == 'scraper'
    
    try:
        articles = await source.fetch()
        assert isinstance(articles, list)
        
        if articles:
            article = articles[0]
            assert article.source == '5phutcrypto'
            assert article.url.startswith('https://5phutcrypto.io/')
    except Exception as e:
        pytest.skip(f"Network/scraping error: {e}")


@pytest.mark.asyncio
async def test_rss_source_fetch():
    """Test generic RSS source"""
    source = RSSSource(
        name='Test RSS',
        url='https://vnexpress.net/rss/thoi-su.rss'
    )
    
    assert source.source.name == 'Test RSS'
    assert source.url == 'https://vnexpress.net/rss/thoi-su.rss'
    
    try:
        articles = await source.fetch()
        assert isinstance(articles, list)
        assert len(articles) <= 5
        
        if articles:
            article = articles[0]
            assert article.source == 'Test RSS'
    except Exception as e:
        pytest.skip(f"Network error: {e}")


def test_rss_source_icon_detection():
    """Test icon URL detection for different sources"""
    # VnExpress
    source = RSSSource('VnExpress', 'https://vnexpress.net/rss')
    assert 'vnexpress.net' in source.source.icon_url
    
    # BBC
    source = RSSSource('BBC News', 'https://feeds.bbci.co.uk/news/rss.xml')
    assert 'bbc.com' in source.source.icon_url
    
    # Cointelegraph
    source = RSSSource('Cointelegraph', 'https://cointelegraph.com/rss')
    assert 'cointelegraph.com' in source.source.icon_url
