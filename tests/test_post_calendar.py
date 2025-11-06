"""
Script test đăng Economic Calendar ngay lập tức
"""
import discord
from discord.ext import commands
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from cogs.news_cog import NewsCog
from dotenv import load_dotenv

load_dotenv()

# Lấy token
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Tạo bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    
    # Load NewsCog
    await bot.load_extension('cogs.news_cog')
    news_cog = bot.get_cog('NewsCog')
    
    if news_cog:
        print("📰 NewsCog loaded, fetching economic calendar...")
        
        # Lặp qua guilds và post calendar
        for guild in bot.guilds:
            print(f"🔹 Processing guild: {guild.name}")
            
            try:
                config = news_cog.load_news_config(guild.id)
                
                if config and config.get('economic_calendar_channel'):
                    channel = bot.get_channel(config['economic_calendar_channel'])
                    
                    if channel:
                        print(f"📊 Found channel: {channel.name}")
                        
                        # Fetch events
                        events = await news_cog.fetch_economic_calendar()
                        print(f"✅ Fetched {len(events)} economic events")
                        
                        if events:
                            # Import dependencies
                            from datetime import datetime
                            import pytz
                            
                            vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
                            now = datetime.now(vietnam_tz)
                            
                            # Tạo embed
                            embed = discord.Embed(
                                title="📅 Economic Calendar - Lịch Kinh Tế Hôm Nay",
                                description=f"Các sự kiện kinh tế quan trọng trong ngày {now.strftime('%d/%m/%Y')}",
                                color=0x3498DB,
                                timestamp=now
                            )
                            
                            # Phân loại theo impact
                            high_impact = [e for e in events if e['impact'] == 'High']
                            medium_impact = [e for e in events if e['impact'] == 'Medium']
                            
                            print(f"📊 High: {len(high_impact)}, Medium: {len(medium_impact)}")
                            
                            # High Impact
                            if high_impact:
                                high_text = ""
                                for event in high_impact[:15]:
                                    time = event.get('time', 'TBA')
                                    name = event.get('event', 'Unknown')
                                    country = event.get('country', 'N/A')
                                    if len(name) > 60:
                                        name = name[:57] + "..."
                                    high_text += f"🔴 **{time}** - {name} ({country})\n"
                                
                                if len(high_text) > 1020:
                                    high_text = high_text[:1020] + "..."
                                
                                embed.add_field(
                                    name="🔴 High Impact Events",
                                    value=high_text if high_text else "Không có",
                                    inline=False
                                )
                            
                            # Medium Impact
                            if medium_impact:
                                medium_text = ""
                                for event in medium_impact[:15]:
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
                            
                            # Send
                            await channel.send(embed=embed)
                            print(f"✅ Posted calendar to {channel.name}")
                        else:
                            print("⚠️ No events found")
                    else:
                        print(f"⚠️ Channel not found: {config['economic_calendar_channel']}")
                else:
                    print("⚠️ No economic calendar channel configured")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n✅ Done! Shutting down bot...")
        await bot.close()
    else:
        print("❌ Could not load NewsCog")
        await bot.close()

# Run bot
bot.run(TOKEN)
