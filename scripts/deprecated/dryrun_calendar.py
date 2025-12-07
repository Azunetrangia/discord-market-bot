"""
Dry-run script for Economic Calendar: fetch events and simulate sending
(not posting to Discord). Prints summaries of embeds that would be sent.
"""
import asyncio
import sys
import os
from datetime import datetime

# ensure repo root in path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import pytz
from cogs.news_cog import NewsCog

# Fake channel/guild/bot
class FakeChannel:
    def __init__(self, name):
        self.name = name
    async def send(self, embed=None):
        # Print a compact summary of the embed
        title = getattr(embed, 'title', None)
        fields = []
        try:
            for f in embed.fields:
                fields.append((f.name, (f.value[:200] + '...') if len(f.value) > 200 else f.value))
        except Exception:
            pass
        print(f"\n--- WOULD SEND to {self.name} ---")
        print(f"Title: {title}")
        for n, v in fields:
            print(f"Field: {n} -> {v}")
        print("--- END ---\n")

class FakeGuild:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class FakeBot:
    def __init__(self, guilds, channel_map):
        self.guilds = guilds
        self._channel_map = channel_map
    def get_channel(self, channel_id):
        return self._channel_map.get(channel_id)
    async def wait_until_ready(self):
        return

async def main():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(tz)
    print(f"Dry-run: now (VN) = {now.strftime('%Y-%m-%d %H:%M:%S')}")

    guild = FakeGuild(1111, 'DryRunGuild')
    channel = FakeChannel('dryrun-calendar')
    bot = FakeBot([guild], {8888: channel})

    cog = NewsCog(bot)
    # cancel background loops started by the cog
    try:
        cog.news_checker.cancel()
        cog.daily_calendar_summary.cancel()
        cog.economic_calendar_scheduler.cancel()
    except Exception:
        pass

    # monkeypatch load_news_config to point to fake channel
    def fake_load_news_config(guild_id=None):
        return {'economic_calendar_channel': 8888}
    cog.load_news_config = fake_load_news_config

    # monkeypatch send_economic_event_update to call our fake channel.send
    async def fake_send(channel_obj, event, is_update=False):
        # Reuse NewsCog.send_economic_event_update to build embed then send
        # but to avoid network, we call the method and intercept the channel
        # by passing our fake channel into it
        await cog.send_economic_event_update(channel_obj, event, is_update=is_update)

    # Use fetch_economic_calendar to get today's events (no alert window)
    print('Fetching economic calendar (no alert window) ...')
    events = await cog.fetch_economic_calendar(use_alert_window=False)
    if not events:
        print('No events found (Investing.com may not have data for today).')
        return
    print(f'Found {len(events)} events total. Filtering Medium/High impacts...')

    to_post = [e for e in events if e.get('impact') in ('Medium', 'High')]
    print(f'Will simulate posting for {len(to_post)} events (Medium/High).')

    # Simulate sending first 10 events
    for event in to_post[:10]:
        print(f"Simulating event: {event.get('event')} @ {event.get('time')} impact={event.get('impact')}")
        await fake_send(channel, event, is_update=False)

    print('Dry-run complete.')

if __name__ == '__main__':
    asyncio.run(main())
