"""
Embed formatters for different news sources
"""

import discord
from datetime import datetime
from typing import Optional
import pytz

from .models import Article

VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')


class EmbedFormatter:
    """Format articles into Discord embeds"""
    
    # Color mappings for sources
    COLORS = {
        'glassnode': 0x5B8DEE,
        'santiment': 0x26A69A,
        'theblock': 0x1E1E1E,
        '5phutcrypto': 0xFF6B00,
        'vnexpress': 0xC81E1E,
        'bbc': 0xBB1919,
        'cnn': 0xCC0000,
        'reuters': 0xFF6600,
        'bloomberg': 0x000000,
        'default': 0xFFA500
    }
    
    @classmethod
    def create_embed(
        cls,
        article: Article,
        translated_title: str,
        translated_description: str,
        is_vietnamese: bool = False
    ) -> discord.Embed:
        """
        Create Discord embed for article
        
        Args:
            article: Article object
            translated_title: Translated title
            translated_description: Translated description
            is_vietnamese: Whether source is Vietnamese (no translation needed)
        
        Returns:
            discord.Embed: Formatted embed
        """
        # Get color for source
        color = cls._get_color(article.source)
        
        # Create embed
        embed = discord.Embed(
            title=cls._format_title(article.source, translated_title),
            url=article.url,
            description=translated_description or "Không có mô tả",
            color=color,
            timestamp=cls._parse_timestamp(article.published_at)
        )
        
        # Set author
        author_name, icon_url = cls._get_author_info(article)
        embed.set_author(name=author_name, icon_url=icon_url)
        
        # Set image if available
        if article.image_url:
            try:
                embed.set_image(url=article.image_url)
            except:
                pass
        
        # Set footer
        footer_text = cls._get_footer_text(article.source, is_vietnamese)
        embed.set_footer(text=footer_text, icon_url=icon_url)
        
        return embed
    
    @staticmethod
    def _format_title(source: str, title: str) -> str:
        """Add emoji prefix to title based on source"""
        emoji_map = {
            'glassnode': '📊',
            'santiment': '📈',
            'theblock': '📰',
            '5phutcrypto': '💰',
            'default': '🌍'
        }
        emoji = emoji_map.get(source.lower(), emoji_map['default'])
        return f"{emoji} {title}"
    
    @classmethod
    def _get_color(cls, source: str) -> int:
        """Get color for source"""
        return cls.COLORS.get(source.lower(), cls.COLORS['default'])
    
    @staticmethod
    def _get_author_info(article: Article) -> tuple[str, str]:
        """Get author name and icon URL"""
        source_info = {
            'glassnode': ('Glassnode Insights', 'https://www.google.com/s2/favicons?domain=glassnode.com&sz=128'),
            'santiment': (f'Santiment Insights • {article.author}' if article.author else 'Santiment Insights', 
                         'https://www.google.com/s2/favicons?domain=santiment.net&sz=128'),
            'theblock': ('The Block', 'https://www.google.com/s2/favicons?domain=theblock.co&sz=128'),
            '5phutcrypto': ('5 Phút Crypto', 'https://www.google.com/s2/favicons?domain=5phutcrypto.io&sz=128'),
        }
        
        return source_info.get(article.source.lower(), (article.source, ''))
    
    @staticmethod
    def _get_footer_text(source: str, is_vietnamese: bool) -> str:
        """Get footer text based on source"""
        footer_map = {
            'glassnode': '📈 Nguồn: Glassnode • On-chain Analytics',
            'santiment': '📈 Nguồn: Santiment • Market Intelligence',
            'theblock': '📰 Nguồn: The Block • Institutional-grade Crypto News',
            '5phutcrypto': '💰 Nguồn: 5 Phút Crypto • Tin tức & phân tích',
        }
        
        footer = footer_map.get(source.lower(), f'📡 Nguồn: {source} • RSS Feed')
        
        if not is_vietnamese and source.lower() not in ['5phutcrypto']:
            footer += ' • Đã dịch tự động'
        
        return footer
    
    @staticmethod
    def _parse_timestamp(published_at: Optional[str]) -> Optional[datetime]:
        """Parse published timestamp"""
        if not published_at:
            return datetime.now(VN_TZ)
        
        try:
            # Try ISO format first
            if published_at.endswith('Z'):
                published_at = published_at.replace('Z', '+00:00')
            return datetime.fromisoformat(published_at)
        except:
            try:
                # Try parsing as datetime object
                from email.utils import parsedate_to_datetime
                return parsedate_to_datetime(published_at)
            except:
                return datetime.now(VN_TZ)
