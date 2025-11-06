import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def check_guilds():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"Bot: {bot.user}")
        print(f"Total guilds: {len(bot.guilds)}")
        print("\nGuilds:")
        for guild in bot.guilds:
            print(f"  - {guild.name} (ID: {guild.id})")
            print(f"    Members: {guild.member_count}")
            print(f"    Channels: {len(guild.channels)}")
        
        await bot.close()
    
    await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    asyncio.run(check_guilds())
