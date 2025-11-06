import json

with open('data/last_post_ids.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Before - Messari: {len(data['messari'])}, 5phutcrypto: {len(data['5phutcrypto'])}, Economic: {len(data['economic_events'])}")

# Xóa một nửa dữ liệu
data['messari'] = data['messari'][:2]
data['5phutcrypto'] = data['5phutcrypto'][:2]
data['economic_events'] = data['economic_events'][:20]

for feed_url in data['rss']:
    original_len = len(data['rss'][feed_url])
    data['rss'][feed_url] = data['rss'][feed_url][:original_len//2]
    print(f"RSS {feed_url[:50]}: {original_len} -> {len(data['rss'][feed_url])}")

with open('data/last_post_ids.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nAfter - Messari: {len(data['messari'])}, 5phutcrypto: {len(data['5phutcrypto'])}, Economic: {len(data['economic_events'])}")
print('✅ Đã xóa một nửa dữ liệu')
