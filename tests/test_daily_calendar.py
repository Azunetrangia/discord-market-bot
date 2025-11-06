import asyncio
import discord
from discord.ext import commands
import json
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_daily_calendar():
    """Test gửi daily calendar summary"""
    
    # Tạo bot instance
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"Bot đã đăng nhập: {bot.user}")
        
        # Load config
        with open('data/news_config.json', 'r', encoding='utf-8') as f:
            all_configs = json.load(f)
        
        # Fetch economic calendar
        print("📊 Fetching economic calendar...")
        url = "https://www.investing.com/economic-calendar/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        events = []
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    rows = soup.find_all('tr', {'class': 'js-event-item'})
                    print(f"Found {len(rows)} events")
                    
                    for row in rows[:50]:
                        try:
                            # Get time
                            time_elem = row.find('td', {'class': 'time'})
                            time_str = time_elem.text.strip() if time_elem else ''
                            
                            # Get country
                            country_elem = row.find('td', {'class': 'flagCur'})
                            if country_elem:
                                country_span = country_elem.find('span', {'class': 'ceFlags'})
                                country = country_span.get('title', '') if country_span else ''
                            else:
                                country = ''
                            
                            # Filter for major economies
                            major_countries = ['United States', 'Euro Zone', 'Germany', 'United Kingdom', 'Japan', 'China']
                            if country not in major_countries:
                                continue
                            
                            # Get impact
                            impact_elem = row.find('td', {'class': 'sentiment'})
                            impact_class = str(impact_elem.get('class', [])) if impact_elem else ''
                            if 'redFont' in impact_class or 'bearish' in impact_class:
                                impact = 'High'
                            elif 'yellowFont' in impact_class or 'neutral' in impact_class:
                                impact = 'Medium'
                            else:
                                impact = 'Low'
                            
                            # Get event name
                            event_elem = row.find('td', {'class': 'event'})
                            event_name = event_elem.text.strip() if event_elem else ''
                            
                            if not event_name:
                                continue
                            
                            # Get values
                            forecast_elem = row.find('td', {'class': 'fore'})
                            forecast_str = forecast_elem.text.strip() if forecast_elem else ''
                            
                            previous_elem = row.find('td', {'class': 'prev'})
                            previous_str = previous_elem.text.strip() if previous_elem else ''
                            
                            if not forecast_str and not previous_str:
                                continue
                            
                            event = {
                                'event': event_name,
                                'country': country,
                                'impact': impact,
                                'time': time_str
                            }
                            
                            events.append(event)
                            
                        except Exception as e:
                            continue
        
        print(f"✅ Scraped {len(events)} relevant events")
        
        if events:
            # Tìm channel để gửi
            for guild in bot.guilds:
                guild_id = str(guild.id)
                if guild_id in all_configs.get('guilds', {}):
                    config = all_configs['guilds'][guild_id]
                    if config.get('economic_calendar_channel'):
                        channel = bot.get_channel(config['economic_calendar_channel'])
                        if channel:
                            # Lấy giờ hiện tại
                            vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
                            now = datetime.now(vietnam_tz)
                            
                            # Tạo embed
                            embed = discord.Embed(
                                title="📅 Economic Calendar - Lịch Kinh Tế Hôm Nay",
                                description=f"Các sự kiện kinh tế quan trọng trong ngày {now.strftime('%d/%m/%Y')}",
                                color=0x3498DB,
                                timestamp=datetime.now()
                            )
                            
                            # Phân loại theo impact
                            high_impact = [e for e in events if e['impact'] == 'High']
                            medium_impact = [e for e in events if e['impact'] == 'Medium']
                            low_impact = [e for e in events if e['impact'] == 'Low']
                            
                            # High Impact
                            if high_impact:
                                high_text = ""
                                for event in high_impact[:5]:
                                    time = event.get('time', 'TBA')
                                    name = event.get('event', 'Unknown')
                                    country = event.get('country', 'N/A')
                                    high_text += f"🔴 **{time}** - {name} ({country})\n"
                                
                                embed.add_field(
                                    name="🔴 High Impact Events",
                                    value=high_text,
                                    inline=False
                                )
                            
                            # Medium Impact
                            if medium_impact:
                                medium_text = ""
                                for event in medium_impact[:5]:
                                    time = event.get('time', 'TBA')
                                    name = event.get('event', 'Unknown')
                                    country = event.get('country', 'N/A')
                                    medium_text += f"🟠 **{time}** - {name} ({country})\n"
                                
                                embed.add_field(
                                    name="🟠 Medium Impact Events",
                                    value=medium_text,
                                    inline=False
                                )
                            
                            # Low Impact
                            if low_impact:
                                low_text = ""
                                for event in low_impact[:5]:
                                    time = event.get('time', 'TBA')
                                    name = event.get('event', 'Unknown')
                                    country = event.get('country', 'N/A')
                                    low_text += f"🟢 **{time}** - {name} ({country})\n"
                                
                                embed.add_field(
                                    name="🟢 Low Impact Events",
                                    value=low_text,
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
                            print(f"✅ Đã gửi lịch Economic Calendar đến {channel.name}")
                            break
        
        await bot.close()
    
    # Run bot
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(test_daily_calendar())
