import discord
from discord.ext import commands, tasks
import aiohttp
import feedparser
import json
import os
import re
import html
from datetime import datetime, timedelta
import asyncio
from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Timezone UTC+7 (Vietnam/Bangkok)
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

class AddRSSModal(discord.ui.Modal, title="Thêm RSS Feed mới"):
    """Modal để nhập thông tin RSS Feed"""
    
    url = discord.ui.TextInput(
        label="URL của RSS Feed",
        placeholder="https://example.com/rss.xml",
        required=True,
        style=discord.TextStyle.short
    )
    
    name = discord.ui.TextInput(
        label="Tên nguồn tin",
        placeholder="Ví dụ: Tin Vĩ Mô ABC",
        required=True,
        max_length=100,
        style=discord.TextStyle.short
    )
    
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
        
    async def on_submit(self, interaction: discord.Interaction):
        """Xử lý khi user submit Modal"""
        # Lưu thông tin tạm để dùng sau khi chọn channel
        self.cog.temp_rss_data[interaction.user.id] = {
            'url': str(self.url),
            'name': str(self.name)
        }
        
        # Hiển thị ChannelSelect để chọn kênh
        view = ChannelSelectView(self.cog, 'rss')
        embed = discord.Embed(
            title="📺 Chọn kênh đăng tin",
            description=f"Chọn kênh để đăng tin từ nguồn **{self.name}**",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class ChannelSelectView(discord.ui.View):
    """View chứa ChannelSelect để chọn kênh Discord"""
    
    def __init__(self, cog, source_type):
        super().__init__(timeout=60)
        self.cog = cog
        self.source_type = source_type  # 'messari', 'santiment', '5phutcrypto', 'economic_calendar', hoặc 'rss'
        
    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Chọn một kênh...",
        channel_types=[discord.ChannelType.text]
    )
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        """Xử lý khi user chọn channel"""
        channel = select.values[0]
        
        # Load config hiện tại
        config = self.cog.load_news_config(interaction.guild_id)
        
        if self.source_type == 'messari':
            config['messari_channel'] = channel.id
            await interaction.response.edit_message(
                content=f"✅ Đã cài đặt kênh tin Glassnode Insights: {channel.mention}",
                embed=None,
                view=None
            )
            
        elif self.source_type == 'santiment':
            config['santiment_channel'] = channel.id
            await interaction.response.edit_message(
                content=f"✅ Đã cài đặt kênh tin Santiment: {channel.mention}",
                embed=None,
                view=None
            )
            
        elif self.source_type == '5phutcrypto':
            config['5phutcrypto_channel'] = channel.id
            await interaction.response.edit_message(
                content=f"✅ Đã cài đặt kênh tin 5 Phút Crypto: {channel.mention}",
                embed=None,
                view=None
            )
            
        elif self.source_type == 'theblock':
            config['theblock_channel'] = channel.id
            await interaction.response.edit_message(
                content=f"✅ Đã cài đặt kênh tin The Block: {channel.mention}",
                embed=None,
                view=None
            )
            
        elif self.source_type == 'economic_calendar':
            config['economic_calendar_channel'] = channel.id
            await interaction.response.edit_message(
                content=f"✅ Đã cài đặt kênh Economic Calendar: {channel.mention}",
                embed=None,
                view=None
            )
            
        elif self.source_type == 'rss':
            # Lấy thông tin RSS từ temp storage
            rss_data = self.cog.temp_rss_data.get(interaction.user.id)
            if not rss_data:
                await interaction.response.edit_message(
                    content="❌ Lỗi: Không tìm thấy thông tin RSS",
                    embed=None,
                    view=None
                )
                return
                
            # Thêm RSS feed vào config
            config['rss_feeds'].append({
                'name': rss_data['name'],
                'url': rss_data['url'],
                'channel_id': channel.id
            })
            
            # Xóa temp data
            del self.cog.temp_rss_data[interaction.user.id]
            
            await interaction.response.edit_message(
                content=f"✅ Đã thêm RSS Feed **{rss_data['name']}** vào kênh {channel.mention}",
                embed=None,
                view=None
            )
        
        # Lưu config
        self.cog.save_news_config(config, interaction.guild_id)

class RemoveRSSView(discord.ui.View):
    """View để chọn RSS feed cần xóa"""
    
    def __init__(self, cog, rss_feeds):
        super().__init__(timeout=60)
        self.cog = cog
        
        # Tạo options cho select menu
        options = []
        for idx, feed in enumerate(rss_feeds):
            options.append(
                discord.SelectOption(
                    label=feed['name'],
                    description=feed['url'][:100],
                    value=str(idx)
                )
            )
        
        # Thêm select vào view
        select = discord.ui.Select(
            placeholder="Chọn RSS feed để xóa...",
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)
        
    async def select_callback(self, interaction: discord.Interaction):
        """Xử lý khi user chọn RSS để xóa"""
        selected_idx = int(interaction.data['values'][0])
        
        # Load config
        config = self.cog.load_news_config(interaction.guild_id)
        
        # Lấy tên feed trước khi xóa
        feed_name = config['rss_feeds'][selected_idx]['name']
        
        # Xóa feed
        del config['rss_feeds'][selected_idx]
        
        # Lưu config
        self.cog.save_news_config(config, interaction.guild_id)
        
        await interaction.response.edit_message(
            content=f"✅ Đã xóa RSS Feed: **{feed_name}**",
            embed=None,
            view=None
        )

