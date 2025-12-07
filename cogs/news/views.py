"""
Discord UI Views and Modals for news management
"""

import discord
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..news_cog import NewsCog


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
    
    def __init__(self, cog: 'NewsCog'):
        super().__init__()
        self.cog = cog
        
    async def on_submit(self, interaction: discord.Interaction):
        """Xử lý khi user submit Modal"""
        # Validate RSS URL
        url_str = str(self.url)
        if not self._validate_rss_url(url_str):
            await interaction.response.send_message(
                "❌ URL không hợp lệ! Vui lòng nhập URL RSS feed hợp lệ (bắt đầu bằng http:// hoặc https://)",
                ephemeral=True
            )
            return
        
        # Lưu thông tin tạm
        self.cog.temp_rss_data[interaction.user.id] = {
            'url': url_str,
            'name': str(self.name)
        }
        
        # Hiển thị ChannelSelect
        view = ChannelSelectView(self.cog, 'rss')
        embed = discord.Embed(
            title="📺 Chọn kênh đăng tin",
            description=f"Chọn kênh để đăng tin từ nguồn **{self.name}**",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    @staticmethod
    def _validate_rss_url(url: str) -> bool:
        """Validate RSS URL"""
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Check for basic URL structure
        if len(url) < 10 or '.' not in url:
            return False
        
        # Block potentially malicious URLs
        blocked_domains = ['localhost', '127.0.0.1', '0.0.0.0']
        for blocked in blocked_domains:
            if blocked in url.lower():
                return False
        
        return True


class ChannelSelectView(discord.ui.View):
    """View chứa ChannelSelect để chọn kênh Discord"""
    
    def __init__(self, cog: 'NewsCog', source_type: str):
        super().__init__(timeout=60)
        self.cog = cog
        self.source_type = source_type
        
    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Chọn một kênh...",
        channel_types=[discord.ChannelType.text]
    )
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        """Xử lý khi user chọn channel"""
        channel = select.values[0]
        config = self.cog.load_news_config(interaction.guild_id)
        
        if self.source_type == 'glassnode':
            config['glassnode_channel'] = channel.id
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
            
        elif self.source_type == 'rss':
            rss_data = self.cog.temp_rss_data.get(interaction.user.id)
            if not rss_data:
                await interaction.response.edit_message(
                    content="❌ Lỗi: Không tìm thấy thông tin RSS",
                    embed=None,
                    view=None
                )
                return
                
            config['rss_feeds'].append({
                'name': rss_data['name'],
                'url': rss_data['url'],
                'channel_id': channel.id
            })
            
            del self.cog.temp_rss_data[interaction.user.id]
            
            await interaction.response.edit_message(
                content=f"✅ Đã thêm RSS Feed **{rss_data['name']}** vào kênh {channel.mention}",
                embed=None,
                view=None
            )
        
        self.cog.save_news_config(config, interaction.guild_id)


class RemoveRSSView(discord.ui.View):
    """View để chọn RSS feed cần xóa"""
    
    def __init__(self, cog: 'NewsCog', rss_feeds: list):
        super().__init__(timeout=60)
        self.cog = cog
        
        options = []
        for idx, feed in enumerate(rss_feeds):
            options.append(
                discord.SelectOption(
                    label=feed['name'],
                    description=feed['url'][:100],
                    value=str(idx)
                )
            )
        
        select = discord.ui.Select(
            placeholder="Chọn RSS feed để xóa...",
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)
        
    async def select_callback(self, interaction: discord.Interaction):
        """Xử lý khi user chọn RSS để xóa"""
        selected_idx = int(interaction.data['values'][0])
        config = self.cog.load_news_config(interaction.guild_id)
        feed_name = config['rss_feeds'][selected_idx]['name']
        del config['rss_feeds'][selected_idx]
        self.cog.save_news_config(config, interaction.guild_id)
        
        await interaction.response.edit_message(
            content=f"✅ Đã xóa RSS Feed: **{feed_name}**",
            embed=None,
            view=None
        )


