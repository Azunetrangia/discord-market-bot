"""
News source fetchers - Abstract base and implementations
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import aiohttp
import feedparser
import asyncio
import os
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

from logger_config import get_logger
from config import BotConfig as bot_config
from utils import retry_with_backoff, rate_limiters
from .models import Article, NewsSource

logger = get_logger('news_sources')
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')


class BaseFetcher(ABC):
    """Abstract base class for news fetchers"""
    
    def __init__(self, source: NewsSource):
        self.source = source
        self.limiter = rate_limiters.get(source.name.lower(), None)
    
    @abstractmethod
    async def fetch(self) -> List[Article]:
        """Fetch articles from source"""
        pass
    
    async def fetch_with_retry(self) -> List[Article]:
        """Fetch with rate limiting and retry logic"""
        if self.limiter:
            await self.limiter.wait_if_needed()
        
        @retry_with_backoff(max_retries=3, base_delay=2)
        async def _fetch():
            return await self.fetch()
        
        try:
            return await _fetch()
        except Exception as e:
            logger.error(f"Failed to fetch from {self.source.name}: {e}")
            return []


class GlassnodeSource(BaseFetcher):
    """Glassnode Insights RSS fetcher"""
    
    def __init__(self):
        source = NewsSource(
            name='Glassnode',
            type='rss',
            color=0x5B8DEE,
            icon_url='https://www.google.com/s2/favicons?domain=glassnode.com&sz=128',
            rate_limit=30
        )
        super().__init__(source)
        self.url = 'https://insights.glassnode.com/feed/'
    
    async def fetch(self) -> List[Article]:
        """Fetch from Glassnode RSS"""
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, self.url)
        
        articles = []
        for entry in feed.entries[:bot_config.GLASSNODE_MAX_ARTICLES]:
            article = Article(
                id=entry.get('link', entry.get('id', '')),
                title=entry.get('title', 'Không có tiêu đề'),
                url=entry.get('link', ''),
                source='glassnode',
                description=entry.get('description', '') or entry.get('summary', ''),
                published_at=entry.get('published', ''),
            )
            articles.append(article)
        
        logger.info(f"Fetched {len(articles)} articles from Glassnode")
        return articles


class SantimentSource(BaseFetcher):
    """Santiment API fetcher"""
    
    def __init__(self):
        source = NewsSource(
            name='Santiment',
            type='api',
            color=0x26A69A,
            icon_url='https://www.google.com/s2/favicons?domain=santiment.net&sz=128',
            rate_limit=20
        )
        super().__init__(source)
        self.api_key = os.getenv('SANTIMENT_API_KEY')
    
    async def fetch(self) -> List[Article]:
        """Fetch from Santiment API"""
        if not self.api_key:
            logger.warning("SANTIMENT_API_KEY not found")
            return []
        
        query = """
        {
          allInsights(page: 1, pageSize: 5) {
            id
            title
            text
            readyState
            publishedAt
            user {
              username
            }
          }
        }
        """
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Apikey {self.api_key}'
            }
            timeout = aiohttp.ClientTimeout(total=bot_config.REQUEST_TIMEOUT)
            
            async with session.post(
                'https://api.santiment.net/graphql',
                json={'query': query},
                headers=headers,
                timeout=timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'errors' in data:
                        logger.error(f"Santiment GraphQL errors: {data['errors']}")
                        return []
                    
                    insights = data.get('data', {}).get('allInsights', [])
                    
                    articles = []
                    for insight in insights:
                        if insight.get('readyState') == 'published':
                            # Clean HTML from text
                            soup = BeautifulSoup(insight.get('text', ''), 'html.parser')
                            clean_text = soup.get_text()[:400]
                            
                            article = Article(
                                id=str(insight.get('id')),
                                title=insight.get('title', 'Không có tiêu đề'),
                                url=f"https://insights.santiment.net/read/{insight.get('id')}",
                                source='santiment',
                                description=clean_text,
                                published_at=insight.get('publishedAt', ''),
                                author=insight.get('user', {}).get('username', 'Santiment'),
                            )
                            articles.append(article)
                    
                    logger.info(f"Fetched {len(articles)} insights from Santiment")
                    return articles
        
        return []


class TheBlockSource(BaseFetcher):
    """The Block RSS fetcher"""
    
    def __init__(self):
        source = NewsSource(
            name='TheBlock',
            type='rss',
            color=0x1E1E1E,
            icon_url='https://www.google.com/s2/favicons?domain=theblock.co&sz=128',
            rate_limit=60
        )
        super().__init__(source)
        self.url = 'https://www.theblock.co/rss.xml'
    
    async def fetch(self) -> List[Article]:
        """Fetch from The Block RSS"""
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, self.url)
        
        articles = []
        for entry in feed.entries[:bot_config.THEBLOCK_MAX_ARTICLES]:
            soup = BeautifulSoup(entry.get('description', ''), 'html.parser')
            clean_description = soup.get_text()[:400]
            
            article = Article(
                id=entry.get('link', entry.get('id', '')),
                title=entry.get('title', 'Không có tiêu đề'),
                url=entry.get('link', ''),
                source='theblock',
                description=clean_description,
                published_at=entry.get('published', ''),
            )
            articles.append(article)
        
        logger.info(f"Fetched {len(articles)} articles from The Block")
        return articles


class PhutcryptoSource(BaseFetcher):
    """5phutcrypto.io web scraper"""
    
    def __init__(self):
        source = NewsSource(
            name='5phutcrypto',
            type='scraper',
            color=0xFF6B00,
            icon_url='https://www.google.com/s2/favicons?domain=5phutcrypto.io&sz=128',
            rate_limit=60
        )
        super().__init__(source)
        self.url = 'https://5phutcrypto.io/'
    
    async def fetch(self) -> List[Article]:
        """Scrape from 5phutcrypto.io"""
        async with aiohttp.ClientSession() as session:
            timeout = aiohttp.ClientTimeout(total=bot_config.REQUEST_TIMEOUT)
            async with session.get(self.url, timeout=timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    articles = []
                    for h3 in soup.find_all('h3'):
                        link_tag = h3.find('a', href=True)
                        if link_tag and link_tag['href'].startswith('https://5phutcrypto.io/'):
                            # Skip special links
                            if any(skip in link_tag['href'] for skip in ['/tag/', '/author/', '/goc-nhin/', '/chuyen-sau/']):
                                continue
                            
                            # Find image
                            image_url = None
                            parent = h3.find_parent()
                            if parent:
                                img = parent.find('img')
                                if img and 'data-src' in img.attrs:
                                    image_url = img['data-src']
                                elif img and 'src' in img.attrs and not img['src'].startswith('data:'):
                                    image_url = img['src']
                            
                            article = Article(
                                id=link_tag['href'],
                                title=link_tag.get_text(strip=True),
                                url=link_tag['href'],
                                source='5phutcrypto',
                                description='',
                                published_at=datetime.now(VN_TZ).isoformat(),
                                image_url=image_url,
                            )
                            articles.append(article)
                            
                            if len(articles) >= bot_config.PHUTCRYPTO_MAX_ARTICLES:
                                break
                    
                    logger.info(f"Fetched {len(articles)} articles from 5phutcrypto")
                    return articles[:bot_config.PHUTCRYPTO_MAX_ARTICLES]
        
        return []


class RSSSource(BaseFetcher):
    """Generic RSS feed fetcher"""
    
    def __init__(self, name: str, url: str, color: int = 0xFFA500):
        source = NewsSource(
            name=name,
            type='rss',
            color=color,
            icon_url=self._get_feed_icon(url, name),
            rate_limit=100
        )
        super().__init__(source)
        self.url = url
    
    @staticmethod
    def _get_feed_icon(feed_url: str, feed_name: str) -> str:
        """Get icon URL for RSS feed"""
        from urllib.parse import urlparse
        
        domain_map = {
            'vnexpress': 'vnexpress.net',
            'bbc': 'bbc.com',
            'cnn': 'cnn.com',
            'reuters': 'reuters.com',
            'bloomberg': 'bloomberg.com',
            'cointelegraph': 'cointelegraph.com',
            'decrypt': 'decrypt.co',
        }
        
        domain = None
        for key, mapped_domain in domain_map.items():
            if key in feed_name.lower() or key in feed_url.lower():
                domain = mapped_domain
                break
        
        if not domain:
            parsed = urlparse(feed_url)
            domain = parsed.netloc
        
        if domain:
            return f'https://www.google.com/s2/favicons?domain={domain}&sz=128'
        
        return 'https://cdn-icons-png.flaticon.com/512/888/888846.png'
    
    async def fetch(self) -> List[Article]:
        """Fetch from RSS feed"""
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, self.url)
        
        articles = []
        for entry in feed.entries[:bot_config.RSS_MAX_ENTRIES]:
            # Extract image URL
            image_url = None
            if hasattr(entry, 'media_content') and entry.media_content:
                try:
                    if len(entry.media_content) > 0 and 'url' in entry.media_content[0]:
                        image_url = entry.media_content[0]['url']
                except:
                    pass
            
            if not image_url and hasattr(entry, 'enclosures') and entry.enclosures:
                try:
                    for enclosure in entry.enclosures:
                        if 'image' in enclosure.get('type', '').lower():
                            image_url = enclosure.get('href', '')
                            break
                except:
                    pass
            
            # Clean description
            description = entry.get('summary', entry.get('description', ''))
            if description:
                import html
                import re
                description = re.sub(r'#(\d+);', r'&#\1;', description)
                description = html.unescape(description)
                description = re.sub(r'<[^>]+>', '', description)
                description = re.sub(r'\s+', ' ', description).strip()
            
            article = Article(
                id=entry.get('id', entry.get('link', '')),
                title=entry.get('title', 'Không có tiêu đề'),
                url=entry.get('link', ''),
                source=self.source.name,
                description=description,
                published_at=entry.get('published', ''),
                image_url=image_url,
            )
            articles.append(article)
        
        logger.debug(f"Fetched {len(articles)} entries from RSS: {self.url}")
        return articles
