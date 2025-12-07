#!/usr/bin/env python3
"""One-shot migration helper: merge any legacy 'messari' keys into 'glassnode'.

Usage:
  python scripts/migrate_messari_to_glassnode.py

What it does:
- Creates a timestamped backup of data/*.json into data/backups/
- For each guild in data/last_post_ids.json:
    - If 'messari' exists, append its IDs into 'glassnode' (dedup, keep newest),
      then remove the 'messari' key.
- For each guild in data/news_config.json:
    - If 'messari_channel' exists and 'glassnode_channel' is empty, copy the
      value to 'glassnode_channel' and remove 'messari_channel'.

This script is safe to run multiple times.
"""

import json
import os
from datetime import datetime


DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')


def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def backup_file(name):
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    src = os.path.join(DATA_DIR, name)
    dst = os.path.join(BACKUP_DIR, f'{ts}_{name}')
    if os.path.exists(src):
        with open(src, 'r', encoding='utf-8') as f:
            data = f.read()
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(data)
        print(f'Backed up {name} -> {dst}')
    else:
        print(f'Skipped backup (not found): {name}')


def load_json(path, default=None):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def migrate_last_post_ids():
    path = os.path.join(DATA_DIR, 'last_post_ids.json')
    data = load_json(path, default={'guilds': {}})
    guilds = data.get('guilds', {})
    changed = False

    for gid, gdata in list(guilds.items()):
        messari_list = gdata.pop('messari', None)
        if messari_list:
            glass = gdata.get('glassnode', [])
            # merge, preserve order (append then dedupe keeping last occurrences)
            merged = glass + messari_list
            # dedupe while preserving order, keep latest occurrences at end
            seen = set()
            deduped = []
            for item in merged:
                if item in seen:
                    continue
                seen.add(item)
                deduped.append(item)
            # keep last 100
            deduped = deduped[-100:]
            gdata['glassnode'] = deduped
            guilds[gid] = gdata
            changed = True
            print(f'Migrated {len(messari_list)} IDs from messari -> glassnode for guild {gid}')

    if changed:
        data['guilds'] = guilds
        save_json(path, data)
        print('Saved migrated last_post_ids.json')
    else:
        print('No messari entries found in last_post_ids.json')


def migrate_news_config():
    path = os.path.join(DATA_DIR, 'news_config.json')
    data = load_json(path, default={'guilds': {}})
    guilds = data.get('guilds', {})
    changed = False

    for gid, gdata in list(guilds.items()):
        if 'messari_channel' in gdata:
            if not gdata.get('glassnode_channel'):
                gdata['glassnode_channel'] = gdata.get('messari_channel')
                print(f'Copied messari_channel -> glassnode_channel for guild {gid}')
            # remove legacy key
            gdata.pop('messari_channel', None)
            guilds[gid] = gdata
            changed = True

    if changed:
        data['guilds'] = guilds
        save_json(path, data)
        print('Saved migrated news_config.json')
    else:
        print('No messari_channel keys found in news_config.json')


def main():
    ensure_backup_dir()
    backup_file('news_config.json')
    backup_file('last_post_ids.json')
    backup_file('alerts.json')

    migrate_last_post_ids()
    migrate_news_config()


if __name__ == '__main__':
    main()