class QuickSetupView(discord.ui.View):
    """View cho Quick Setup với các RSS feeds có sẵn"""
    
    def __init__(self, cog: 'NewsCog'):
        super().__init__(timeout=180)
        self.cog = cog
        
    @discord.ui.button(label="Cài đặt Tất cả", style=discord.ButtonStyle.success, emoji="⚡")
    async def setup_all_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cài đặt tất cả RSS feeds vào channel hiện tại"""
        await interaction.response.defer()
        
        preset_feeds = [
            {"name": "Thời sự - VnExpress RSS", "url": "https://vnexpress.net/rss/thoi-su.rss"},
            {"name": "BBC News", "url": "https://feeds.bbci.co.uk/news/rss.xml"},
            {"name": "Cointelegraph.com News", "url": "https://cointelegraph.com/rss"},
            {"name": "Cointelegraph - Blockchain", "url": "https://cointelegraph.com/rss/tag/blockchain"},
            {"name": "Cointelegraph - Market Analysis", "url": "https://cointelegraph.com/rss/category/market-analysis"},
            {"name": "Decrypt", "url": "https://decrypt.co/feed"}
        ]
        
        config = self.cog.load_news_config(interaction.guild_id)
        existing_urls = {feed['url'] for feed in config['rss_feeds']}
        
        added_count = 0
        for feed in preset_feeds:
            if feed['url'] not in existing_urls:
                config['rss_feeds'].append({
                    'name': feed['name'],
                    'url': feed['url'],
                    'channel_id': interaction.channel_id
                })
                added_count += 1
        
        self.cog.save_news_config(config, interaction.guild_id)
        
        embed = discord.Embed(
            title="⚡ Quick Setup Hoàn tất!",
            description=f"Đã cài đặt **{added_count}** RSS feeds vào channel này.",
            color=discord.Color.green()
        )
        
        if added_count > 0:
            feed_list = "\n".join([f"✅ {feed['name']}" for feed in preset_feeds if feed['url'] not in existing_urls])
            embed.add_field(name="📰 Feeds đã thêm:", value=feed_list, inline=False)
        
        if added_count < len(preset_feeds):
            embed.add_field(
                name="ℹ️ Lưu ý:",
                value=f"Đã bỏ qua {len(preset_feeds) - added_count} feed(s) đã tồn tại.",
                inline=False
            )
        
        await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=None)
    
    @discord.ui.button(label="Chọn Từng Cái", style=discord.ButtonStyle.primary, emoji="📝")
    async def select_individual_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cho phép chọn từng RSS feed riêng lẻ"""
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
        await interaction.response.edit_message(content="❌ Đã hủy Quick Setup.", embed=None, view=None)


