"""
RSS Health Checker Cog
Monitors RSS feed health and alerts admins about issues
"""

import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import feedparser

from logger_config import get_logger
from database import get_database

logger = get_logger('health_checker')


class HealthChecker(commands.Cog):
    """Monitor RSS feed health and uptime"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = get_database()
        
        # Health tracking
        self.feed_failures: Dict[int, int] = {}  # feed_id -> failure_count
        self.feed_last_check: Dict[int, datetime] = {}
        self.feed_uptime: Dict[int, float] = {}  # feed_id -> uptime %
        
        # Configuration
        self.check_interval_hours = 6
        self.max_failures_before_disable = 3
        self.timeout_seconds = 10
        
        # Start health checker
        self.health_check_task.start()
        logger.info("RSS Health Checker initialized")
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.health_check_task.cancel()
    
    @tasks.loop(hours=6)
    async def health_check_task(self):
        """Periodic health check for all RSS feeds"""
        logger.info("Starting RSS health check...")
        
        all_feeds = self.db.get_all_rss_feeds()
        results = []
        
        for feed in all_feeds:
            if not feed['enabled']:
                continue
            
            feed_id = feed['feed_id']
            url = feed['url']
            source_name = feed['source_name']
            
            # Check feed health
            is_healthy, error_msg = await self.check_feed_health(url)
            
            self.feed_last_check[feed_id] = datetime.now()
            
            if is_healthy:
                # Reset failure count on success
                self.feed_failures[feed_id] = 0
                results.append(f"✅ {source_name}: OK")
                logger.info(f"Feed '{source_name}' is healthy")
            else:
                # Increment failure count
                self.feed_failures[feed_id] = self.feed_failures.get(feed_id, 0) + 1
                failure_count = self.feed_failures[feed_id]
                
                results.append(f"❌ {source_name}: {error_msg} (Failures: {failure_count}/{self.max_failures_before_disable})")
                logger.warning(f"Feed '{source_name}' failed: {error_msg}")
                
                # Auto-disable after max failures
                if failure_count >= self.max_failures_before_disable:
                    await self.disable_feed(feed_id, source_name, error_msg)
                else:
                    # Alert admin about failure
                    await self.alert_admin(feed['guild_id'], source_name, error_msg, failure_count)
        
        # Calculate uptime statistics
        self.update_uptime_stats()
        
        logger.info(f"Health check completed: {len(results)} feeds checked")
    
    async def check_feed_health(self, url: str) -> tuple[bool, str]:
        """
        Check if RSS feed is accessible and valid
        Returns: (is_healthy, error_message)
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as response:
                    if response.status != 200:
                        return False, f"HTTP {response.status}"
                    
                    # Check if content is valid RSS/Atom
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    if feed.bozo:  # feedparser's way of saying "this isn't valid XML"
                        return False, f"Invalid XML: {feed.bozo_exception}"
                    
                    if not feed.entries:
                        return False, "No entries found in feed"
                    
                    return True, ""
        
        except asyncio.TimeoutError:
            return False, f"Timeout after {self.timeout_seconds}s"
        except aiohttp.ClientError as e:
            return False, f"Connection error: {str(e)[:50]}"
        except Exception as e:
            return False, f"Unknown error: {str(e)[:50]}"
    
    async def alert_admin(self, guild_id: int, source_name: str, error: str, failure_count: int):
        """Send alert to admin channel about feed failure"""
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            
            # Try to find admin/mod channel
            admin_channel = None
            for channel in guild.text_channels:
                if any(keyword in channel.name.lower() for keyword in ['admin', 'mod', 'log', 'alert']):
                    admin_channel = channel
                    break
            
            if not admin_channel:
                # Fallback: use first text channel
                admin_channel = guild.text_channels[0] if guild.text_channels else None
            
            if admin_channel:
                embed = discord.Embed(
                    title="⚠️ RSS Feed Health Alert",
                    description=f"Feed **{source_name}** is experiencing issues",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="Error", value=error, inline=False)
                embed.add_field(name="Failure Count", value=f"{failure_count}/{self.max_failures_before_disable}", inline=True)
                embed.add_field(name="Action", value="Feed will be auto-disabled after 3 failures", inline=True)
                embed.set_footer(text="RSS Health Checker")
                
                await admin_channel.send(embed=embed)
                logger.info(f"Sent alert for '{source_name}' to guild {guild_id}")
        
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    async def disable_feed(self, feed_id: int, source_name: str, error: str):
        """Disable feed after too many failures"""
        try:
            with self.db.connect() as conn:
                conn.execute('UPDATE rss_feeds SET enabled = 0 WHERE id = ?', (feed_id,))
            
            logger.warning(f"Auto-disabled feed '{source_name}' after {self.max_failures_before_disable} failures")
            
            # Send notification to all guilds using this feed
            feed_info = None
            for feed in self.db.get_all_rss_feeds():
                if feed['feed_id'] == feed_id:
                    feed_info = feed
                    break
            
            if feed_info:
                guild = self.bot.get_guild(feed_info['guild_id'])
                if guild:
                    admin_channel = guild.text_channels[0] if guild.text_channels else None
                    if admin_channel:
                        embed = discord.Embed(
                            title="🔴 RSS Feed Auto-Disabled",
                            description=f"Feed **{source_name}** has been automatically disabled",
                            color=discord.Color.red(),
                            timestamp=datetime.now()
                        )
                        embed.add_field(name="Reason", value=f"Failed {self.max_failures_before_disable} consecutive health checks", inline=False)
                        embed.add_field(name="Last Error", value=error, inline=False)
                        embed.add_field(name="Action Required", value="Please check the feed URL and re-enable manually if fixed", inline=False)
                        embed.set_footer(text="RSS Health Checker")
                        
                        await admin_channel.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Failed to disable feed: {e}")
    
    def update_uptime_stats(self):
        """Update uptime statistics for all feeds"""
        for feed_id in self.feed_failures:
            # Simple uptime calculation: (total_checks - failures) / total_checks
            # This is a simplified version; you could store more detailed history
            failures = self.feed_failures.get(feed_id, 0)
            # Assume 1 check every 6 hours = 4 checks per day
            # If we track last 7 days = 28 total checks
            total_checks = 28
            successful_checks = total_checks - min(failures, total_checks)
            uptime_percent = (successful_checks / total_checks) * 100
            
            self.feed_uptime[feed_id] = uptime_percent
    
    @health_check_task.before_loop
    async def before_health_check(self):
        """Wait for bot to be ready before starting health checks"""
        await self.bot.wait_until_ready()
        logger.info("Bot ready, health checker starting...")
    
    @commands.command(name='checkfeeds')
    @commands.has_permissions(administrator=True)
    async def check_feeds_command(self, ctx):
        """Manually trigger RSS health check (Admin only)"""
        await ctx.send("🔍 Running RSS health check...")
        
        all_feeds = self.db.get_all_rss_feeds()
        
        if not all_feeds:
            await ctx.send("No RSS feeds configured.")
            return
        
        results = []
        for feed in all_feeds:
            if not feed['enabled']:
                continue
            
            is_healthy, error = await self.check_feed_health(feed['url'])
            
            if is_healthy:
                results.append(f"✅ **{feed['source_name']}**: Healthy")
            else:
                results.append(f"❌ **{feed['source_name']}**: {error}")
        
        # Send results in chunks to avoid message length limit
        chunk_size = 10
        for i in range(0, len(results), chunk_size):
            chunk = results[i:i+chunk_size]
            await ctx.send("\n".join(chunk))
        
        await ctx.send(f"✅ Health check completed: {len(results)} feeds checked")
    
    @commands.command(name='feedstats')
    @commands.has_permissions(administrator=True)
    async def feed_stats_command(self, ctx):
        """Show RSS feed uptime statistics (Admin only)"""
        embed = discord.Embed(
            title="📊 RSS Feed Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        all_feeds = self.db.get_all_rss_feeds()
        
        for feed in all_feeds[:10]:  # Limit to first 10 feeds
            feed_id = feed['feed_id']
            uptime = self.feed_uptime.get(feed_id, 100.0)
            failures = self.feed_failures.get(feed_id, 0)
            last_check = self.feed_last_check.get(feed_id)
            
            status = "✅ Enabled" if feed['enabled'] else "🔴 Disabled"
            last_check_str = last_check.strftime("%Y-%m-%d %H:%M") if last_check else "Never"
            
            embed.add_field(
                name=f"{feed['source_name']} ({status})",
                value=f"Uptime: {uptime:.1f}% | Failures: {failures} | Last check: {last_check_str}",
                inline=False
            )
        
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Setup function for loading the cog"""
    await bot.add_cog(HealthChecker(bot))
    logger.info("HealthChecker cog loaded")
