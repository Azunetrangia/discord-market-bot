import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            application_id=None
        )
        
    async def setup_hook(self):
        """Load all cogs when bot starts"""
        # Load cogs
        await self.load_extension('cogs.news_cog')
        await self.load_extension('cogs.health_checker')  # RSS Health Monitoring
        
        # Sync commands
        await self.tree.sync()
        print(f"Synced commands")
        
    async def on_ready(self):
        print(f'Bot đã đăng nhập: {self.user.name}')
        print(f'Bot ID: {self.user.id}')
        print('------')

# Tạo bot instance
bot = MyBot()

# View chính với 2 buttons
class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # View không bao giờ timeout
        
    @discord.ui.button(label="Quản lý Tin tức", style=discord.ButtonStyle.primary, emoji="📰", row=0)
    async def news_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button để truy cập quản lý tin tức"""
        # Kiểm tra quyền admin cho chức năng quản lý tin tức
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Bạn cần có quyền Administrator để quản lý tin tức!",
                ephemeral=True
            )
            return
            
        # Import và tạo NewsMenuView từ news_cog
        from cogs.news_cog import NewsMenuView
        view = NewsMenuView()
        
        embed = discord.Embed(
            title="📰 Quản lý Tin tức",
            description="Chọn một tùy chọn từ menu bên dưới:",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="Economic Calendar", style=discord.ButtonStyle.success, emoji="📊", row=0)
    async def economic_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button để truy cập Economic Calendar - Coming Soon"""
        # Kiểm tra quyền admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Bạn cần có quyền Administrator để quản lý Economic Calendar!",
                ephemeral=True
            )
            return
        
        # Placeholder message - feature coming soon
        embed = discord.Embed(
            title="📊 Economic Calendar",
            description="🚧 Tính năng Economic Calendar sẽ được cập nhật trong tương lai\n\nChúng tôi đang phát triển phiên bản mới với nhiều cải tiến!",
            color=discord.Color.gold()
        )
        embed.set_footer(text="Stay tuned for updates! 🎯")
        
        await interaction.response.edit_message(embed=embed, view=None)

# Lệnh /start duy nhất
@bot.tree.command(name="start", description="Khởi động bot và truy cập quản lý tin tức")
async def start_command(interaction: discord.Interaction):
    """Lệnh /start - điểm khởi đầu cho quản lý tin tức"""
    
    embed = discord.Embed(
        title="🤖 Chào mừng đến với News Bot!",
        description="Bot tự động đăng tin tức từ nhiều nguồn với dịch tự động sang tiếng Việt",
        color=discord.Color.blurple()
    )
    embed.add_field(
        name="📰 Quản lý Tin tức",
        value="Cấu hình và quản lý nguồn tin tự động (Glassnode, Santiment, The Block, 5phutcrypto, RSS)\n• Tự động dịch sang tiếng Việt\n• Hỗ trợ RSS từ mọi nguồn\n• Kiểm tra tin mới mỗi 5 phút",
        inline=False
    )
    embed.add_field(
        name="📊 Economic Calendar",
        value="🚧 Tính năng đang được phát triển - Coming Soon!\n• Sẽ cập nhật trong phiên bản tiếp theo",
        inline=False
    )
    
    view = MainView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Chạy bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Lỗi: Không tìm thấy DISCORD_TOKEN trong file .env")
        exit(1)
    
    bot.run(token)