class PresetRSSSelectView(discord.ui.View):
    """View để chọn RSS feeds từ danh sách có sẵn"""
    
    def __init__(self, cog: 'NewsCog'):
        super().__init__(timeout=180)
        self.cog = cog
        
        select = discord.ui.Select(
            placeholder="Chọn các RSS feeds...",
            min_values=1,
            max_values=6,
            options=[
                discord.SelectOption(label="VnExpress - Tin mới nhất", description="https://vnexpress.net/rss/thoi-su.rss", emoji="🇻🇳", value="https://vnexpress.net/rss/thoi-su.rss"),
                discord.SelectOption(label="BBC News", description="https://feeds.bbci.co.uk/news/rss.xml", emoji="🇬🇧", value="https://feeds.bbci.co.uk/news/rss.xml"),
                discord.SelectOption(label="Cointelegraph - All News", description="https://cointelegraph.com/rss", emoji="₿", value="https://cointelegraph.com/rss"),
                discord.SelectOption(label="Cointelegraph - Blockchain", description="https://cointelegraph.com/rss/tag/blockchain", emoji="⛓️", value="https://cointelegraph.com/rss/tag/blockchain"),
                discord.SelectOption(label="Cointelegraph - Market Analysis", description="https://cointelegraph.com/rss/category/market-analysis", emoji="📊", value="https://cointelegraph.com/rss/category/market-analysis"),
                discord.SelectOption(label="Decrypt", description="https://decrypt.co/feed", emoji="🔐", value="https://decrypt.co/feed")
            ]
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        """Xử lý khi user chọn các RSS feeds"""
        selected_urls = interaction.data['values']
        
        url_to_name = {
            "https://vnexpress.net/rss/thoi-su.rss": "Thời sự - VnExpress RSS",
            "https://feeds.bbci.co.uk/news/rss.xml": "BBC News",
            "https://cointelegraph.com/rss": "Cointelegraph.com News",
            "https://cointelegraph.com/rss/tag/blockchain": "Cointelegraph - Blockchain",
            "https://cointelegraph.com/rss/category/market-analysis": "Cointelegraph - Market Analysis",
            "https://decrypt.co/feed": "Decrypt"
        }
        
        config = self.cog.load_news_config(interaction.guild_id)
        existing_urls = {feed['url'] for feed in config['rss_feeds']}
        
        added_feeds = []
        for url in selected_urls:
            if url not in existing_urls:
                config['rss_feeds'].append({
                    'name': url_to_name.get(url, 'Unknown'),
                    'url': url,
                    'channel_id': interaction.channel_id
                })
                added_feeds.append(url_to_name.get(url, 'Unknown'))
        
        self.cog.save_news_config(config, interaction.guild_id)
        
        embed = discord.Embed(
            title="✅ Đã thêm RSS Feeds!",
            description=f"Đã thêm **{len(added_feeds)}** RSS feeds vào channel này.",
            color=discord.Color.green()
        )
        
        if added_feeds:
            embed.add_field(name="📰 Feeds đã thêm:", value="\n".join([f"✅ {name}" for name in added_feeds]), inline=False)
        
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
            discord.SelectOption(label="⚡ Quick Setup - Tự động cài đặt", description="Tự động thêm tất cả RSS feeds phổ biến", emoji="⚡", value="quick_setup"),
            discord.SelectOption(label="Cài đặt kênh tin Glassnode", description="Chọn kênh để nhận insights từ Glassnode", emoji="📊", value="glassnode"),
            discord.SelectOption(label="Cài đặt kênh tin Santiment", description="Chọn kênh để nhận tin từ Santiment API", emoji="📈", value="santiment"),
            discord.SelectOption(label="Cài đặt kênh tin 5 Phút Crypto", description="Chọn kênh để nhận tin từ 5phutcrypto.io", emoji="💰", value="5phutcrypto"),
            discord.SelectOption(label="Cài đặt kênh tin The Block", description="Chọn kênh để nhận tin từ The Block", emoji="📰", value="theblock"),
            discord.SelectOption(label="Thêm một RSS Feed mới", description="Thêm nguồn RSS Feed tùy chỉnh", emoji="➕", value="add_rss"),
            discord.SelectOption(label="Xóa một RSS Feed", description="Xóa RSS Feed đã cài đặt", emoji="🗑️", value="remove_rss"),
            discord.SelectOption(label="Liệt kê các nguồn tin", description="Xem tất cả nguồn tin đang hoạt động", emoji="📋", value="list_sources")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Xử lý khi user chọn một option"""
        value = select.values[0]
        cog = interaction.client.get_cog('NewsCog')
        
        if value == "quick_setup":
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
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif value in ["glassnode", "santiment", "5phutcrypto", "theblock"]:
            view = ChannelSelectView(cog, value)
            titles = {
                "glassnode": "📊 Cài đặt kênh tin Glassnode Insights",
                "santiment": "📈 Cài đặt kênh tin Santiment",
                "5phutcrypto": "💰 Cài đặt kênh tin 5 Phút Crypto",
                "theblock": "📰 Cài đặt kênh tin The Block"
            }
            embed = discord.Embed(title=titles[value], description=f"Chọn kênh để nhận tin từ {value}", color=discord.Color.blue())
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif value == "add_rss":
            modal = AddRSSModal(cog)
            await interaction.response.send_modal(modal)
            
        elif value == "remove_rss":
            config = cog.load_news_config(interaction.guild_id)
            if not config['rss_feeds']:
                await interaction.response.edit_message(content="❌ Không có RSS Feed nào để xóa!", embed=None, view=None)
                return
            view = RemoveRSSView(cog, config['rss_feeds'])
            embed = discord.Embed(title="🗑️ Xóa RSS Feed", description="Chọn RSS Feed bạn muốn xóa:", color=discord.Color.red())
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif value == "list_sources":
            await cog.list_sources_command(interaction)
