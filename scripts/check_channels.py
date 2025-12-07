import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import json

load_dotenv()

async def check_channels():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"Bot: {bot.user}\n")
        
        # Load config
        with open('data/news_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        for guild_id, guild_config in config['guilds'].items():
            print(f"=== Guild ID: {guild_id} ===")
            guild = bot.get_guild(int(guild_id))
            
            if not guild:
                print(f"❌ Bot không tìm thấy guild này!\n")
                continue
            
            print(f"✅ Guild: {guild.name}")
            
            # Check các channel (prefer 'glassnode_channel' but accept legacy 'messari_channel')
            channels_to_check = {
                'glassnode_channel': guild_config.get('glassnode_channel') or guild_config.get('messari_channel'),
                'santiment_channel': guild_config.get('santiment_channel'),
                '5phutcrypto_channel': guild_config.get('5phutcrypto_channel'),
                'economic_calendar_channel': guild_config.get('economic_calendar_channel')
            }
            
            for ch_name, ch_id in channels_to_check.items():
                if ch_id:
                    channel = bot.get_channel(ch_id)
                    if channel:
                        # Check permissions
                        perms = channel.permissions_for(guild.me)
                        can_send = perms.send_messages and perms.embed_links
                        status = "✅" if can_send else "⚠️ (Không có quyền)"
                        print(f"  {status} {ch_name}: #{channel.name} (ID: {ch_id})")
                    else:
                        print(f"  ❌ {ch_name}: Channel ID {ch_id} không tìm thấy!")
            
            # Check RSS feeds
            if guild_config.get('rss_feeds'):
                print(f"  RSS Feeds: {len(guild_config['rss_feeds'])} feeds")
                for feed in guild_config['rss_feeds'][:3]:
                    ch_id = feed.get('channel_id')
                    channel = bot.get_channel(ch_id)
                    if channel:
                        perms = channel.permissions_for(guild.me)
                        can_send = perms.send_messages and perms.embed_links
                        status = "✅" if can_send else "⚠️"
                        print(f"    {status} {feed['name']}: #{channel.name}")
                    else:
                        print(f"    ❌ {feed['name']}: Channel {ch_id} không tìm thấy")
            
            print()
        
        await bot.close()
    
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(check_channels())
