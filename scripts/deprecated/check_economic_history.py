"""Utility: check recent messages in configured Economic Calendar channel(s)

This script will:
 - load the bot token from the environment or .env
 - read `data/news_config.json` to find guilds with `economic_calendar_channel`
 - connect to Discord, fetch recent messages from those channels (up to 200)
 - print messages that look like 'actual' postings (embed title contains 'Đã công bố' or content contains keywords)

Run from project root (discord-bot/) so relative paths resolve correctly.
"""
import os
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    print("ERROR: DISCORD_TOKEN not set in environment or .env")
    raise SystemExit(1)

import discord

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'news_config.json')
DATA_FILE = os.path.abspath(DATA_FILE)

KEYWORDS = ['Đã công bố', 'Actual', '📊', '✅', 'Actual:']

async def gather_channels_from_config():
    chans = set()
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"Failed to load config {DATA_FILE}: {e}")
        return chans

    for guild_id, guild_cfg in cfg.get('guilds', {}).items():
        ch = guild_cfg.get('economic_calendar_channel')
        if ch:
            chans.add(int(ch))

    # Allow override via env
    env_ch = os.getenv('ECONOMIC_CHANNEL_ID')
    if env_ch:
        try:
            chans.add(int(env_ch))
        except:
            pass

    return chans


class HistoryChecker(discord.Client):
    def __init__(self, channel_ids, **opts):
        super().__init__(intents=discord.Intents.default())
        self.channel_ids = channel_ids

    async def on_ready(self):
        print(f"Logged in as {self.user} ({self.user.id})")
        for cid in sorted(self.channel_ids):
            try:
                ch = self.get_channel(cid) or await self.fetch_channel(cid)
            except Exception as e:
                print(f"Failed to fetch channel {cid}: {e}")
                continue

            print('\n' + '='*60)
            print(f"Channel: {ch} (ID: {cid})")
            print('='*60)

            try:
                msgs = [m async for m in ch.history(limit=200)]
            except Exception as e:
                print(f"Error fetching history for {cid}: {e}")
                continue

            matches = []
            for m in msgs:
                text = (m.content or '')
                embed_title = ''
                if m.embeds:
                    try:
                        embed_title = m.embeds[0].title or ''
                    except:
                        embed_title = ''

                combined = text + ' ' + embed_title
                if any(k in combined for k in KEYWORDS):
                    matches.append((m, embed_title))

            print(f"Scanned {len(msgs)} messages, found {len(matches)} matching posts")
            max_print = int(os.getenv('MAX_PRINT', '10'))
            full_dump = os.getenv('FULL_DUMP', '') not in ('', '0', 'false', 'False')
            for i, (m, etitle) in enumerate(matches[:max_print], 1):
                ts = m.created_at.isoformat()
                author = f"{m.author} ({m.author.id})"
                print(f"\n[{i}] {ts} by {author}")
                if etitle:
                    print(f" Embed title: {etitle}")
                if m.content:
                    print(f" Content: {m.content[:800]}")

                if full_dump and m.embeds:
                    try:
                        # discord Embed objects support to_dict()
                        ed = m.embeds[0].to_dict()
                        import json as _json
                        print('\nFull embed JSON:')
                        print(_json.dumps(ed, ensure_ascii=False, indent=2))
                    except Exception as e:
                        print(f"Failed to dump embed JSON: {e}")
                else:
                    if m.embeds and getattr(m.embeds[0], 'fields', None):
                        for fld in m.embeds[0].fields:
                            print(f" Field: {fld.name} -> {fld.value[:200]}")

                print('-'*40)

        await self.close()


def main():
    chans = asyncio.run(gather_channels_from_config())
    if not chans:
        print('No economic_calendar_channel found in config and ECONOMIC_CHANNEL_ID not set.')
        return

    client = HistoryChecker(chans)
    client.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
