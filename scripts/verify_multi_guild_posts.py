import discord
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Đọc config
with open('data/news_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print("=" * 60)
    
    # Kiểm tra tin trong 24h gần nhất
    check_time = datetime.utcnow() - timedelta(hours=24)
    
    for guild_id_str, guild_config in config.get('guilds', {}).items():
        guild_id = int(guild_id_str)
        guild = client.get_guild(guild_id)
        
        if not guild:
            print(f"❌ Không tìm thấy guild {guild_id}")
            continue
            
        print(f"\n📌 GUILD: {guild.name} (ID: {guild_id})")
        print("-" * 60)
        
        # Kiểm tra các channel chính (Glassnode migrated from legacy 'messari')
        glass_ch = guild_config.get('glassnode_channel') or guild_config.get('messari_channel')
        channels_to_check = {
            "Glassnode": glass_ch,
            "Santiment": guild_config.get('santiment_channel'),
            "5phutcrypto": guild_config.get('5phutcrypto_channel'),
            "Economic Calendar": guild_config.get('economic_calendar_channel')
        }
        
        for channel_name, channel_id in channels_to_check.items():
            if not channel_id:
                continue
                
            channel = guild.get_channel(channel_id)
            if not channel:
                print(f"  ❌ {channel_name}: Không tìm thấy channel {channel_id}")
                continue
            
            # Đếm số tin trong 24h gần nhất
            try:
                messages = []
                async for msg in channel.history(limit=100, after=check_time):
                    if msg.author.id == client.user.id:  # Chỉ đếm tin của bot
                        messages.append(msg)
                
                if messages:
                    latest_msg = messages[0]
                    print(f"  ✅ {channel_name}: {len(messages)} bài trong 24h")
                    print(f"     → Bài mới nhất: {latest_msg.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                    if latest_msg.embeds:
                        print(f"     → Tiêu đề: {latest_msg.embeds[0].title[:50]}...")
                else:
                    print(f"  ⚠️  {channel_name}: Không có bài nào trong 24h")
            except Exception as e:
                print(f"  ❌ {channel_name}: Lỗi khi kiểm tra - {e}")
        
        # Kiểm tra RSS feeds
        print(f"\n  📡 RSS Feeds:")
        if 'rss_feeds' in guild_config:
            for feed in guild_config['rss_feeds']:
                channel_id = feed.get('channel_id')
                feed_url = feed.get('url', 'Unknown')
                
                if not channel_id:
                    continue
                    
                channel = guild.get_channel(channel_id)
                if not channel:
                    print(f"    ❌ RSS {feed_url[:30]}...: Không tìm thấy channel")
                    continue
                
                try:
                    count = 0
                    async for msg in channel.history(limit=50, after=check_time):
                        if msg.author.id == client.user.id:
                            count += 1
                    
                    if count > 0:
                        print(f"    ✅ RSS: {count} bài trong 24h")
                    else:
                        print(f"    ⚠️  RSS: Không có bài nào trong 24h")
                except Exception as e:
                    print(f"    ❌ RSS: Lỗi - {e}")
    
    print("\n" + "=" * 60)
    await client.close()

client.run(TOKEN)
