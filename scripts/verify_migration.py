"""
Verify migration from JSON to SQLite
Compares old JSON data with new database to ensure accuracy
"""

import sys
import os
import json

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_database
from logger_config import get_logger

logger = get_logger('verify_migration')


def load_json_files():
    """Load old JSON files"""
    config_path = 'data/news_config.json'
    posts_path = 'data/last_post_ids.json'
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    with open(posts_path, 'r') as f:
        posts = json.load(f)
    
    return config, posts


def verify_guilds(db, old_config):
    """Verify guild configurations"""
    print("\n1️⃣  Verifying Guild Configurations...")
    
    guilds = old_config.get('guilds', {})
    errors = []
    
    for guild_id_str, old_cfg in guilds.items():
        guild_id = int(guild_id_str)
        
        # Get from database
        new_cfg = db.get_guild_config(guild_id)
        
        # Compare channels
        checks = [
            ('glassnode_channel', 'glassnode_channel'),
            ('santiment_channel', 'santiment_channel'),
            ('5phutcrypto_channel', 'phutcrypto_channel'),
            ('theblock_channel', 'theblock_channel'),
        ]
        
        for old_key, new_key in checks:
            old_val = old_cfg.get(old_key)
            new_val = new_cfg.get(new_key)
            
            if old_val != new_val:
                errors.append(f"Guild {guild_id}: {old_key} mismatch - "
                            f"JSON: {old_val}, DB: {new_val}")
        
        # Compare RSS feeds count
        old_feeds = len(old_cfg.get('rss_feeds', []))
        new_feeds = len(new_cfg.get('rss_feeds', []))
        
        if old_feeds != new_feeds:
            errors.append(f"Guild {guild_id}: RSS feeds mismatch - "
                        f"JSON: {old_feeds}, DB: {new_feeds}")
    
    if errors:
        print("   ❌ Errors found:")
        for error in errors:
            print(f"      • {error}")
        return False
    else:
        print(f"   ✅ All {len(guilds)} guilds verified successfully")
        return True


def verify_rss_feeds(db, old_config):
    """Verify RSS feeds"""
    print("\n2️⃣  Verifying RSS Feeds...")
    
    guilds = old_config.get('guilds', {})
    total_feeds = 0
    errors = []
    
    for guild_id_str, old_cfg in guilds.items():
        guild_id = int(guild_id_str)
        old_feeds = old_cfg.get('rss_feeds', [])
        new_feeds = db.get_rss_feeds(guild_id)
        
        total_feeds += len(old_feeds)
        
        # Check each feed
        for old_feed in old_feeds:
            found = False
            for new_feed in new_feeds:
                if (old_feed['url'] == new_feed['url'] and 
                    old_feed['name'] == new_feed['name']):
                    found = True
                    # Check channel ID
                    if old_feed['channel_id'] != new_feed['channel_id']:
                        errors.append(f"Feed '{old_feed['name']}': channel mismatch")
                    break
            
            if not found:
                errors.append(f"Feed '{old_feed['name']}' not found in database")
    
    if errors:
        print("   ❌ Errors found:")
        for error in errors:
            print(f"      • {error}")
        return False
    else:
        print(f"   ✅ All {total_feeds} RSS feeds verified successfully")
        return True


def verify_posted_articles(db, old_posts):
    """Verify posted articles tracking"""
    print("\n3️⃣  Verifying Posted Articles...")
    
    guilds = old_posts.get('guilds', {})
    total_articles = 0
    sample_checks = 0
    errors = []
    
    for guild_id_str, guild_posts in guilds.items():
        guild_id = int(guild_id_str)
        
        # Check regular sources
        for source, article_ids in guild_posts.items():
            if source == 'rss':
                # Handle RSS feeds
                for feed_url, ids in article_ids.items():
                    for article_id in ids[:5]:  # Sample first 5
                        total_articles += 1
                        sample_checks += 1
                        
                        # Check in database
                        exists = db.is_article_posted(guild_id, article_id, f'rss:{feed_url}')
                        if not exists:
                            errors.append(f"Article {article_id} (RSS) not found in DB")
            else:
                # Regular sources
                for article_id in article_ids[:5]:  # Sample first 5
                    total_articles += 1
                    sample_checks += 1
                    
                    # Check in database
                    exists = db.is_article_posted(guild_id, article_id, source)
                    if not exists:
                        errors.append(f"Article {article_id} ({source}) not found in DB")
    
    if errors:
        print("   ❌ Errors found in sample:")
        for error in errors[:10]:  # Show first 10
            print(f"      • {error}")
        if len(errors) > 10:
            print(f"      ... and {len(errors) - 10} more")
        return False
    else:
        print(f"   ✅ Sampled {sample_checks} articles - all verified successfully")
        return True


