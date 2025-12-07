"""
Data models for news articles and sources
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Article:
    """Represents a news article"""
    
    id: str
    title: str
    url: str
    source: str
    description: str = ""
    published_at: Optional[str] = None
    image_url: Optional[str] = None
    author: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and clean data after initialization"""
        # Ensure title is not empty
        if not self.title:
            self.title = "Không có tiêu đề"
        
        # Truncate long titles
        if len(self.title) > 250:
            self.title = self.title[:247] + "..."
        
        # Truncate long descriptions
        if len(self.description) > 400:
            self.description = self.description[:397] + "..."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'description': self.description,
            'published_at': self.published_at,
            'image_url': self.image_url,
            'author': self.author,
            'metadata': self.metadata,
        }


@dataclass
class NewsSource:
    """Represents a news source configuration"""
    
    name: str
    type: str  # 'rss', 'api', 'scraper'
    color: int
    icon_url: str
    rate_limit: int = 60  # calls per minute
    enabled: bool = True
    
    def __post_init__(self):
        """Validate source configuration"""
        if self.rate_limit < 1:
            raise ValueError("Rate limit must be at least 1 call per minute")
        
        if self.type not in ['rss', 'api', 'scraper']:
            raise ValueError(f"Invalid source type: {self.type}")
