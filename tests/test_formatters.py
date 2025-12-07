"""
Unit tests for embed formatters
"""

import pytest
import discord
from datetime import datetime
from cogs.news.models import Article
from cogs.news.formatters import EmbedFormatter


def test_format_title_with_emoji():
    """Test title formatting with emojis"""
    assert EmbedFormatter._format_title('glassnode', 'Test') == '📊 Test'
    assert EmbedFormatter._format_title('santiment', 'Test') == '📈 Test'
    assert EmbedFormatter._format_title('theblock', 'Test') == '📰 Test'
    assert EmbedFormatter._format_title('5phutcrypto', 'Test') == '💰 Test'
    assert EmbedFormatter._format_title('unknown', 'Test') == '🌍 Test'


def test_get_color():
    """Test color mapping"""
    assert EmbedFormatter._get_color('glassnode') == 0x5B8DEE
    assert EmbedFormatter._get_color('santiment') == 0x26A69A
    assert EmbedFormatter._get_color('theblock') == 0x1E1E1E
    assert EmbedFormatter._get_color('5phutcrypto') == 0xFF6B00
    assert EmbedFormatter._get_color('unknown') == 0xFFA500


def test_create_embed_basic():
    """Test basic embed creation"""
    article = Article(
        id='123',
        title='Test Article',
        url='https://test.com',
        source='glassnode',
        description='Test description'
    )
    
    embed = EmbedFormatter.create_embed(
        article,
        translated_title='Bài viết test',
        translated_description='Mô tả test',
        is_vietnamese=False
    )
    
    assert isinstance(embed, discord.Embed)
    assert '📊 Bài viết test' in embed.title
    assert embed.url == 'https://test.com'
    assert 'Mô tả test' in embed.description
    assert embed.color.value == 0x5B8DEE


def test_create_embed_with_image():
    """Test embed with image"""
    article = Article(
        id='123',
        title='Test',
        url='https://test.com',
        source='5phutcrypto',
        image_url='https://test.com/image.jpg'
    )
    
    embed = EmbedFormatter.create_embed(
        article,
        'Test',
        'Description',
        is_vietnamese=True
    )
    
    assert embed.image.url == 'https://test.com/image.jpg'


def test_create_embed_vietnamese_source():
    """Test Vietnamese source (no translation note)"""
    article = Article(
        id='1',
        title='Tin tức',
        url='https://vnexpress.net',
        source='vnexpress'
    )
    
    embed = EmbedFormatter.create_embed(
        article,
        'Tin tức',
        'Mô tả',
        is_vietnamese=True
    )
    
    # Vietnamese source should not have "Đã dịch tự động" in footer
    assert 'Đã dịch tự động' not in embed.footer.text


def test_create_embed_foreign_source():
    """Test foreign source (with translation note)"""
    article = Article(
        id='1',
        title='News',
        url='https://bbc.com',
        source='bbc'
    )
    
    embed = EmbedFormatter.create_embed(
        article,
        'Tin tức',
        'Mô tả',
        is_vietnamese=False
    )
    
    # Foreign source should have translation note
    assert 'Đã dịch tự động' in embed.footer.text


def test_get_footer_text():
    """Test footer text generation"""
    footer = EmbedFormatter._get_footer_text('glassnode', False)
    assert 'Glassnode' in footer
    assert 'Đã dịch tự động' in footer
    
    footer = EmbedFormatter._get_footer_text('5phutcrypto', True)
    assert '5 Phút Crypto' in footer
    assert 'Đã dịch tự động' not in footer


def test_get_author_info():
    """Test author info extraction"""
    article = Article(
        id='1',
        title='Test',
        url='http://test.com',
        source='santiment',
        author='TestUser'
    )
    
    name, icon = EmbedFormatter._get_author_info(article)
    assert 'Santiment' in name
    assert 'TestUser' in name
    assert 'santiment.net' in icon
