"""
Unit tests for news models
"""

import pytest
from cogs.news.models import Article, NewsSource


def test_article_creation():
    """Test basic article creation"""
    article = Article(
        id='123',
        title='Test Article',
        url='https://test.com',
        source='test',
        description='Test description'
    )
    
    assert article.id == '123'
    assert article.title == 'Test Article'
    assert article.url == 'https://test.com'
    assert article.source == 'test'


def test_article_title_truncation():
    """Test that long titles are truncated"""
    long_title = 'A' * 300
    article = Article(
        id='1',
        title=long_title,
        url='http://test.com',
        source='test'
    )
    
    assert len(article.title) <= 250
    assert article.title.endswith('...')


def test_article_description_truncation():
    """Test that long descriptions are truncated"""
    long_desc = 'B' * 500
    article = Article(
        id='1',
        title='Test',
        url='http://test.com',
        source='test',
        description=long_desc
    )
    
    assert len(article.description) <= 400
    assert article.description.endswith('...')


def test_article_empty_title():
    """Test that empty titles are handled"""
    article = Article(
        id='1',
        title='',
        url='http://test.com',
        source='test'
    )
    
    assert article.title == 'Không có tiêu đề'


def test_article_to_dict():
    """Test article serialization"""
    article = Article(
        id='123',
        title='Test',
        url='https://test.com',
        source='test'
    )
    
    data = article.to_dict()
    
    assert isinstance(data, dict)
    assert data['id'] == '123'
    assert data['title'] == 'Test'
    assert data['source'] == 'test'


def test_news_source_creation():
    """Test news source configuration"""
    source = NewsSource(
        name='Test Source',
        type='rss',
        color=0xFF0000,
        icon_url='https://test.com/icon.png',
        rate_limit=60
    )
    
    assert source.name == 'Test Source'
    assert source.type == 'rss'
    assert source.color == 0xFF0000
    assert source.rate_limit == 60
    assert source.enabled is True


def test_news_source_invalid_type():
    """Test that invalid source types are rejected"""
    with pytest.raises(ValueError, match="Invalid source type"):
        NewsSource(
            name='Test',
            type='invalid',
            color=0xFF0000,
            icon_url='test.png',
            rate_limit=60
        )


def test_news_source_invalid_rate_limit():
    """Test that invalid rate limits are rejected"""
    with pytest.raises(ValueError, match="Rate limit must be at least 1"):
        NewsSource(
            name='Test',
            type='rss',
            color=0xFF0000,
            icon_url='test.png',
            rate_limit=0
        )