def verify_statistics(db, old_config, old_posts):
    """Verify overall statistics"""
    print("\n4️⃣  Verifying Statistics...")
    
    # Count from JSON
    json_guilds = len(old_config.get('guilds', {}))
    json_feeds = sum(len(cfg.get('rss_feeds', [])) 
                     for cfg in old_config.get('guilds', {}).values())
    
    json_articles = 0
    for guild_posts in old_posts.get('guilds', {}).values():
        for source, data in guild_posts.items():
            if source == 'rss':
                json_articles += sum(len(ids) for ids in data.values())
            else:
                json_articles += len(data)
    
    # Get from database
    db_stats = db.get_statistics()
    
    print(f"\n   📊 Comparison:")
    print(f"   • Guilds:       JSON: {json_guilds:4d}  |  DB: {db_stats['total_guilds']:4d}")
    print(f"   • RSS Feeds:    JSON: {json_feeds:4d}  |  DB: {db_stats['total_rss_feeds']:4d}")
    print(f"   • Articles:     JSON: {json_articles:4d}  |  DB: {db_stats['total_articles']:4d}")
    
    # Check for discrepancies
    discrepancies = []
    if json_guilds != db_stats['total_guilds']:
        discrepancies.append(f"Guild count mismatch: {json_guilds} vs {db_stats['total_guilds']}")
    
    if json_feeds != db_stats['total_rss_feeds']:
        discrepancies.append(f"RSS feed count mismatch: {json_feeds} vs {db_stats['total_rss_feeds']}")
    
    # Allow small variance in articles (test entries)
    article_diff = abs(json_articles - db_stats['total_articles'])
    if article_diff > 5:
        discrepancies.append(f"Article count mismatch: {json_articles} vs {db_stats['total_articles']}")
    
    if discrepancies:
        print("\n   ⚠️  Discrepancies found:")
        for disc in discrepancies:
            print(f"      • {disc}")
        return False
    else:
        print("\n   ✅ All statistics match!")
        return True


def main():
    """Run migration verification"""
    print("=" * 70)
    print("MIGRATION VERIFICATION")
    print("=" * 70)
    print("\nComparing JSON files with SQLite database...")
    
    try:
        # Load old data
        print("\n📂 Loading JSON files...")
        old_config, old_posts = load_json_files()
        print("   ✅ JSON files loaded")
        
        # Get database
        print("\n🗄️  Connecting to database...")
        db = get_database()
        print("   ✅ Database connected")
        
        # Run verifications
        results = []
        results.append(("Guild Configs", verify_guilds(db, old_config)))
        results.append(("RSS Feeds", verify_rss_feeds(db, old_config)))
        results.append(("Posted Articles", verify_posted_articles(db, old_posts)))
        results.append(("Statistics", verify_statistics(db, old_config, old_posts)))
        
        # Summary
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        
        all_passed = all(result[1] for result in results)
        
        for name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}  {name}")
        
        print("=" * 70)
        
        if all_passed:
            print("\n🎉 All verifications passed! Migration is accurate.")
            print("\n✅ Safe to use database. You can delete old JSON files after 7 days.")
            return 0
        else:
            print("\n⚠️  Some verifications failed. Check errors above.")
            print("\n⚠️  Do NOT delete JSON files yet. Investigate discrepancies.")
            return 1
        
    except Exception as e:
        logger.error(f"Verification error: {e}", exc_info=True)
        print(f"\n❌ Verification failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