class QuickSetupView(discord.ui.View):
    """View cho Quick Setup với các RSS feeds có sẵn"""
    
    def __init__(self, cog):
        super().__init__(timeout=180)
        self.cog = cog
        
    @discord.ui.button(label="Cài đặt Tất cả", style=discord.ButtonStyle.success, emoji="⚡")
    async def setup_all_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cài đặt tất cả RSS feeds vào channel hiện tại"""
        await interaction.response.defer()
        
        # Lấy channel hiện tại
        channel_id = interaction.channel_id
        
        # Danh sách RSS feeds có sẵn
        preset_feeds = [
            {
                "name": "Thời sự - VnExpress RSS",
                "url": "https://vnexpress.net/rss/thoi-su.rss"
            },
            {
                "name": "BBC News",
                "url": "https://feeds.bbci.co.uk/news/rss.xml"
            },
            {
                "name": "Cointelegraph.com News",
                "url": "https://cointelegraph.com/rss"
            },
            {
                "name": "Cointelegraph - Blockchain",
                "url": "https://cointelegraph.com/rss/tag/blockchain"
            },
            {
                "name": "Cointelegraph - Market Analysis",
                "url": "https://cointelegraph.com/rss/category/market-analysis"
            },
            {
                "name": "Decrypt",
                "url": "https://decrypt.co/feed"
            }
        ]
        
        # Load config hiện tại
        config = self.cog.load_news_config(interaction.guild_id)
        
        # Lấy danh sách URL đã có
        existing_urls = {feed['url'] for feed in config['rss_feeds']}
        
        # Thêm các feed chưa có
        added_count = 0
        for feed in preset_feeds:
            if feed['url'] not in existing_urls:
                config['rss_feeds'].append({
                    'name': feed['name'],
                    'url': feed['url'],
                    'channel_id': channel_id
                })
                added_count += 1
        
        # Lưu config
        self.cog.save_news_config(config, interaction.guild_id)
        
        # Tạo embed kết quả
        embed = discord.Embed(
            title="⚡ Quick Setup Hoàn tất!",
            description=f"Đã cài đặt **{added_count}** RSS feeds vào channel này.",
            color=discord.Color.green()
        )
        
        if added_count > 0:
            feed_list = "\n".join([f"✅ {feed['name']}" for feed in preset_feeds if feed['url'] not in existing_urls])
            embed.add_field(
                name="📰 Feeds đã thêm:",
                value=feed_list,
                inline=False
            )
        
        if added_count < len(preset_feeds):
            embed.add_field(
                name="ℹ️ Lưu ý:",
                value=f"Đã bỏ qua {len(preset_feeds) - added_count} feed(s) đã tồn tại.",
                inline=False
            )
        
        embed.add_field(
            name="⏰ Thông tin:",
            value="Bot sẽ tự động đăng tin mới mỗi 5 phút.\nTin nước ngoài sẽ được dịch sang tiếng Việt.",
            inline=False
        )
        
        await interaction.followup.edit_message(
            message_id=interaction.message.id,
            embed=embed,
            view=None
        )
    
    @discord.ui.button(label="Chọn Từng Cái", style=discord.ButtonStyle.primary, emoji="📝")
    async def select_individual_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cho phép chọn từng RSS feed riêng lẻ"""
        # Tạo SelectMenu với các RSS feeds
        view = PresetRSSSelectView(self.cog)
        
        embed = discord.Embed(
            title="📝 Chọn RSS Feeds",
            description="Chọn các RSS feeds bạn muốn thêm (có thể chọn nhiều):",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="Hủy", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Hủy Quick Setup"""
        await interaction.response.edit_message(
            content="❌ Đã hủy Quick Setup.",
            embed=None,
            view=None
        )

class PresetRSSSelectView(discord.ui.View):
    """View để chọn RSS feeds từ danh sách có sẵn"""
    
    def __init__(self, cog):
        super().__init__(timeout=180)
        self.cog = cog
        
        # Tạo SelectMenu
        select = discord.ui.Select(
            placeholder="Chọn các RSS feeds...",
            min_values=1,
            max_values=6,
            options=[
                discord.SelectOption(
                    label="VnExpress - Tin mới nhất",
                    description="https://vnexpress.net/rss/thoi-su.rss",
                    emoji="🇻🇳",
                    value="https://vnexpress.net/rss/thoi-su.rss"
                ),
                discord.SelectOption(
                    label="BBC News",
                    description="https://feeds.bbci.co.uk/news/rss.xml",
                    emoji="🇬🇧",
                    value="https://feeds.bbci.co.uk/news/rss.xml"
                ),
                discord.SelectOption(
                    label="Cointelegraph - All News",
                    description="https://cointelegraph.com/rss",
                    emoji="₿",
                    value="https://cointelegraph.com/rss"
                ),
                discord.SelectOption(
                    label="Cointelegraph - Blockchain",
                    description="https://cointelegraph.com/rss/tag/blockchain",
                    emoji="⛓️",
                    value="https://cointelegraph.com/rss/tag/blockchain"
                ),
                discord.SelectOption(
                    label="Cointelegraph - Market Analysis",
                    description="https://cointelegraph.com/rss/category/market-analysis",
                    emoji="📊",
                    value="https://cointelegraph.com/rss/category/market-analysis"
                ),
                discord.SelectOption(
                    label="Decrypt",
                    description="https://decrypt.co/feed",
                    emoji="🔐",
                    value="https://decrypt.co/feed"
                )
            ]
        )
        
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        """Xử lý khi user chọn các RSS feeds"""
        selected_urls = interaction.data['values']
        channel_id = interaction.channel_id
        
        # Map URL to name
        url_to_name = {
            "https://vnexpress.net/rss/thoi-su.rss": "Thời sự - VnExpress RSS",
            "https://feeds.bbci.co.uk/news/rss.xml": "BBC News",
            "https://cointelegraph.com/rss": "Cointelegraph.com News",
            "https://cointelegraph.com/rss/tag/blockchain": "Cointelegraph - Blockchain",
            "https://cointelegraph.com/rss/category/market-analysis": "Cointelegraph - Market Analysis",
            "https://decrypt.co/feed": "Decrypt"
        }
        
        # Load config hiện tại
        config = self.cog.load_news_config(interaction.guild_id)
        
        # Lấy danh sách URL đã có
        existing_urls = {feed['url'] for feed in config['rss_feeds']}
        
        # Thêm các feed được chọn
        added_feeds = []
        for url in selected_urls:
            if url not in existing_urls:
                config['rss_feeds'].append({
                    'name': url_to_name.get(url, 'Unknown'),
                    'url': url,
                    'channel_id': channel_id
                })
                added_feeds.append(url_to_name.get(url, 'Unknown'))
        
        # Lưu config
        self.cog.save_news_config(config, interaction.guild_id)
        
        # Tạo embed kết quả
        embed = discord.Embed(
            title="✅ Đã thêm RSS Feeds!",
            description=f"Đã thêm **{len(added_feeds)}** RSS feeds vào channel này.",
            color=discord.Color.green()
        )
        
        if added_feeds:
            embed.add_field(
                name="📰 Feeds đã thêm:",
                value="\n".join([f"✅ {name}" for name in added_feeds]),
                inline=False
            )
        
        if len(added_feeds) < len(selected_urls):
            embed.add_field(
                name="ℹ️ Lưu ý:",
                value=f"Đã bỏ qua {len(selected_urls) - len(added_feeds)} feed(s) đã tồn tại.",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=None)

class NewsMenuView(discord.ui.View):
    """View chính cho menu quản lý tin tức"""
    
    def __init__(self):
        super().__init__(timeout=180)
        
    @discord.ui.select(
        placeholder="Chọn một tùy chọn...",
        options=[
            discord.SelectOption(
                label="⚡ Quick Setup - Tự động cài đặt",
                description="Tự động thêm tất cả RSS feeds phổ biến",
                emoji="⚡",
                value="quick_setup"
            ),
            discord.SelectOption(
                label="Cài đặt kênh tin Glassnode",
                description="Chọn kênh để nhận insights từ Glassnode",
                emoji="📊",
                value="messari"
            ),
            discord.SelectOption(
                label="Cài đặt kênh tin Santiment",
                description="Chọn kênh để nhận tin từ Santiment API",
                emoji="📈",
                value="santiment"
            ),
            discord.SelectOption(
                label="Cài đặt kênh tin 5 Phút Crypto",
                description="Chọn kênh để nhận tin từ 5phutcrypto.io",
                emoji="💰",
                value="5phutcrypto"
            ),
            discord.SelectOption(
                label="Cài đặt kênh tin The Block",
                description="Chọn kênh để nhận tin từ The Block",
                emoji="📰",
                value="theblock"
            ),
            discord.SelectOption(
                label="Thêm một RSS Feed mới",
                description="Thêm nguồn RSS Feed tùy chỉnh",
                emoji="➕",
                value="add_rss"
            ),
            discord.SelectOption(
                label="Xóa một RSS Feed",
                description="Xóa RSS Feed đã cài đặt",
                emoji="🗑️",
                value="remove_rss"
            ),
            discord.SelectOption(
                label="Liệt kê các nguồn tin",
                description="Xem tất cả nguồn tin đang hoạt động",
                emoji="📋",
                value="list_sources"
            )
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Xử lý khi user chọn một option"""
        value = select.values[0]
        
        # Lấy cog instance
        cog = interaction.client.get_cog('NewsCog')
        
        if value == "quick_setup":
            # Hiển thị Quick Setup View
            view = QuickSetupView(cog)
            embed = discord.Embed(
                title="⚡ Quick Setup - Cài đặt Nhanh",
                description=(
                    "Tự động thêm 6 RSS feeds phổ biến:\n\n"
                    "🇻🇳 **VnExpress** - Tin mới nhất\n"
                    "🇬🇧 **BBC News** - Tin quốc tế\n"
                    "₿ **Cointelegraph** - Crypto news\n"
                    "⛓️ **Cointelegraph** - Blockchain\n"
                    "📊 **Cointelegraph** - Market Analysis\n"
                    "🔐 **Decrypt** - Crypto & Web3\n\n"
                    "Chọn **Cài đặt Tất cả** để thêm ngay hoặc **Chọn Từng Cái** để custom."
                ),
                color=discord.Color.gold()
            )
            embed.set_footer(text="Tất cả feeds sẽ được thêm vào channel này")
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif value == "messari":
            # Hiển thị ChannelSelect cho Glassnode
            view = ChannelSelectView(cog, 'messari')
            embed = discord.Embed(
                title="📊 Cài đặt kênh tin Glassnode Insights",
                description="Chọn kênh để nhận insights từ Glassnode (on-chain analytics)",
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif value == "santiment":
            # Hiển thị ChannelSelect cho Santiment
            view = ChannelSelectView(cog, 'santiment')
            embed = discord.Embed(
                title="📈 Cài đặt kênh tin Santiment",
                description="Chọn kênh để nhận tin tức từ Santiment API",
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif value == "5phutcrypto":
            # Hiển thị ChannelSelect cho 5 Phút Crypto
            view = ChannelSelectView(cog, '5phutcrypto')
            embed = discord.Embed(
                title="💰 Cài đặt kênh tin 5 Phút Crypto",
                description="Chọn kênh để nhận tin tức từ 5phutcrypto.io",
                color=discord.Color.orange()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif value == "theblock":
            # Hiển thị ChannelSelect cho The Block
            view = ChannelSelectView(cog, 'theblock')
            embed = discord.Embed(
                title="📰 Cài đặt kênh tin The Block",
                description="Chọn kênh để nhận tin tức từ The Block (institutional-grade crypto news)",
                color=0x1E1E1E  # Màu đen của The Block
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif value == "add_rss":
            # Hiển thị Modal để nhập thông tin RSS
            modal = AddRSSModal(cog)
            await interaction.response.send_modal(modal)
            
        elif value == "remove_rss":
            # Hiển thị danh sách RSS để xóa
            config = cog.load_news_config(interaction.guild_id)
            
            if not config['rss_feeds']:
                await interaction.response.edit_message(
                    content="❌ Không có RSS Feed nào để xóa!",
                    embed=None,
                    view=None
                )
                return
                
            view = RemoveRSSView(cog, config['rss_feeds'])
            embed = discord.Embed(
                title="🗑️ Xóa RSS Feed",
                description="Chọn RSS Feed bạn muốn xóa:",
                color=discord.Color.red()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif value == "list_sources":
            # Liệt kê tất cả nguồn tin
            config = cog.load_news_config(interaction.guild_id)
            
            embed = discord.Embed(
                title="📋 Danh sách Nguồn Tin",
                color=discord.Color.blue()
            )
            
            # Glassnode Insights
            if config['messari_channel']:
                channel = interaction.guild.get_channel(config['messari_channel'])
                if not channel:
                    # Thử fetch từ bot
                    try:
                        channel = await interaction.client.fetch_channel(config['messari_channel'])
                    except:
                        channel = None
                
                if channel:
                    embed.add_field(
                        name="📊 Glassnode Insights",
                        value=f"Kênh: {channel.mention}\nID: `{config['messari_channel']}`",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="📊 Glassnode Insights",
                        value=f"⚠️ Kênh không tìm thấy hoặc bot không có quyền truy cập\nID: `{config['messari_channel']}`",
                        inline=False
                    )
            
            # Santiment
            if config['santiment_channel']:
                channel = interaction.guild.get_channel(config['santiment_channel'])
                if not channel:
                    # Thử fetch từ bot
                    try:
                        channel = await interaction.client.fetch_channel(config['santiment_channel'])
                    except:
                        channel = None
                
                if channel:
                    embed.add_field(
                        name="📈 Santiment API",
                        value=f"Kênh: {channel.mention}\nID: `{config['santiment_channel']}`",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="📈 Santiment API",
                        value=f"⚠️ Kênh không tìm thấy hoặc bot không có quyền truy cập\nID: `{config['santiment_channel']}`",
                        inline=False
                    )
            
            # 5 Phút Crypto
            if config.get('5phutcrypto_channel'):
                channel = interaction.guild.get_channel(config['5phutcrypto_channel'])
                if not channel:
                    # Thử fetch từ bot
                    try:
                        channel = await interaction.client.fetch_channel(config['5phutcrypto_channel'])
                    except:
                        channel = None
                
                if channel:
                    embed.add_field(
                        name="💰 5 Phút Crypto",
                        value=f"Kênh: {channel.mention}\nID: `{config['5phutcrypto_channel']}`",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="💰 5 Phút Crypto",
                        value=f"⚠️ Kênh không tìm thấy hoặc bot không có quyền truy cập\nID: `{config['5phutcrypto_channel']}`",
                        inline=False
                    )
            
            # The Block
            if config.get('theblock_channel'):
                channel = interaction.guild.get_channel(config['theblock_channel'])
                if not channel:
                    # Thử fetch từ bot
                    try:
                        channel = await interaction.client.fetch_channel(config['theblock_channel'])
                    except:
                        channel = None
                
                if channel:
                    embed.add_field(
                        name="📰 The Block",
                        value=f"Kênh: {channel.mention}\nID: `{config['theblock_channel']}`",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="📰 The Block",
                        value=f"⚠️ Kênh không tìm thấy hoặc bot không có quyền truy cập\nID: `{config['theblock_channel']}`",
                        inline=False
                    )
            
            # Economic Calendar
            if config.get('economic_calendar_channel'):
                channel = interaction.guild.get_channel(config['economic_calendar_channel'])
                if not channel:
                    # Thử fetch từ bot
                    try:
                        channel = await interaction.client.fetch_channel(config['economic_calendar_channel'])
                    except:
                        channel = None
                
                if channel:
                    embed.add_field(
                        name="📅 Economic Calendar",
                        value=f"Kênh: {channel.mention}\nID: `{config['economic_calendar_channel']}`",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="📅 Economic Calendar",
                        value=f"⚠️ Kênh không tìm thấy hoặc bot không có quyền truy cập\nID: `{config['economic_calendar_channel']}`",
                        inline=False
                    )
            
            # RSS Feeds
            if config['rss_feeds']:
                rss_list = ""
                for feed in config['rss_feeds']:
                    channel = interaction.guild.get_channel(feed['channel_id'])
                    if not channel:
                        # Thử fetch từ bot
                        try:
                            channel = await interaction.client.fetch_channel(feed['channel_id'])
                        except:
                            channel = None
                    
                    rss_list += f"**{feed['name']}**\n"
                    rss_list += f"URL: `{feed['url']}`\n"
                    if channel:
                        rss_list += f"Kênh: {channel.mention}\n\n"
                    else:
                        rss_list += f"⚠️ Kênh không tìm thấy (ID: `{feed['channel_id']}`)\n\n"
                
                embed.add_field(
                    name=f"📰 RSS Feeds ({len(config['rss_feeds'])} feeds)",
                    value=rss_list if len(rss_list) < 1024 else rss_list[:1000] + "...",
                    inline=False
                )
            
            if not config['messari_channel'] and not config['santiment_channel'] and not config.get('5phutcrypto_channel') and not config['rss_feeds']:
                embed.description = "Chưa có nguồn tin nào được cài đặt."
            
            await interaction.response.edit_message(embed=embed, view=None)

class EconomicMenuView(discord.ui.View):
    """View riêng cho Economic Calendar"""
    
    def __init__(self):
        super().__init__(timeout=180)
        
    @discord.ui.select(
        placeholder="Chọn một tùy chọn...",
        options=[
            discord.SelectOption(
                label="Cài đặt kênh Economic Calendar",
                description="Chọn kênh để nhận cập nhật kinh tế",
                emoji="📊",
                value="setup_channel"
            ),
            discord.SelectOption(
                label="Xem các chỉ số đang theo dõi",
                description="Danh sách indicators từ FRED",
                emoji="📋",
                value="list_indicators"
            ),
            discord.SelectOption(
                label="Kiểm tra dữ liệu mới",
                description="Force check dữ liệu kinh tế mới",
                emoji="🔄",
                value="force_check"
            )
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Xử lý khi user chọn option"""
        value = select.values[0]
        cog = interaction.client.get_cog('NewsCog')
        
        if value == "setup_channel":
            view = ChannelSelectView(cog, 'economic_calendar')
            embed = discord.Embed(
                title="📊 Cài đặt kênh Economic Calendar",
                description="Chọn kênh để nhận thông báo về các chỉ số kinh tế quan trọng từ FRED",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif value == "list_indicators":
            embed = discord.Embed(
                title="📋 Các Chỉ Số Đang Theo Dõi",
                description="Dữ liệu từ FRED (Federal Reserve Economic Data)",
                color=discord.Color.blue()
            )
            
            # High impact indicators
            embed.add_field(
                name="🔴 High Impact",
                value=(
                    "• **Federal Funds Rate** (DFF) - Lãi suất Fed\n"
                    "• **Unemployment Rate** (UNRATE) - Tỷ lệ thất nghiệp\n"
                    "• **CPI** (CPIAUCSL) - Chỉ số giá tiêu dùng\n"
                    "• **GDP** (GDP) - Tổng sản phẩm quốc nội\n"
                    "• **Non-Farm Payrolls** (PAYEMS) - Việc làm phi nông nghiệp"
                ),
                inline=False
            )
            
            # Medium impact indicators
            embed.add_field(
                name="🟠 Medium Impact",
                value=(
                    "• **10Y-2Y Treasury Spread** (T10Y2Y)\n"
                    "• **USD/EUR Rate** (DEXUSEU)"
                ),
                inline=False
            )
            
            embed.set_footer(text="Bot kiểm tra cập nhật mỗi 5 phút")
            await interaction.response.edit_message(embed=embed, view=self)
            
        elif value == "force_check":
            await interaction.response.defer(thinking=True)
            
            config = cog.load_news_config(interaction.guild_id)
            if not config.get('economic_calendar_channel'):
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    content="❌ Chưa cài đặt kênh Economic Calendar!",
                    embed=None,
                    view=None
                )
                return
            
            channel = interaction.guild.get_channel(config['economic_calendar_channel'])
            if not channel:
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    content="❌ Không tìm thấy kênh đã cấu hình!",
                    embed=None,
                    view=None
                )
                return
            
            # Fetch và gửi economic data
            events = await cog.fetch_economic_calendar()
            
            if not events:
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    content="ℹ️ Không có dữ liệu kinh tế mới trong lúc này.",
                    embed=None,
                    view=None
                )
                return
            
            # Gửi 3 events đầu tiên
            sent_count = 0
            for event in events[:3]:
                await cog.send_economic_event_update(channel, event, is_update=False)
                sent_count += 1
            
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content=f"✅ Đã gửi {sent_count} chỉ số kinh tế vào {channel.mention}",
                embed=None,
                view=None
            )

class NewsCog(commands.Cog):
    """Cog quản lý tin tức tự động"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_path = 'data/news_config.json'
        self.last_posts_path = 'data/last_post_ids.json'
        self.temp_rss_data = {}  # Lưu tạm data khi thêm RSS
        self.translator = GoogleTranslator(source='auto', target='vi')  # Khởi tạo Google Translator
        
        # Economic Calendar scheduled tasks tracking
        self.scheduled_events = {}  # {event_id: {'pre_alert_posted': bool, 'actual_posted': bool}}
        self.event_tasks = []  # List of scheduled asyncio tasks
        
        # Khởi động background tasks
        self.news_checker.start()
        # Tắt scheduler - chỉ dùng polling mỗi 3 phút
        # self.daily_calendar_summary.start()
        # self.economic_calendar_scheduler.start()
        
    def cog_unload(self):
        """Dừng task khi cog unload"""
        self.news_checker.cancel()
        # Tắt scheduler - chỉ dùng polling mỗi 3 phút
        # self.daily_calendar_summary.cancel()
        # self.economic_calendar_scheduler.cancel()
        
        # Cancel all scheduled event tasks
        for task in self.event_tasks:
            if not task.done():
                task.cancel()
        
    def load_news_config(self, guild_id=None):
        """Load cấu hình tin tức cho guild cụ thể"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                all_configs = json.load(f)
            
            # Nếu là format cũ (không có guilds), migrate sang format mới
            if 'guilds' not in all_configs:
                # Migration: Chuyển config cũ thành format mới
                old_config = all_configs.copy()
                all_configs = {'guilds': {}}
                # Nếu có guild_id, lưu config cũ cho guild đó
                if guild_id:
                    all_configs['guilds'][str(guild_id)] = old_config
                # Lưu lại format mới
                self.save_all_configs(all_configs)
            
            # Trả về config của guild cụ thể
            if guild_id:
                guild_key = str(guild_id)
                if guild_key in all_configs['guilds']:
                    return all_configs['guilds'][guild_key]
            
            # Default config
            return {
                "messari_channel": None,
                "santiment_channel": None,
                "5phutcrypto_channel": None,
                "theblock_channel": None,
                "economic_calendar_channel": None,
                "rss_feeds": []
            }
        except:
            return {
                "messari_channel": None,
                "santiment_channel": None,
                "5phutcrypto_channel": None,
                "theblock_channel": None,
                "economic_calendar_channel": None,
                "rss_feeds": []
            }
    
    def save_news_config(self, config, guild_id):
        """Lưu cấu hình tin tức cho guild cụ thể"""
        try:
            # Load tất cả configs
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    all_configs = json.load(f)
            except:
                all_configs = {'guilds': {}}
            
            # Đảm bảo có structure guilds
            if 'guilds' not in all_configs:
                all_configs = {'guilds': {}}
            
            # Lưu config cho guild này
            all_configs['guilds'][str(guild_id)] = config
            
            # Lưu file
            self.save_all_configs(all_configs)
        except Exception as e:
            print(f"Lỗi khi lưu config: {e}")
    
    def save_all_configs(self, all_configs):
        """Lưu toàn bộ configs"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(all_configs, f, indent=2, ensure_ascii=False)
    
    def load_last_posts(self, guild_id=None):
        """Load danh sách ID bài viết đã đăng cho guild cụ thể"""
        try:
            with open(self.last_posts_path, 'r', encoding='utf-8') as f:
                all_posts = json.load(f)
            
            # Nếu là format cũ (không phân theo guild), migrate sang format mới
            if 'guilds' not in all_posts:
                # Migration: save format mới trực tiếp vào file
                new_format = {'guilds': {}}
                with open(self.last_posts_path, 'w', encoding='utf-8') as f:
                    json.dump(new_format, f, indent=2, ensure_ascii=False)
                all_posts = new_format
            
            # Trả về posts của guild cụ thể
            if guild_id:
                guild_key = str(guild_id)
                if guild_key not in all_posts['guilds']:
                    all_posts['guilds'][guild_key] = {
                        "messari": [],
                        "santiment": [],
                        "5phutcrypto": [],
                        "theblock": [],
                        "economic_events": [],
                        "rss": {}
                    }
                return all_posts['guilds'][guild_key]
            
            # Return default structure
            return {
                "messari": [],
                "santiment": [],
                "5phutcrypto": [],
                "theblock": [],
                "economic_events": [],
                "rss": {}
            }
        except:
            return {
                "messari": [],
                "santiment": [],
                "5phutcrypto": [],
                "theblock": [],
                "economic_events": [],
                "rss": {}
            }
    
    def save_last_posts(self, data, guild_id=None):
        """Lưu danh sách ID bài viết đã đăng cho guild cụ thể"""
        print(f"[DEBUG] save_last_posts called with guild_id={guild_id}")
        try:
            # Load tất cả posts
            try:
                with open(self.last_posts_path, 'r', encoding='utf-8') as f:
                    all_posts = json.load(f)
                print(f"[DEBUG] Loaded existing file, keys: {list(all_posts.keys())}")
                    
                # Migrate nếu chưa có guilds structure
                if 'guilds' not in all_posts:
                    print(f"[DEBUG] Migrating to new format!")
                    all_posts = {'guilds': {}}
                else:
                    print(f"[DEBUG] File already has guilds structure")
            except Exception as ex:
                print(f"[DEBUG] Failed to load file: {ex}, creating new")
                all_posts = {'guilds': {}}
            
            # Lưu posts cho guild này
            if guild_id:
                all_posts['guilds'][str(guild_id)] = data
                print(f"[DEBUG] Saved data for guild {guild_id}, total guilds: {len(all_posts['guilds'])}")
            
            # Lưu file
            with open(self.last_posts_path, 'w', encoding='utf-8') as f:
                json.dump(all_posts, f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] File saved successfully")
        except Exception as e:
            print(f"Lỗi khi lưu last_posts: {e}")
    
    async def translate_to_vietnamese(self, text, max_length=None):
        """Dịch text sang tiếng Việt"""
        if not text:
            return ""
        
        try:
            # Giới hạn độ dài nếu cần (Google Translate có giới hạn 5000 ký tự)
            if max_length and len(text) > max_length:
                text = text[:max_length]
            
            # deep-translator hỗ trợ tối đa 5000 ký tự
            if len(text) > 4500:
                text = text[:4500]
            
            # Dịch trong executor để không block
            loop = asyncio.get_event_loop()
            translated = await loop.run_in_executor(
                None, 
                self.translator.translate,
                text
            )
            return translated
        except Exception as e:
            print(f"Lỗi khi dịch text: {e}")
            return text  # Trả về text gốc nếu lỗi
    
    def _get_feed_icon(self, feed_url, feed_name):
        """Lấy icon URL cho RSS feed dựa trên nguồn"""
        # Sử dụng Google Favicon Service để lấy icon chất lượng cao
        try:
            from urllib.parse import urlparse
            
            # Map domain cho các nguồn tin chính
            domain_map = {
                'vnexpress': 'vnexpress.net',
                'bbc': 'bbc.com',
                'cnn': 'cnn.com',
                'reuters': 'reuters.com',
                'bloomberg': 'bloomberg.com',
                'techcrunch': 'techcrunch.com',
                'theverge': 'theverge.com',
                'cointelegraph': 'cointelegraph.com',
                'decrypt': 'decrypt.co',
            }
            
            # Tìm domain phù hợp
            domain = None
            for key, mapped_domain in domain_map.items():
                if key in feed_name.lower() or key in feed_url.lower():
                    domain = mapped_domain
                    break
            
            # Nếu không có trong map, extract từ URL
            if not domain:
                parsed = urlparse(feed_url)
                domain = parsed.netloc
            
            if domain:
                # Google Favicon Service với size 128x128 để hiển thị rõ
                return f'https://www.google.com/s2/favicons?domain={domain}&sz=128'
        except Exception as e:
            print(f"Lỗi khi lấy icon: {e}")
        
        # Default fallback icon
        return 'https://cdn-icons-png.flaticon.com/512/888/888846.png'
    
    async def fetch_glassnode_insights(self):
        """Lấy insights từ Glassnode RSS feed"""
        try:
            url = 'https://insights.glassnode.com/feed/'
            
            # Sử dụng feedparser trong executor để không block
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, url)
            
            if feed.entries:
                articles = []
                for entry in feed.entries[:5]:  # Lấy 5 tin mới nhất
                    article = {
                        'id': entry.get('link', entry.get('id', '')),
                        'title': entry.get('title', 'Không có tiêu đề'),
                        'url': entry.get('link', ''),
                        'description': entry.get('description', '') or entry.get('summary', ''),
                        'published_at': entry.get('published', ''),
                    }
                    articles.append(article)
                return articles
        except Exception as e:
            print(f"Lỗi khi lấy tin Glassnode: {e}")
        
        return []
    
    async def fetch_theblock_news(self):
        """Lấy tin tức từ The Block RSS feed"""
        try:
            url = 'https://www.theblock.co/rss.xml'
            
            # Sử dụng feedparser trong executor để không block
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, url)
            
            if feed.entries:
                articles = []
                for entry in feed.entries[:5]:  # Lấy 5 tin mới nhất
                    article = {
                        'id': entry.get('link', entry.get('id', '')),
                        'title': entry.get('title', 'Không có tiêu đề'),
                        'url': entry.get('link', ''),
                        'description': entry.get('description', '') or entry.get('summary', ''),
                        'published_at': entry.get('published', ''),
                    }
                    articles.append(article)
                return articles
        except Exception as e:
            print(f"Lỗi khi lấy tin The Block: {e}")
        
        return []
    
    async def fetch_5phutcrypto_news(self):
        """Scrape tin tức mới nhất từ 5phutcrypto.io"""
        try:
            async with aiohttp.ClientSession() as session:
                url = 'https://5phutcrypto.io/'
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        articles = []
                        
                        # Tìm tất cả các bài viết trong section "Tin tức"
                        # Tìm các thẻ <h3> có link bài viết
                        for h3 in soup.find_all('h3'):
                            link_tag = h3.find('a', href=True)
                            if link_tag and link_tag['href'].startswith('https://5phutcrypto.io/'):
                                # Bỏ qua các link đặc biệt
                                if any(skip in link_tag['href'] for skip in ['/tag/', '/author/', '/goc-nhin/', '/chuyen-sau/']):
                                    continue
                                
                                article = {
                                    'id': link_tag['href'],
                                    'title': link_tag.get_text(strip=True),
                                    'url': link_tag['href'],
                                    'published_at': datetime.now(VN_TZ).isoformat()  # UTC+7
                                }
                                
                                # Tìm ảnh thumbnail (thường ở gần h3)
                                parent = h3.find_parent()
                                if parent:
                                    img = parent.find('img')
                                    if img and 'data-src' in img.attrs:
                                        article['image_url'] = img['data-src']
                                    elif img and 'src' in img.attrs and not img['src'].startswith('data:'):
                                        article['image_url'] = img['src']
                                
                                articles.append(article)
                                
                                if len(articles) >= 5:
                                    break
                        
                        return articles[:5]
        except Exception as e:
            print(f"Lỗi khi scrape 5phutcrypto.io: {e}")
            import traceback
            traceback.print_exc()
        
        return []
    
    async def send_economic_event_update(self, channel, event, is_update=False):
        """Gửi thông báo chỉ số kinh tế với Forecast/Actual/Previous từ Investing.com"""
        try:
            # Lấy thông tin
            event_name = event.get('event', 'Unknown Event')
            country = event.get('country', 'N/A')
            impact = event.get('impact', 'Unknown')
            time_str = event.get('time', 'N/A')
            
            # Lấy 3 giá trị: Forecast, Actual, Previous
            forecast = event.get('forecast', 'N/A')
            actual = event.get('actual', 'N/A')
            previous = event.get('previous', 'N/A')
            
            # Xác định event status
            from datetime import datetime
            import pytz
            vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
            now = datetime.now(vietnam_tz)
            now_time = now.strftime('%H:%M')
            
            # Parse event time to compare
            try:
                event_time = time_str
                is_upcoming = event_time > now_time
            except:
                is_upcoming = True  # Default to upcoming if can't parse
            
            # Màu sắc theo impact
            color_map = {
                'High': 0xFF4444,      # Đỏ đậm
                'Medium': 0xFFA500,    # Cam
                'Low': 0x4CAF50        # Xanh lá
            }
            color = color_map.get(impact, 0x808080)
            
            # Icon theo impact
            icon_map = {
                'High': '🔴',
                'Medium': '🟠',
                'Low': '🟢'
            }
            icon = icon_map.get(impact, '⚪')
            
            # Title với status indicator
            if is_upcoming and actual == 'N/A':
                # Pre-event alert (chưa diễn ra)
                title = f"⏰ Sắp diễn ra: {event_name}"
                status_emoji = "🔔"
            elif actual != 'N/A':
                # Event đã có kết quả
                title = f"✅ Đã công bố: {event_name}"
                status_emoji = "📊"
            else:
                # Event đang diễn ra hoặc chưa có kết quả
                title = f"⏳ {event_name}"
                status_emoji = "⏰"
            
            # Tạo embed
            embed = discord.Embed(
                title=title,
                color=color,
                timestamp=datetime.now(VN_TZ)  # UTC+7
            )
            
            # Tạo field hiển thị đầy đủ 3 giá trị
            comparison_text = f"```diff\n"
            
            # Hiển thị Forecast
            if forecast != 'N/A':
                comparison_text += f"  📊 Forecast:  {forecast}\n"
            
            # Hiển thị Actual với màu (+ nếu tăng so với previous, - nếu giảm)
            if actual != 'N/A':
                try:
                    # Thử parse để so sánh
                    actual_num = float(str(actual).replace('%', '').replace('K', '').replace('M', '').replace('B', '').replace(',', '').strip()) if actual != 'N/A' else None
                    previous_num = float(str(previous).replace('%', '').replace('K', '').replace('M', '').replace('B', '').replace(',', '').strip()) if previous != 'N/A' else None
                    
                    if actual_num is not None and previous_num is not None:
                        if actual_num > previous_num:
                            comparison_text += f"+ 📈 Actual:    {actual}\n"
                        elif actual_num < previous_num:
                            comparison_text += f"- 📉 Actual:    {actual}\n"
                        else:
                            comparison_text += f"  📊 Actual:    {actual}\n"
                    else:
                        comparison_text += f"  📊 Actual:    {actual}\n"
                except:
                    comparison_text += f"  📊 Actual:    {actual}\n"
            else:
                # Chưa có actual - đây là pre-event alert
                comparison_text += f"  ⏳ Actual:    Chưa công bố\n"
            
            # Hiển thị Previous
            if previous != 'N/A':
                comparison_text += f"  📋 Previous:  {previous}\n"
            
            comparison_text += f"```"
            
            embed.add_field(
                name=f"{icon} **{impact} Impact Event**",
                value=comparison_text,
                inline=False
            )
            
            # Thông tin chi tiết
            info_text = f"⏰ **Time:** {time_str}\n"
            info_text += f"🌍 **Country:** {country}\n"
            
            # Thêm countdown nếu là upcoming event
            if is_upcoming and actual == 'N/A':
                info_text += f"\n{status_emoji} **Status:** Sắp diễn ra trong vài phút\n"
            elif actual != 'N/A':
                info_text += f"\n{status_emoji} **Status:** Đã công bố kết quả\n"
            
            embed.add_field(
                name="ℹ️ Details",
                value=info_text,
                inline=False
            )
            
            # Set author
            embed.set_author(
                name="Investing.com Economic Calendar",
                icon_url="https://www.google.com/s2/favicons?domain=investing.com&sz=128"
            )
            
            # Footer
            footer_text = "📊 Economic Calendar • Real-time Updates"
            embed.set_footer(
                text=footer_text,
                icon_url="https://www.google.com/s2/favicons?domain=stlouisfed.org&sz=128"
            )
            
            await channel.send(embed=embed)
            
        except Exception as e:
            print(f"Lỗi khi gửi economic event: {e}")
            import traceback
            traceback.print_exc()
    
    async def send_daily_summary(self, channel, events):
        """Gửi tổng quan lịch kinh tế hàng ngày (7:00 AM UTC+7)
        Chia thành 4 time blocks: Morning, Afternoon, Evening, Night với table format
        
        Args:
            channel: Discord channel to send to
            events: List of events from fetch_economic_calendar
        """
        try:
            vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
            now = datetime.now(vietnam_tz)
            
            # Filter Medium/High impact only
            filtered_events = [e for e in events if e.get('impact') in ['Medium', 'High']]
            
            if not filtered_events:
                await channel.send("📅 Không có sự kiện kinh tế quan trọng nào hôm nay.")
                return
            
            # Group events by time blocks
            time_blocks = {
                'morning': [],    # 07:00 - 11:59
                'afternoon': [],  # 12:00 - 17:59
                'evening': [],    # 18:00 - 23:59
                'night': []       # 00:00 - 04:30 (next day)
            }
            
            for event in filtered_events:
                time_str = event.get('time', '')
                try:
                    # Parse time to determine block
                    if '/' in time_str:
                        # Format: dd/mm HH:MM (next day event)
                        parsed = datetime.strptime(time_str, '%d/%m %H:%M')
                        hour = parsed.hour
                        # All next-day events go to night block
                        time_blocks['night'].append(event)
                    else:
                        # Format: HH:MM (today event)
                        parsed = datetime.strptime(time_str, '%H:%M')
                        hour = parsed.hour
                        
                        if 7 <= hour < 12:
                            time_blocks['morning'].append(event)
                        elif 12 <= hour < 18:
                            time_blocks['afternoon'].append(event)
                        elif 18 <= hour < 24:
                            time_blocks['evening'].append(event)
                        else:  # 0 <= hour < 7
                            time_blocks['night'].append(event)
                except:
                    # If parsing fails, put in morning by default
                    time_blocks['morning'].append(event)
            
            # Prepare block metadata
            block_info = {
                'morning': {'emoji': '🌅', 'title': 'BUỔI SÁNG (07:00 - 11:59)', 'color': 0xFFD700},
                'afternoon': {'emoji': '☀️', 'title': 'BUỔI CHIỀU (12:00 - 17:59)', 'color': 0xFF8C00},
                'evening': {'emoji': '🌙', 'title': 'BUỔI TỐI (18:00 - 23:59)', 'color': 0x4169E1},
                'night': {'emoji': '🌃', 'title': 'ĐÊM/SÁNG SỚM (00:00 - 04:30)', 'color': 0x483D8B}
            }
            
            # Send intro message - clean and professional
            intro_embed = discord.Embed(
                title="📅 LỊCH KINH TẾ HÔM NAY",
                description="",
                color=0x2ECC71,  # Green color
                timestamp=now
            )
            
            # Add info fields
            intro_embed.add_field(
                name="📆 Ngày",
                value=f"`{now.strftime('%d/%m/%Y')}`",
                inline=True
            )
            
            intro_embed.add_field(
                name="⏰ Cập nhật lúc",
                value=f"`{now.strftime('%H:%M')} UTC+7`",
                inline=True
            )
            
            intro_embed.add_field(
                name="📊 Tổng số sự kiện",
                value=f"`{len(filtered_events)} events`",
                inline=True
            )
            
            # Count by impact
            high_total = len([e for e in filtered_events if e.get('impact') == 'High'])
            med_total = len([e for e in filtered_events if e.get('impact') == 'Medium'])
            
            intro_embed.add_field(
                name="� Phân loại Impact",
                value=f"🔴 **High:** {high_total} events\n🟠 **Medium:** {med_total} events",
                inline=False
            )
            
            intro_embed.add_field(
                name="🔔 Lưu ý",
                value="Bot sẽ tự động đăng kết quả actual khi có công bố chính thức từ Investing.com",
                inline=False
            )
            
            intro_embed.set_footer(
                text="📊 Investing.com Economic Calendar • Tự động cập nhật",
                icon_url="https://www.google.com/s2/favicons?domain=investing.com&sz=128"
            )
            
            await channel.send(embed=intro_embed)
            
            # Send each time block
            for block_key in ['morning', 'afternoon', 'evening', 'night']:
                block_events = time_blocks[block_key]
                if not block_events:
                    continue
                
                info = block_info[block_key]
                
                # Count by impact
                high_count = len([e for e in block_events if e.get('impact') == 'High'])
                med_count = len([e for e in block_events if e.get('impact') == 'Medium'])
                
                # Create embed for this block
                embed = discord.Embed(
                    title=f"{info['emoji']} {info['title']}",
                    description=f"**Tổng: {len(block_events)} sự kiện** (🔴 {high_count} High, 🟠 {med_count} Medium)\n",
                    color=info['color']
                )
                
                # Add each event as a field (max 25 fields per embed)
                for evt in block_events[:25]:  # Discord limit: 25 fields
                    time_display = evt.get('time', 'N/A')
                    country = evt.get('country', 'N/A')
                    event_name = evt.get('event', 'Unknown')
                    impact = evt.get('impact', 'Low')
                    
                    # Impact icon
                    if impact == 'High':
                        impact_icon = '🔴'
                    elif impact == 'Medium':
                        impact_icon = '🟠'
                    else:
                        impact_icon = '🟢'
                    
                    # Get flag emoji for country
                    country_flags = {
                        'United States': '🇺🇸',
                        'Euro Zone': '🇪🇺',
                        'Germany': '🇩🇪',
                        'United Kingdom': '🇬🇧',
                        'Japan': '🇯🇵',
                        'China': '🇨🇳',
                        'Canada': '🇨🇦',
                        'Australia': '🇦🇺',
                        'Switzerland': '🇨🇭',
                        'France': '🇫🇷',
                        'Italy': '🇮🇹',
                        'Spain': '🇪🇸',
                    }
                    flag = country_flags.get(country, '🌍')
                    
                    # Truncate long event names
                    if len(event_name) > 45:
                        event_name = event_name[:42] + "..."
                    
                    # Field name: Time + Impact
                    field_name = f"{impact_icon} **{time_display}** | {flag} {country}"
                    
                    # Field value: Event name
                    field_value = f"{event_name}"
                    
                    embed.add_field(
                        name=field_name,
                        value=field_value,
                        inline=False
                    )
                
                embed.set_footer(
                    text=f"📊 {info['emoji']} {len(block_events)} events",
                    icon_url="https://www.google.com/s2/favicons?domain=investing.com&sz=128"
                )
                
                await channel.send(embed=embed)
                await asyncio.sleep(0.5)  # Small delay between embeds
            
            print(f"✅ Sent daily summary: {len(filtered_events)} events across {sum(1 for v in time_blocks.values() if v)} time blocks")
            
        except Exception as e:
            print(f"❌ Error sending daily summary: {e}")
            import traceback
            traceback.print_exc()
    
    async def fetch_economic_calendar(self, target_time=None):
        """Lấy dữ liệu kinh tế từ Investing.com (có đầy đủ Forecast/Actual/Previous)
        
        Args:
            target_time: Nếu None, lấy TẤT CẢ events từ now → 4:30 AM ngày hôm sau
                        Nếu có giá trị (datetime), chỉ lấy events trong khoảng ±5 phút của target_time
        """
        try:
            from bs4 import BeautifulSoup
            import aiohttp
            
            # Get today's and tomorrow's date in UTC+7
            vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
            today = datetime.now(vietnam_tz)
            tomorrow = today + timedelta(days=1)
            
            # Fetch both today and tomorrow to cover events until 4:30 AM next day
            date_str_today = today.strftime('%Y-%m-%d')
            date_str_tomorrow = tomorrow.strftime('%Y-%m-%d')
            
            # Use date filter to get events from both days
            url = f"https://www.investing.com/economic-calendar/?dateFrom={date_str_today}&dateTo={date_str_tomorrow}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            economic_updates = []
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find all event rows
                        rows = soup.find_all('tr', {'class': 'js-event-item'})
                        print(f"📊 Found {len(rows)} economic events from Investing.com")
                        
                        # Get current datetime in UTC+7
                        vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
                        now_vn = datetime.now(vietnam_tz)
                        today_vn = now_vn.date()
                        print(f"📅 Now in UTC+7: {now_vn.strftime('%Y-%m-%d %H:%M')}")
                        
                        for row in rows[:150]:  # Tăng lên 150 để đảm bảo đủ events
                            try:
                                # Get event datetime from data attribute
                                event_datetime_str = row.get('data-event-datetime', '')
                                
                                if not event_datetime_str:
                                    continue
                                
                                # Parse datetime (format: "2025/11/06 10:00:00" in UTC-5)
                                try:
                                    # Parse as UTC-5 (naive datetime)
                                    event_dt_utc5 = datetime.strptime(event_datetime_str, '%Y/%m/%d %H:%M:%S')
                                    
                                    # Convert to UTC+7 (add 12 hours) and make it timezone-aware
                                    event_dt_vn_naive = event_dt_utc5 + timedelta(hours=12)
                                    event_dt_vn = vietnam_tz.localize(event_dt_vn_naive)
                                    
                                    # Determine filter behavior based on target_time
                                    if target_time:
                                        # Targeted fetch: Only get events within ±5 min of target_time (for actual checks)
                                        time_diff = abs((event_dt_vn - target_time).total_seconds())
                                        if time_diff > 300:  # 5 minutes = 300 seconds
                                            continue
                                    else:
                                        # Daily summary fetch: Get all events from now until 4:30 AM next day
                                        now_vn = datetime.now(vietnam_tz)
                                        
                                        # Calculate end time: 4:30 AM next day
                                        next_day = now_vn + timedelta(days=1)
                                        end_time = vietnam_tz.localize(datetime(next_day.year, next_day.month, next_day.day, 4, 30))
                                        
                                        # Skip events that already passed or are beyond 4:30 AM tomorrow
                                        if event_dt_vn < now_vn or event_dt_vn > end_time:
                                            continue
                                    
                                    # Format time for display
                                    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
                                    now_vn = datetime.now(vietnam_tz)
                                    today_vn = now_vn.date()
                                    
                                    if event_dt_vn.date() == today_vn:
                                        time_str = event_dt_vn.strftime('%H:%M')
                                    else:
                                        # Include date if event is tomorrow or later
                                        time_str = event_dt_vn.strftime('%d/%m %H:%M')
                                    
                                except Exception as e:
                                    print(f"Error parsing datetime {event_datetime_str}: {e}")
                                    continue
                                
                                # Get country
                                country_elem = row.find('td', {'class': 'flagCur'})
                                if country_elem:
                                    country_span = country_elem.find('span', {'class': 'ceFlags'})
                                    country = country_span.get('title', '') if country_span else ''
                                else:
                                    country = ''
                                
                                # Không filter theo country nữa - lấy tất cả các quốc gia
                                # Filter for major economies only
                                # major_countries = ['United States', 'Euro Zone', 'Germany', 'United Kingdom', 'Japan', 'China']
                                # if country not in major_countries:
                                #     continue
                                
                                # Get impact - DÙNG data-img_key thay vì class
                                impact_elem = row.find('td', {'class': 'sentiment'})
                                if impact_elem:
                                    img_key = impact_elem.get('data-img_key', '')
                                    if img_key == 'bull3':
                                        impact = 'High'
                                    elif img_key == 'bull2':
                                        impact = 'Medium'
                                    else:  # bull1 or empty
                                        impact = 'Low'
                                else:
                                    impact = 'Low'
                                
                                # Get event name
                                event_elem = row.find('td', {'class': 'event'})
                                event_name = event_elem.text.strip() if event_elem else ''
                                
                                if not event_name:
                                    continue
                                
                                # Get Actual value
                                actual_elem = row.find('td', {'class': 'act'})
                                actual_str = actual_elem.text.strip() if actual_elem else ''
                                
                                # Get Forecast value
                                forecast_elem = row.find('td', {'class': 'fore'})
                                forecast_str = forecast_elem.text.strip() if forecast_elem else ''
                                
                                # Get Previous value
                                previous_elem = row.find('td', {'class': 'prev'})
                                previous_str = previous_elem.text.strip() if previous_elem else ''
                                
                                # Không skip nữa - lấy tất cả events kể cả không có forecast/previous
                                # Skip if no forecast AND no previous (nhưng có thể có actual)
                                # if not forecast_str and not previous_str:
                                #     continue
                                
                                # Create event ID
                                event_id = f"investing_{country.replace(' ', '_')}_{event_name.replace(' ', '_')[:30]}_{time_str}"
                                
                                event = {
                                    'id': event_id,
                                    'event': event_name,
                                    'country': country,
                                    'impact': impact,
                                    'time': time_str,
                                    'actual': actual_str if actual_str else 'N/A',
                                    'forecast': forecast_str if forecast_str else 'N/A',
                                    'previous': previous_str if previous_str else 'N/A',
                                    'datetime': datetime.now(VN_TZ)  # UTC+7
                                }
                                
                                economic_updates.append(event)
                                
                            except Exception as e:
                                print(f"Lỗi khi parse event: {e}")
                                continue
                        
                        print(f"✅ Scraped {len(economic_updates)} relevant economic events")
            
            return economic_updates
            
        except Exception as e:
            print(f"Lỗi khi lấy economic calendar: {e}")
            import traceback
            traceback.print_exc()
        
        return []
    
    async def fetch_santiment_news(self):
        """Lấy insights từ Santiment API"""
        api_key = os.getenv('SANTIMENT_API_KEY')
        if not api_key:
            return []
        
        try:
            # GraphQL query cho Santiment - sử dụng allInsights
            query = """
            {
              allInsights(
                page: 1
                pageSize: 5
              ) {
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
                    'Authorization': f'Apikey {api_key}'
                }
                url = 'https://api.santiment.net/graphql'
                
                async with session.post(url, json={'query': query}, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'errors' in data:
                            print(f"Santiment GraphQL errors: {data['errors']}")
                            return []
                        
                        insights = data.get('data', {}).get('allInsights', [])
                        
                        # Chỉ lấy insights đã published
                        published_insights = [
                            insight for insight in insights 
                            if insight.get('readyState') == 'published'
                        ]
                        
                        return published_insights
        except Exception as e:
            print(f"Lỗi khi lấy tin Santiment: {e}")
        
        return []
    
    async def fetch_rss_feed(self, url):
        """Lấy tin từ RSS Feed"""
        try:
            # Sử dụng feedparser trong executor để không block
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, url)
            
            if feed.entries:
                return feed.entries[:5]  # Lấy 5 tin mới nhất
        except Exception as e:
            print(f"Lỗi khi lấy RSS từ {url}: {e}")
        
        return []
    
    @tasks.loop(minutes=3)
    async def news_checker(self):
        """Background task kiểm tra tin tức mới mỗi 5 phút"""
        print(f"🔥 NEWS_CHECKER STARTED at {datetime.now(VN_TZ)}")
        print(f"🔥 Found {len(self.bot.guilds)} guilds to process")
        
        # Lặp qua tất cả guilds
        for guild in self.bot.guilds:
            print(f"🔥 Processing guild: {guild.name} (ID: {guild.id})")
            try:
                config = self.load_news_config(guild.id)
                last_posts = self.load_last_posts(guild.id)  # ← Load theo guild
                
                # Kiểm tra Glassnode Insights (thay thế Messari)
                if config['messari_channel']:  # Dùng lại key này cho Glassnode
                    channel = self.bot.get_channel(config['messari_channel'])
                    if channel:
                        articles = await self.fetch_glassnode_insights()
                        
                        if not articles:
                            print(f"⚠️ Glassnode không trả về dữ liệu")
                        
                        for article in articles:
                            article_id = article.get('id')
                            if article_id not in last_posts['messari']:  # Dùng lại key này
                                # Lấy nội dung gốc
                                original_title = article.get('title', 'Không có tiêu đề')
                                original_description = article.get('description', '')
                                
                                # Strip HTML tags từ description
                                soup = BeautifulSoup(original_description, 'html.parser')
                                clean_description = soup.get_text()[:400]
                                
                                # Dịch sang tiếng Việt
                                translated_title = await self.translate_to_vietnamese(original_title, 250)
                                translated_description = await self.translate_to_vietnamese(clean_description, 400) if clean_description else ""
                                
                                # Đăng tin mới với thiết kế đẹp - chỉ bản dịch
                                # Use a clear emoji instead of a replacement character
                                embed = discord.Embed(
                                    title=f"📊 {translated_title}",
                                    url=article.get('url', ''),
                                    description=translated_description,
                                    color=0x5B8DEE,  # Xanh dương Glassnode
                                    timestamp=datetime.now(VN_TZ)
                                )
                                
                                # Thêm author info với Google Favicon
                                embed.set_author(
                                    name="Glassnode Insights",
                                    icon_url="https://www.google.com/s2/favicons?domain=glassnode.com&sz=128"
                                )
                                
                                # Footer với icon
                                embed.set_footer(
                                    text="📈 Nguồn: Glassnode • On-chain Analytics • Đã dịch tự động",
                                    icon_url="https://www.google.com/s2/favicons?domain=glassnode.com&sz=128"
                                )
                                
                                await channel.send(embed=embed)
                                
                                # Lưu ID
                                last_posts['messari'].append(article_id)
                                # Giữ tối đa 100 IDs
                                if len(last_posts['messari']) > 100:
                                    last_posts['messari'] = last_posts['messari'][-100:]
                
                # Kiểm tra Santiment
                if config['santiment_channel']:
                    channel = self.bot.get_channel(config['santiment_channel'])
                    if channel:
                        insights = await self.fetch_santiment_news()
                        for insight in insights:
                            insight_id = str(insight.get('id'))
                            if insight_id not in last_posts['santiment']:
                                # Lấy nội dung gốc
                                original_title = insight.get('title', 'Không có tiêu đề')
                                
                                # Lấy text và strip HTML tags
                                original_text = insight.get('text', '')
                                # Remove HTML tags cơ bản
                                soup = BeautifulSoup(original_text, 'html.parser')
                                clean_text = soup.get_text()[:400]
                                
                                # Dịch sang tiếng Việt
                                translated_title = await self.translate_to_vietnamese(original_title, 250)
                                translated_text = await self.translate_to_vietnamese(clean_text, 400) if clean_text else "Đọc thêm tại Santiment"
                                
                                # Tạo URL đến insight
                                insight_url = f"https://insights.santiment.net/read/{insight_id}"
                                
                                # Thông tin tác giả
                                author_name = insight.get('user', {}).get('username', 'Santiment')
                                
                                # Đăng tin mới - chỉ bản dịch
                                embed = discord.Embed(
                                    title=f"📊 {translated_title}",
                                    url=insight_url,
                                    description=translated_text,
                                    color=0x26A69A,  # Xanh lá ngọc lam
                                    timestamp=datetime.fromisoformat(insight.get('publishedAt', '').replace('Z', '+00:00'))
                                )
                                
                                # Set author với Google Favicon
                                embed.set_author(
                                    name=f"Santiment Insights • {author_name}",
                                    icon_url="https://www.google.com/s2/favicons?domain=santiment.net&sz=128"
                                )
                                
                                # Footer với icon
                                embed.set_footer(
                                    text="📈 Nguồn: Santiment • Market Intelligence • Đã dịch tự động",
                                    icon_url="https://www.google.com/s2/favicons?domain=santiment.net&sz=128"
                                )
                                
                                await channel.send(embed=embed)
                                
                                # Lưu ID
                                last_posts['santiment'].append(insight_id)
                                if len(last_posts['santiment']) > 100:
                                    last_posts['santiment'] = last_posts['santiment'][-100:]
                
                # Kiểm tra 5 Phút Crypto
                if config.get('5phutcrypto_channel'):
                    channel = self.bot.get_channel(config['5phutcrypto_channel'])
                    if channel:
                        news = await self.fetch_5phutcrypto_news()
                        for article in news:
                            article_id = article.get('id')
                            if article_id not in last_posts['5phutcrypto']:
                                # Lấy tiêu đề (đã là tiếng Việt)
                                title = article.get('title', 'Không có tiêu đề')
                                
                                # Đăng tin mới
                                embed = discord.Embed(
                                    title=f"💰 {title}",
                                    url=article.get('url', ''),
                                    description="",  # 5phutcrypto không có description ngắn
                                    color=0xFF6B00,  # Cam của 5phutcrypto
                                    timestamp=datetime.fromisoformat(article.get('published_at', ''))
                                )
                                
                                # Set author với icon
                                embed.set_author(
                                    name="5 Phút Crypto",
                                    icon_url="https://www.google.com/s2/favicons?domain=5phutcrypto.io&sz=128"
                                )
                                
                                # Thêm ảnh nếu có
                                if article.get('image_url'):
                                    embed.set_image(url=article.get('image_url'))
                                
                                # Footer với icon
                                embed.set_footer(
                                    text="💰 Nguồn: 5 Phút Crypto • Tin tức & phân tích",
                                    icon_url="https://www.google.com/s2/favicons?domain=5phutcrypto.io&sz=128"
                                )
                                
                                await channel.send(embed=embed)
                                
                                # Lưu ID
                                last_posts['5phutcrypto'].append(article_id)
                                if len(last_posts['5phutcrypto']) > 100:
                                    last_posts['5phutcrypto'] = last_posts['5phutcrypto'][-100:]
                
                # Kiểm tra The Block
                if config.get('theblock_channel'):
                    channel = self.bot.get_channel(config['theblock_channel'])
                    if channel:
                        articles = await self.fetch_theblock_news()
                        
                        if not articles:
                            print(f"⚠️ The Block không trả về dữ liệu")
                        
                        for article in articles:
                            article_id = article.get('id')
                            if article_id not in last_posts['theblock']:
                                # Lấy nội dung gốc
                                original_title = article.get('title', 'Không có tiêu đề')
                                original_description = article.get('description', '')
                                
                                # Strip HTML tags từ description
                                soup = BeautifulSoup(original_description, 'html.parser')
                                clean_description = soup.get_text()[:400]
                                
                                # Dịch sang tiếng Việt
                                translated_title = await self.translate_to_vietnamese(original_title, 250)
                                translated_description = await self.translate_to_vietnamese(clean_description, 400) if clean_description else ""
                                
                                # Đăng tin mới với thiết kế đẹp - chỉ bản dịch
                                embed = discord.Embed(
                                    title=f"📰 {translated_title}",
                                    url=article.get('url', ''),
                                    description=translated_description,
                                    color=0x1E1E1E,  # Màu đen The Block
                                    timestamp=datetime.now(VN_TZ)
                                )
                                
                                # Thêm author info với Google Favicon
                                embed.set_author(
                                    name="The Block",
                                    icon_url="https://www.google.com/s2/favicons?domain=theblock.co&sz=128"
                                )
                                
                                # Footer với icon
                                embed.set_footer(
                                    text="📰 Nguồn: The Block • Institutional-grade Crypto News • Đã dịch tự động",
                                    icon_url="https://www.google.com/s2/favicons?domain=theblock.co&sz=128"
                                )
                                
                                await channel.send(embed=embed)
                                
                                # Lưu ID
                                last_posts['theblock'].append(article_id)
                                # Giữ tối đa 100 IDs
                                if len(last_posts['theblock']) > 100:
                                    last_posts['theblock'] = last_posts['theblock'][-100:]
                
                # Kiểm tra Economic Calendar (polling mỗi 3 phút)
                if config.get('economic_calendar_channel'):
                    channel = self.bot.get_channel(config['economic_calendar_channel'])
                    if channel:
                        events = await self.fetch_economic_calendar()
                        for event in events:
                            event_id = event.get('id')
                            
                            # Chỉ post Medium và High impact
                            # Chỉ post nếu có actual value (chưa post trước đó)
                            actual = event.get('actual', 'N/A')
                            if event.get('impact') in ['Medium', 'High'] and actual and actual != 'N/A':
                                if event_id not in last_posts['economic_events']:
                                    await self.send_economic_event_update(channel, event, is_update=False)
                                    
                                    # Lưu ID
                                    last_posts['economic_events'].append(event_id)
                                    # Giữ tối đa 200 IDs
                                    if len(last_posts['economic_events']) > 200:
                                        last_posts['economic_events'] = last_posts['economic_events'][-200:]
                
                # Kiểm tra RSS Feeds
                for feed_config in config['rss_feeds']:
                    channel = self.bot.get_channel(feed_config['channel_id'])
                    if channel:
                        feed_url = feed_config['url']
                        feed_name = feed_config['name']
                        
                        # Khởi tạo list cho feed này nếu chưa có
                        if feed_url not in last_posts['rss']:
                            last_posts['rss'][feed_url] = []
                        
                        entries = await self.fetch_rss_feed(feed_url)
                        for entry in entries:
                            try:
                                entry_id = entry.get('id', entry.get('link', ''))
                                
                                if entry_id not in last_posts['rss'][feed_url]:
                                    # Chọn màu dựa trên nguồn
                                    color_map = {
                                        'vnexpress': 0xC81E1E,  # Đỏ VNExpress
                                        'bbc': 0xBB1919,         # Đỏ BBC
                                        'cnn': 0xCC0000,         # Đỏ CNN
                                        'reuters': 0xFF6600,     # Cam Reuters
                                        'bloomberg': 0x000000,   # Đen Bloomberg
                                    }
                                    
                                    # Tìm màu phù hợp với feed
                                    color = 0xFFA500  # Cam mặc định
                                    for key, col in color_map.items():
                                        if key in feed_name.lower() or key in feed_url.lower():
                                            color = col
                                            break
                                    
                                    # Lấy title và description gốc
                                    original_title = entry.get('title', 'Không có tiêu đề')
                                    # Decode HTML entities (&#244; -> ô, &#225; -> á, etc.)
                                    # VNEconomy có lỗi format: #225; thay vì &#225; nên phải fix
                                    original_title = re.sub(r'#(\d+);', r'&#\1;', original_title)
                                    original_title = html.unescape(original_title)
                                    if len(original_title) > 250:
                                        original_title = original_title[:247] + '...'
                                    
                                    # Mô tả với định dạng đẹp - loại bỏ HTML tags
                                    original_description = entry.get('summary', entry.get('description', ''))
                                    if original_description:
                                        # Fix VNEconomy format error: #225; -> &#225;
                                        original_description = re.sub(r'#(\d+);', r'&#\1;', original_description)
                                        # Decode HTML entities
                                        original_description = html.unescape(original_description)
                                        # Loại bỏ tất cả HTML tags bằng regex
                                        original_description = re.sub(r'<[^>]+>', '', original_description)
                                        # Xóa nhiều khoảng trắng liên tiếp
                                        original_description = re.sub(r'\s+', ' ', original_description)
                                        # Trim
                                        original_description = original_description.strip()
                                        # Giới hạn độ dài
                                        if len(original_description) > 350:
                                            original_description = original_description[:347] + '...'
                                    
                                    # Kiểm tra xem có phải tiếng Việt không (VNExpress không cần dịch)
                                    is_vietnamese = 'vnexpress' in feed_url.lower() or 'vn' in feed_name.lower()
                                    
                                    if is_vietnamese:
                                        # Không dịch, chỉ hiển thị tiếng Việt
                                        translated_title = original_title
                                        description_text = original_description if original_description else "Không có mô tả"
                                    else:
                                        # Dịch sang tiếng Việt
                                        translated_title = await self.translate_to_vietnamese(original_title, 250)
                                        
                                        if original_description:
                                            translated_description = await self.translate_to_vietnamese(original_description, 350)
                                            description_text = translated_description
                                        else:
                                            description_text = "Không có mô tả"
                                    
                                    # Tạo embed đẹp - chỉ bản dịch
                                    embed = discord.Embed(
                                        title=f"🌍 {translated_title}",
                                        url=entry.get('link', ''),
                                        description=description_text,
                                        color=color
                                    )
                                    
                                    # Thêm published date nếu có
                                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                        try:
                                            dt = datetime(*entry.published_parsed[:6])
                                            embed.timestamp = dt
                                        except Exception as e:
                                            print(f"Lỗi parse timestamp: {e}")
                                    
                                    # Thêm thumbnail/image từ RSS nếu có - xử lý an toàn
                                    image_url = None
                                    
                                    # Thử media_content trước
                                    if hasattr(entry, 'media_content') and entry.media_content:
                                        try:
                                            if len(entry.media_content) > 0 and 'url' in entry.media_content[0]:
                                                image_url = entry.media_content[0]['url']
                                        except Exception as e:
                                            print(f"Lỗi media_content: {e}")
                                    
                                    # Thử media_thumbnail
                                    if not image_url and hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                                        try:
                                            if len(entry.media_thumbnail) > 0 and 'url' in entry.media_thumbnail[0]:
                                                image_url = entry.media_thumbnail[0]['url']
                                        except Exception as e:
                                            print(f"Lỗi media_thumbnail: {e}")
                                    
                                    # Thử enclosures (VNExpress dùng cái này)
                                    if not image_url and hasattr(entry, 'enclosures') and entry.enclosures:
                                        try:
                                            for enclosure in entry.enclosures:
                                                enc_type = enclosure.get('type', '')
                                                enc_href = enclosure.get('href', '')
                                                if 'image' in enc_type.lower() and enc_href:
                                                    image_url = enc_href
                                                    break
                                        except Exception as e:
                                            print(f"Lỗi enclosures: {e}")
                                    
                                    # Set image nếu tìm thấy
                                    if image_url:
                                        try:
                                            embed.set_image(url=image_url)
                                        except Exception as e:
                                            print(f"Lỗi set_image với URL {image_url}: {e}")
                                    
                                    # Set author với icon
                                    try:
                                        embed.set_author(
                                            name=feed_name,
                                            icon_url=self._get_feed_icon(feed_url, feed_name)
                                        )
                                    except Exception as e:
                                        print(f"Lỗi set_author: {e}")
                                    
                                    # Footer đẹp với emoji
                                    try:
                                        footer_text = f"📡 Nguồn: {feed_name} • RSS Feed"
                                        if not is_vietnamese:
                                            footer_text += " • Đã dịch tự động"
                                        
                                        embed.set_footer(
                                            text=footer_text,
                                            icon_url=self._get_feed_icon(feed_url, feed_name)
                                        )
                                    except Exception as e:
                                        print(f"Lỗi set_footer: {e}")
                                    
                                    # Gửi embed
                                    await channel.send(embed=embed)
                                    
                                    # Lưu ID
                                    last_posts['rss'][feed_url].append(entry_id)
                                    if len(last_posts['rss'][feed_url]) > 100:
                                        last_posts['rss'][feed_url] = last_posts['rss'][feed_url][-100:]
                            
                            except Exception as e:
                                print(f"Lỗi khi xử lý RSS entry từ {feed_name}: {e}")
                                import traceback
                                traceback.print_exc()
                                continue
            
            except Exception as e:
                print(f"Lỗi khi xử lý tin tức cho guild {guild.id}: {e}")
                import traceback
                traceback.print_exc()
                continue
            
            # Lưu last_posts cho guild này
            print(f"🔹 DEBUG: About to save for guild {guild.id}, last_posts has {len(last_posts.get('messari', []))} messari")
            self.save_last_posts(last_posts, guild.id)
            print(f"🔹 DEBUG: Saved completed for guild {guild.id}")
    
    @news_checker.before_loop
    async def before_news_checker(self):
        """Đợi bot sẵn sàng trước khi chạy task"""
        await self.bot.wait_until_ready()
    
    @tasks.loop(hours=1)
    async def daily_calendar_summary(self):
        """Gửi lịch Economic Calendar vào 7h sáng UTC+7 mỗi ngày"""
        # Lấy giờ hiện tại theo UTC+7
        vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(vietnam_tz)
        
        # Chỉ chạy vào 7h sáng
        if now.hour != 7:
            return
        
        # Lặp qua tất cả guilds
        for guild in self.bot.guilds:
            try:
                config = self.load_news_config(guild.id)
                
                # Kiểm tra có channel Economic Calendar không
                if config['economic_calendar_channel']:
                    channel = self.bot.get_channel(config['economic_calendar_channel'])
                    if channel:
                        # Fetch economic calendar
                        events = await self.fetch_economic_calendar()
                        
                        if events:
                            # Tạo embed tổng hợp lịch trong ngày
                            embed = discord.Embed(
                                title="📅 Economic Calendar - Lịch Kinh Tế Hôm Nay",
                                description=f"Các sự kiện kinh tế quan trọng trong ngày {now.strftime('%d/%m/%Y')}",
                                color=0x3498DB,
                                timestamp=now  # Đã là UTC+7 từ biến now
                            )
                            
                            # Phân loại theo impact - CHỈ LẤY MEDIUM VÀ HIGH
                            high_impact = [e for e in events if e['impact'] == 'High']
                            medium_impact = [e for e in events if e['impact'] == 'Medium']
                            low_impact = [e for e in events if e['impact'] == 'Low']
                            
                            print(f"📊 DEBUG Impact: High={len(high_impact)}, Medium={len(medium_impact)}, Low={len(low_impact)}")
                            
                            # Debug: In ra 3 events đầu để xem impact
                            for i, e in enumerate(events[:3]):
                                print(f"  Event {i+1}: {e.get('event', 'N/A')} - Impact: {e.get('impact', 'N/A')}")
                            
                            # Thêm High Impact events
                            if high_impact:
                                high_text = ""
                                for event in high_impact[:15]:  # Tối đa 15 events
                                    time = event.get('time', 'TBA')
                                    name = event.get('event', 'Unknown')
                                    country = event.get('country', 'N/A')
                                    # Rút gọn tên nếu quá dài để tránh vượt quá 1024 ký tự
                                    if len(name) > 60:
                                        name = name[:57] + "..."
                                    high_text += f"🔴 **{time}** - {name} ({country})\n"
                                
                                # Cắt nếu vượt quá giới hạn Discord (1024 chars per field)
                                if len(high_text) > 1020:
                                    high_text = high_text[:1020] + "..."
                                
                                embed.add_field(
                                    name="🔴 High Impact Events",
                                    value=high_text if high_text else "Không có",
                                    inline=False
                                )
                            
                            # Thêm Medium Impact events
                            if medium_impact:
                                medium_text = ""
                                for event in medium_impact[:15]:  # Tối đa 15 events
                                    time = event.get('time', 'TBA')
                                    name = event.get('event', 'Unknown')
                                    country = event.get('country', 'N/A')
                                    if len(name) > 60:
                                        name = name[:57] + "..."
                                    medium_text += f"🟠 **{time}** - {name} ({country})\n"
                                
                                if len(medium_text) > 1020:
                                    medium_text = medium_text[:1020] + "..."
                                
                                embed.add_field(
                                    name="🟠 Medium Impact Events",
                                    value=medium_text if medium_text else "Không có",
                                    inline=False
                                )
                            
                            # Set author
                            embed.set_author(
                                name="Investing.com Economic Calendar",
                                icon_url="https://www.google.com/s2/favicons?domain=investing.com&sz=128"
                            )
                            
                            # Footer
                            embed.set_footer(
                                text=f"📊 Tổng: {len(events)} sự kiện • Cập nhật lúc {now.strftime('%H:%M')} (UTC+7)",
                                icon_url="https://www.google.com/s2/favicons?domain=investing.com&sz=128"
                            )
                            
                            await channel.send(embed=embed)
                            print(f"✅ Đã gửi lịch Economic Calendar cho guild {guild.name}")
                        else:
                            print(f"⚠️ Không có events cho guild {guild.name}")
                            
            except Exception as e:
                print(f"Lỗi khi gửi daily calendar cho guild {guild.id}: {e}")
                import traceback
                traceback.print_exc()
    
    @daily_calendar_summary.before_loop
    async def before_daily_calendar_summary(self):
        """Đợi bot sẵn sàng trước khi chạy task"""
        await self.bot.wait_until_ready()
    
    # ==================== ECONOMIC CALENDAR DYNAMIC SCHEDULER ====================
    
    @tasks.loop(hours=24)
    async def economic_calendar_scheduler(self):
        """
        Chạy mỗi ngày lúc 07:00 UTC+7 để:
        1. Gửi daily summary (lịch trình events từ 7:00 → 4:30 sáng hôm sau)
        2. Schedule event checks cho mỗi event
        """
        try:
            VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
            now = datetime.now(VN_TZ)
            print(f"� Economic Calendar Scheduler running at {now.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Cancel all existing scheduled tasks
            for task in self.event_tasks:
                if not task.done():
                    task.cancel()
            self.event_tasks.clear()
            
            # Reset tracking
            self.scheduled_events.clear()
            
            # Fetch all events from now until 4:30 AM tomorrow
            events = await self.fetch_economic_calendar(target_time=None)
            
            if not events:
                print("⚠️ No economic events found")
                return
            
            print(f"📊 Fetched {len(events)} events for today")
            
            # Filter Medium/High impact
            important_events = [e for e in events if e.get('impact') in ['Medium', 'High']]
            print(f"✅ {len(important_events)} Medium/High impact events to schedule")
            
            # Step 1: Send daily summary to all configured guilds
            for guild in self.bot.guilds:
                config = self.load_news_config(guild.id)
                
                if config and config.get('economic_calendar_channel'):
                    channel = self.bot.get_channel(config['economic_calendar_channel'])
                    
                    if channel:
                        await self.send_daily_summary(channel, events)
                        print(f"📬 Sent daily summary to {guild.name}")
            
            # Step 2: Schedule event checks for each important event
            for event in important_events:
                event_id = event.get('id')
                event_time_str = event.get('time', '')
                event_name = event.get('event', 'Unknown')
                
                if not event_time_str or event_time_str in ('All Day', 'Tentative'):
                    continue
                
                try:
                    # Parse event time to datetime
                    if '/' in event_time_str:
                        # Format: dd/mm HH:MM (next day)
                        dt = datetime.strptime(event_time_str, '%d/%m %H:%M')
                        event_time_naive = datetime(year=now.year, month=dt.month, day=dt.day, hour=dt.hour, minute=dt.minute)
                    else:
                        # Format: HH:MM (today)
                        parsed = datetime.strptime(event_time_str, '%H:%M')
                        event_time_naive = datetime(year=now.year, month=now.month, day=now.day, hour=parsed.hour, minute=parsed.minute)
                    
                    # Localize to Vietnam timezone
                    event_time = VN_TZ.localize(event_time_naive)
                    
                    # If event already passed today, assume it's for tomorrow
                    if event_time < now:
                        event_time = event_time + timedelta(days=1)
                    
                    # Initialize tracking
                    self.scheduled_events[event_id] = {
                        'actual_posted': False,
                        'event': event
                    }
                    
                    # Schedule the check task
                    task = asyncio.create_task(self._check_and_post_event(event, event_time))
                    self.event_tasks.append(task)
                    print(f"  � Scheduled checks for {event_name} at {event_time.strftime('%H:%M')}")
                    
                except Exception as e:
                    print(f"❌ Error scheduling {event_name}: {e}")
                    continue
            
            print(f"✅ Scheduled {len(self.event_tasks)} event check tasks")
            
        except Exception as e:
            print(f"❌ Economic Calendar Scheduler error: {e}")
            import traceback
            traceback.print_exc()
    
    @economic_calendar_scheduler.before_loop
    async def before_economic_calendar_scheduler(self):
        """Đợi bot sẵn sàng và đợi đến 07:00 UTC+7"""
        await self.bot.wait_until_ready()
        
        VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(VN_TZ)
        
        # Calculate next 7:00 AM
        target_hour = 7
        if now.hour >= target_hour:
            # Already past 7 AM today, schedule for tomorrow 7 AM
            next_run = now + timedelta(days=1)
            next_run = next_run.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        else:
            # Before 7 AM today, schedule for today 7 AM
            next_run = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)
        
        wait_seconds = (next_run - now).total_seconds()
        
        print(f"⏰ Economic Calendar Scheduler initialized at {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Next run scheduled for {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Waiting {wait_seconds:.0f} seconds ({wait_seconds/3600:.1f} hours)...")
        
        await asyncio.sleep(wait_seconds)
    
    async def _check_and_post_event(self, event, event_time):
        """Check and post event with retry logic
        
        Retry strategy (Option 3 - Hybrid):
        - T+0: First check (all impacts)
        - T+2: Retry if no data (Medium/High only)
        - T+5: Final retry (High only)
        
        Args:
            event: Event dict with id, time, impact, etc.
            event_time: datetime object of when event occurs (UTC+7)
        """
        try:
            VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
            event_id = event.get('id')
            impact = event.get('impact', 'Low')
            event_name = event.get('event', 'Unknown')
            
            # Check times based on impact
            check_times = [0]  # T+0 for all
            if impact in ['Medium', 'High']:
                check_times.append(2)  # T+2 for Medium/High
            if impact == 'High':
                check_times.append(5)  # T+5 for High only
            
            for offset_minutes in check_times:
                check_time = event_time + timedelta(minutes=offset_minutes)
                now = datetime.now(VN_TZ)
                
                # Wait until check_time
                wait_seconds = (check_time - now).total_seconds()
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)
                
                # Check if already posted
                if self.scheduled_events.get(event_id, {}).get('actual_posted'):
                    print(f"✅ Event {event_name} already posted, skipping further checks")
                    return
                
                # Re-fetch data for this specific event
                print(f"🔍 Checking event {event_name} at T+{offset_minutes} min...")
                updated_events = await self.fetch_economic_calendar(target_time=event_time)
                
                # Find this specific event in updated data
                updated_event = None
                for e in updated_events:
                    if e.get('id') == event_id:
                        updated_event = e
                        break
                
                if not updated_event:
                    print(f"⚠️ Event {event_name} not found in re-fetch")
                    continue
                
                # Check if actual value exists
                actual = updated_event.get('actual', 'N/A')
                
                if actual and actual != 'N/A':
                    # Post to all configured guilds
                    for guild in self.bot.guilds:
                        config = self.load_news_config(guild.id)
                        
                        if config and config.get('economic_calendar_channel'):
                            channel = self.bot.get_channel(config['economic_calendar_channel'])
                            
                            if channel:
                                await self.send_economic_event_update(channel, updated_event, is_update=True)
                                print(f"✅ Posted actual for {event_name} ({impact}) to {guild.name} at T+{offset_minutes}")
                    
                    # Mark as posted
                    if event_id in self.scheduled_events:
                        self.scheduled_events[event_id]['actual_posted'] = True
                    return  # Success, no need for further retries
                
                else:
                    print(f"⏳ No actual value for {event_name} at T+{offset_minutes}, will retry..." if offset_minutes < max(check_times) else f"❌ No actual value found for {event_name} after all retries")
            
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"❌ Error in _check_and_post_event for {event.get('event', 'Unknown')}: {e}")
            import traceback
            traceback.print_exc()
    
    @commands.command(name='testcalendar')
    @commands.has_permissions(administrator=True)
    async def test_post_calendar(self, ctx):
        """Command để test đăng Economic Calendar ngay lập tức (giống daily summary)"""
        await ctx.send("📊 Đang lấy dữ liệu Economic Calendar...")
        
        try:
            config = self.load_news_config(ctx.guild.id)
            
            if not config or not config.get('economic_calendar_channel'):
                await ctx.send("❌ Chưa cấu hình Economic Calendar channel!")
                return
            
            channel = self.bot.get_channel(config['economic_calendar_channel'])
            
            if not channel:
                await ctx.send(f"❌ Không tìm thấy channel ID: {config['economic_calendar_channel']}")
                return
            
            # Fetch events from now until 4:30 AM tomorrow
            events = await self.fetch_economic_calendar(target_time=None)
            
            if not events:
                await ctx.send("⚠️ **Không có sự kiện nào được tìm thấy!**\n\n" +
                              "Có thể do:\n" +
                              "• Investing.com chưa cập nhật dữ liệu\n" +
                              "• Tất cả events đã kết thúc\n" +
                              "• Lỗi kết nối đến Investing.com\n\n" +
                              "Hãy thử lại sau ít phút! ⏰")
                return
            
            await ctx.send(f"✅ Đã lấy {len(events)} sự kiện. Đang gửi daily summary...")
            
            # Send daily summary (same as 7 AM automatic post)
            await self.send_daily_summary(channel, events)
            
            await ctx.send("✅ Đã gửi daily summary thành công!")
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi: {e}")
            print(f"Error in testcalendar: {e}")
            import traceback
            traceback.print_exc()
    
    @commands.command(name='schedulenow')
    @commands.has_permissions(administrator=True)
    async def schedule_now(self, ctx):
        """Command để trigger scheduler ngay lập tức (gửi daily summary + schedule events)"""
        await ctx.send("🗓️ Triggering Economic Calendar Scheduler...")
        
        try:
            config = self.load_news_config(ctx.guild.id)
            
            if not config or not config.get('economic_calendar_channel'):
                await ctx.send("❌ Chưa cấu hình Economic Calendar channel!")
                return
            
            channel = self.bot.get_channel(config['economic_calendar_channel'])
            if not channel:
                await ctx.send(f"❌ Không tìm thấy channel!")
                return
            
            # Cancel existing tasks
            for task in self.event_tasks:
                if not task.done():
                    task.cancel()
            self.event_tasks.clear()
            self.scheduled_events.clear()
            
            # Fetch events from now until 4:30 AM tomorrow
            VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
            now = datetime.now(VN_TZ)
            
            events = await self.fetch_economic_calendar(target_time=None)
            
            if not events:
                await ctx.send("⚠️ No events found!")
                return
            
            await ctx.send(f"📊 Found {len(events)} events. Sending daily summary...")
            
            # Send daily summary
            await self.send_daily_summary(channel, events)
            
            # Schedule event checks
            important_events = [e for e in events if e.get('impact') in ['Medium', 'High']]
            
            for event in important_events:
                event_id = event.get('id')
                event_time_str = event.get('time', '')
                event_name = event.get('event', 'Unknown')
                
                if not event_time_str or event_time_str in ('All Day', 'Tentative'):
                    continue
                
                try:
                    # Parse event time
                    if '/' in event_time_str:
                        dt = datetime.strptime(event_time_str, '%d/%m %H:%M')
                        event_time_naive = datetime(year=now.year, month=dt.month, day=dt.day, hour=dt.hour, minute=dt.minute)
                    else:
                        parsed = datetime.strptime(event_time_str, '%H:%M')
                        event_time_naive = datetime(year=now.year, month=now.month, day=now.day, hour=parsed.hour, minute=parsed.minute)
                    
                    event_time = VN_TZ.localize(event_time_naive)
                    
                    if event_time < now:
                        event_time = event_time + timedelta(days=1)
                    
                    self.scheduled_events[event_id] = {
                        'actual_posted': False,
                        'event': event
                    }
                    
                    task = asyncio.create_task(self._check_and_post_event(event, event_time))
                    self.event_tasks.append(task)
                    
                except Exception as e:
                    print(f"❌ Error scheduling {event_name}: {e}")
                    continue
            
            await ctx.send(f"✅ Scheduled {len(self.event_tasks)} event check tasks!")
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

async def setup(bot):
    """Setup function để load cog"""
    await bot.add_cog(NewsCog(bot))

