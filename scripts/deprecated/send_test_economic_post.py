"""Send a single test economic-calendar embed to the configured channel.

Usage: run from project root (`discord-bot/`) where `data/news_config.json` lives.
Requires DISCORD_TOKEN in environment or .env.
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    print("ERROR: DISCORD_TOKEN not set in environment or .env")
    raise SystemExit(1)

import asyncio
import discord
import pytz
from datetime import datetime

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'news_config.json'))


def get_channel_id():
    # Try ENV override
    env_ch = os.getenv('ECONOMIC_CHANNEL_ID')
    if env_ch:
        try:
            return int(env_ch)
        except:
            pass

    # Read config and return first configured channel
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"Failed to load config {CONFIG_PATH}: {e}")
        return None

    for guild_id, guild_cfg in cfg.get('guilds', {}).items():
        ch = guild_cfg.get('economic_calendar_channel')
        if ch:
            return int(ch)

    return None


class Poster(discord.Client):
    def __init__(self, channel_id, **opts):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.channel_id = channel_id

    async def on_ready(self):
        print(f"Logged in as {self.user} ({self.user.id})")
        try:
            ch = self.get_channel(self.channel_id) or await self.fetch_channel(self.channel_id)
        except Exception as e:
            print(f"Failed to fetch channel {self.channel_id}: {e}")
            await self.close()
            return

        vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(vietnam_tz)

        embed = discord.Embed(
            title="✅ Đã công bố (TEST): Example Economic Event",
            color=0xFF8C00,
            timestamp=now
        )

        comparison_text = "```diff\n"
        comparison_text += "  📊 Forecast:  46.7\n"
        comparison_text += "- 📉 Actual:    44.1\n"
        # Avoid literal triple-backticks in source to prevent parsing issues in some environments
        comparison_text += "  📋 Previous:  46.2\n" + (chr(96) * 3)

        embed.add_field(name="🟠 **Medium Impact Event**", value=comparison_text, inline=False)

        info_text = f"⏰ **Time:** {now.strftime('%H:%M UTC+7')}\n"
        info_text += "🌍 **Country:** Testland\n\n"
        info_text += "📊 **Status:** Đã công bố kết quả (TEST)"

        embed.add_field(name="ℹ️ Details", value=info_text, inline=False)

        embed.set_author(name="Investing.com Economic Calendar", icon_url="https://www.google.com/s2/favicons?domain=investing.com&sz=128")
        embed.set_footer(text="📊 Economic Calendar • TEST POST", icon_url="https://www.google.com/s2/favicons?domain=investing.com&sz=128")

        try:
            msg = await ch.send(embed=embed)
            print(f"Sent test embed to {ch} (ID: {ch.id}) — message id: {msg.id}")
        except Exception as e:
            print(f"Failed to send message: {e}")

        await self.close()


def main():
    cid = get_channel_id()
    if not cid:
        print("No economic_calendar_channel found in config and ECONOMIC_CHANNEL_ID not set.")
        return

    client = Poster(cid)
    client.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
