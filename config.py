# Bot Configuration
# Cài đặt cấu hình cho Discord News Bot

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class BotConfig:
    """Configuration class chứa tất cả constants và settings"""
    
    # News checking intervals
    NEWS_CHECK_INTERVAL: int = 180  # seconds (3 minutes)
    
    # Translation settings  
    TRANSLATION_MAX_LENGTH: int = 4096  # Max characters for translation
    TRANSLATION_TIMEOUT: int = 30  # seconds
    
    # API retry settings
    MAX_RETRIES: int = 3
    RETRY_BASE_DELAY: int = 1  # seconds
    RETRY_MAX_DELAY: int = 60  # seconds
    
    # HTTP request settings
    REQUEST_TIMEOUT: int = 30  # seconds
    USER_AGENT: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    # File paths
    DATA_DIR: str = 'data'
    LOGS_DIR: str = 'logs'
    CONFIG_FILE: str = 'data/news_config.json'
    LAST_POSTS_FILE: str = 'data/last_post_ids.json'
    
    # Discord embed limits
    EMBED_TITLE_MAX: int = 256
    EMBED_DESCRIPTION_MAX: int = 4096
    EMBED_FIELD_VALUE_MAX: int = 1024
    EMBED_FOOTER_MAX: int = 2048
    
    # RSS Feed settings
    RSS_MAX_ENTRIES: int = 5  # Max entries to fetch per RSS feed
    RSS_CACHE_TTL: int = 300  # seconds (5 minutes)
    
    # News source limits
    GLASSNODE_MAX_ARTICLES: int = 5
    SANTIMENT_MAX_ARTICLES: int = 5
    THEBLOCK_MAX_ARTICLES: int = 5
    PHUTCRYPTO_MAX_ARTICLES: int = 5
    
    @classmethod
    def from_env(cls) -> 'BotConfig':
        """Load configuration from environment variables"""
        return cls(
            NEWS_CHECK_INTERVAL=int(os.getenv('NEWS_CHECK_INTERVAL', 180)),
            TRANSLATION_MAX_LENGTH=int(os.getenv('TRANSLATION_MAX_LENGTH', 4096)),
            TRANSLATION_TIMEOUT=int(os.getenv('TRANSLATION_TIMEOUT', 30)),
            MAX_RETRIES=int(os.getenv('MAX_RETRIES', 3)),
            REQUEST_TIMEOUT=int(os.getenv('REQUEST_TIMEOUT', 30)),
        )
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.NEWS_CHECK_INTERVAL < 60:
            raise ValueError("NEWS_CHECK_INTERVAL must be at least 60 seconds")
        
        if self.MAX_RETRIES < 1:
            raise ValueError("MAX_RETRIES must be at least 1")
        
        if self.REQUEST_TIMEOUT < 5:
            raise ValueError("REQUEST_TIMEOUT must be at least 5 seconds")


# Global config instance
config = BotConfig()
