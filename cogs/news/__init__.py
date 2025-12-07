"""
News module for Discord Bot
Modularized structure for better maintainability
"""

from .models import Article, NewsSource
from .sources import (
    GlassnodeSource,
    SantimentSource,
    TheBlockSource,
    PhutcryptoSource,
    RSSSource
)
from .views import (
    AddRSSModal,
    ChannelSelectView,
    RemoveRSSView,
    QuickSetupView,
    PresetRSSSelectView,
    NewsMenuView
)
from .formatters import EmbedFormatter

__all__ = [
    'Article',
    'NewsSource',
    'GlassnodeSource',
    'SantimentSource',
    'TheBlockSource',
    'PhutcryptoSource',
    'RSSSource',
    'AddRSSModal',
    'ChannelSelectView',
    'RemoveRSSView',
    'QuickSetupView',
    'PresetRSSSelectView',
    'NewsMenuView',
    'EmbedFormatter',
]
