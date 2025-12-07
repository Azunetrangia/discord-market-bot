"""
News Cog - Refactored modular version
Main orchestration for news aggregation and posting
"""

from discord.ext import commands, tasks
import discord
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from deep_translator import GoogleTranslator
import pytz

from logger_config import get_logger
from config import BotConfig as bot_config
from database import get_database
from translation_cache import get_translation_cache
from utils.rate_limiter import get_rate_limiter
from .news.models import Article
from .news.sources import (
    GlassnodeSource,
    SantimentSource,
    TheBlockSource,
    PhutcryptoSource,
    RSSSource
)
from .news.views import NewsMenuView
from .news.formatters import EmbedFormatter

logger = get_logger('news_cog')
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')


class NewsCog(commands.Cog):
    """Cog quản lý tin tức tự động - Refactored version"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = get_database()
        self.cache = get_translation_cache()
        self.rate_limiter = get_rate_limiter()  # Add rate limiter
        self.temp_rss_data: Dict[int, Dict] = {}
        self.translator = GoogleTranslator(source='auto', target='vi')
        
        # Initialize news sources
        self.sources = {
            'glassnode': GlassnodeSource(),
            'santiment': SantimentSource(),
            'theblock': TheBlockSource(),
            '5phutcrypto': PhutcryptoSource(),
        }
        
        # Migration flag
        self._migrated = False
        
        # Start background task
        self.news_checker.start()
        
    def cog_unload(self):
        """Stop task when cog unloads"""
        self.news_checker.cancel()
    
    # ==================== Config Management ====================
    
    def load_news_config(self, guild_id: Optional[int] = None) -> Dict:
        """Load news configuration for specific guild from database"""
        if not guild_id:
            return {
                "glassnode_channel": None,
                "santiment_channel": None,
                "5phutcrypto_channel": None,
                "theblock_channel": None,
                "rss_feeds": []
            }
        
        try:
            config = self.db.get_guild_config(guild_id)
            
            # Map database column names to expected keys
            return {
                "glassnode_channel": config.get('glassnode_channel'),
                "santiment_channel": config.get('santiment_channel'),
                "5phutcrypto_channel": config.get('phutcrypto_channel'),
                "theblock_channel": config.get('theblock_channel'),
                "rss_feeds": config.get('rss_feeds', [])
            }
        except Exception as e:
            logger.error(f"Error loading config for guild {guild_id}: {e}")
            return {
                "glassnode_channel": None,
                "santiment_channel": None,
                "5phutcrypto_channel": None,
                "theblock_channel": None,
                "rss_feeds": []
            }
    
    def save_news_config(self, config: Dict, guild_id: int):
        """Save news configuration for specific guild to database"""
        try:
            self.db.save_guild_config(guild_id, config)
            logger.info(f"Saved config for guild {guild_id}")
        except Exception as e:
            logger.error(f"Error saving config for guild {guild_id}: {e}", exc_info=True)
    
    
    # ==================== Translation ====================
    
    async def translate_to_vietnamese(self, text: str, max_length: Optional[int] = None) -> str:
        """Translate text to Vietnamese with caching and rate limiting"""
        if not text:
            return ""
        
        try:
            # Truncate if needed
            if max_length and len(text) > max_length:
                text = text[:max_length]
            
            # Google Translate max 5000 chars
            if len(text) > 4500:
                text = text[:4500]
            
            # Check cache first (skip rate limiting if cached)
            cached = self.cache.get(text)
            if cached:
                return cached
            
            # Apply rate limiting before API call
            await self.rate_limiter.acquire('google_translate')
            
            # Translate in executor
            loop = asyncio.get_event_loop()
            translated = await loop.run_in_executor(None, self.translator.translate, text)
            
            # Cache the result
            self.cache.set(text, translated)
            
            logger.debug(f"Translated: {len(text)} -> {len(translated)} chars")
            return translated
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    # ==================== News Processing ====================
    
    async def process_and_post_articles(
        self,
        articles: List[Article],
        channel: discord.TextChannel,
        guild_id: int,
        source_key: str,
        is_vietnamese: bool = False
    ):
        """Process and post articles to channel"""
        for article in articles:
            # Check database instead of in-memory list
            if not self.db.is_article_posted(guild_id, article.id, source_key):
                try:
                    # Translate if needed
                    if is_vietnamese:
                        translated_title = article.title
                        translated_desc = article.description or "Không có mô tả"
                    else:
                        translated_title = await self.translate_to_vietnamese(article.title, 250)
                        if article.description:
                            translated_desc = await self.translate_to_vietnamese(article.description, 400)
                        else:
                            translated_desc = "Đọc thêm tại nguồn"
                    
                    # Create embed
                    embed = EmbedFormatter.create_embed(
                        article,
                        translated_title,
                        translated_desc,
                        is_vietnamese
                    )
                    
                    # Send to channel
                    await channel.send(embed=embed)
                    
                    # Mark as posted in database
                    self.db.mark_article_posted(
                        guild_id,
                        article.id,
                        source_key,
                        article.title,
                        article.url
                    )
                    
                    logger.info(f"Posted: {article.source} - {article.title[:50]}")
                    
                except Exception as e:
                    logger.error(f"Error posting article {article.id}: {e}", exc_info=True)
                    continue
    
    # ==================== Background Task ====================
    
    @tasks.loop(minutes=3)
    async def news_checker(self):
        """Background task - check for new articles every 3 minutes"""
        logger.info(f"NEWS_CHECKER STARTED at {datetime.now(VN_TZ)}")
        logger.info(f"Found {len(self.bot.guilds)} guilds to process")
        
        for guild in self.bot.guilds:
            logger.info(f"Processing guild: {guild.name} (ID: {guild.id})")
            
            try:
                config = self.load_news_config(guild.id)
                
                # Process each source
                for source_name, source in self.sources.items():
                    channel_key = f'{source_name}_channel'
                    channel_id = config.get(channel_key)
                    
                    if channel_id:
                        channel = self.bot.get_channel(channel_id)
                        if channel:
                            articles = await source.fetch_with_retry()
                            
                            if articles:
                                await self.process_and_post_articles(
                                    articles,
                                    channel,
                                    guild.id,
                                    source_name,
                                    is_vietnamese=(source_name == '5phutcrypto')
                                )
                
                # Process RSS feeds
                for feed_config in config.get('rss_feeds', []):
                    channel = self.bot.get_channel(feed_config['channel_id'])
                    if channel:
                        feed_url = feed_config['url']
                        feed_name = feed_config['name']
                        
                        # Fetch RSS
                        rss_source = RSSSource(feed_name, feed_url)
                        articles = await rss_source.fetch_with_retry()
                        
                        if articles:
                            is_vietnamese = 'vnexpress' in feed_url.lower() or 'vn' in feed_name.lower()
                            
                            await self.process_and_post_articles(
                                articles,
                                channel,
                                guild.id,
                                f'rss:{feed_url}',
                                is_vietnamese
                            )
                
            except Exception as e:
                logger.error(f"Error processing guild {guild.id}: {e}", exc_info=True)
                continue
        
        # Log cache stats every check cycle
        self.cache.print_stats()
    
    @news_checker.before_loop
    async def before_news_checker(self):
        """Wait for bot to be ready"""
        await self.bot.wait_until_ready()
    
    # ==================== Commands ====================
    
    async def list_sources_command(self, interaction: discord.Interaction):
        """List all configured news sources"""
        config = self.load_news_config(interaction.guild_id)
        
        embed = discord.Embed(
            title="📋 Danh sách Nguồn Tin",
            color=discord.Color.blue()
        )
        
        # List each source type
        source_channels = [
            ('glassnode', '📊 Glassnode Insights'),
            ('santiment', '📈 Santiment API'),
            ('5phutcrypto', '💰 5 Phút Crypto'),
            ('theblock', '📰 The Block')
        ]
        
        for key, name in source_channels:
            channel_id = config.get(f'{key}_channel')
            if channel_id:
                channel = interaction.guild.get_channel(channel_id)
                if channel:
                    embed.add_field(
                        name=name,
                        value=f"Kênh: {channel.mention}\nID: `{channel_id}`",
                        inline=False
                    )
        
        # List RSS feeds
        if config.get('rss_feeds'):
            rss_list = ""
            for feed in config['rss_feeds']:
                channel = interaction.guild.get_channel(feed['channel_id'])
                rss_list += f"**{feed['name']}**\n"
                rss_list += f"URL: `{feed['url']}`\n"
                if channel:
                    rss_list += f"Kênh: {channel.mention}\n\n"
                else:
                    rss_list += f"⚠️ Kênh không tìm thấy (ID: `{feed['channel_id']}`)\n\n"
            
            if rss_list:
                embed.add_field(
                    name=f"📰 RSS Feeds ({len(config['rss_feeds'])} feeds)",
                    value=rss_list if len(rss_list) < 1024 else rss_list[:1000] + "...",
                    inline=False
                )
        
        if not any(config.get(f'{k}_channel') for k, _ in source_channels) and not config.get('rss_feeds'):
            embed.description = "Chưa có nguồn tin nào được cài đặt."
        
        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot: commands.Bot):
    """Setup function to load cog"""
    await bot.add_cog(NewsCog(bot))
