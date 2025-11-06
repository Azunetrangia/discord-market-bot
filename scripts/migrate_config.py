#!/usr/bin/env python3
"""Script để migrate config từ format cũ sang format mới với per-guild storage"""

import json

# Load config cũ
with open('data/news_config.json', 'r', encoding='utf-8') as f:
    old_config = json.load(f)

# Tách config theo guild dựa trên channel_id
guilds = {}

# Tìm guild_id từ channel_id
# Guild 1: channels 1394159512293736479 (Server "Khang")
# Guild 2: channels 1261675273171112056 (Server "Manhdmm")

# Giả sử guild_id của mỗi channel (trong thực tế bot sẽ lấy từ Discord)
# Tạm thời tôi sẽ tạo 2 guild configs riêng
channel_to_guild = {
    1394159512293736479: "guild_1",  # Placeholder
    1261675273171112056: "guild_2"   # Placeholder
}

# Tạo config cho từng guild
for guild_key in set(channel_to_guild.values()):
    guilds[guild_key] = {
        "messari_channel": None,
        "santiment_channel": None,
        "rss_feeds": []
    }

# Phân chia messari_channel
if old_config.get('messari_channel'):
    guild_key = channel_to_guild.get(old_config['messari_channel'])
    if guild_key:
        guilds[guild_key]['messari_channel'] = old_config['messari_channel']

# Phân chia santiment_channel
if old_config.get('santiment_channel'):
    guild_key = channel_to_guild.get(old_config['santiment_channel'])
    if guild_key:
        guilds[guild_key]['santiment_channel'] = old_config['santiment_channel']

# Phân chia RSS feeds
for feed in old_config.get('rss_feeds', []):
    guild_key = channel_to_guild.get(feed['channel_id'])
    if guild_key:
        guilds[guild_key]['rss_feeds'].append(feed)

# Tạo config mới với format per-guild
new_config = {
    "guilds": guilds
}

# Lưu config mới
with open('data/news_config.json', 'w', encoding='utf-8') as f:
    json.dump(new_config, f, indent=2, ensure_ascii=False)

print("✅ Đã migrate config!")
print(f"📊 Tìm thấy {len(guilds)} guild(s):")
for guild_key, config in guilds.items():
    print(f"\n{guild_key}:")
    print(f"  - Messari: {config['messari_channel']}")
    print(f"  - Santiment: {config['santiment_channel']}")
    print(f"  - RSS Feeds: {len(config['rss_feeds'])}")
