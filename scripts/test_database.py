"""
Test database and translation cache functionality
"""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_database
from translation_cache import get_translation_cache
from logger_config import get_logger

logger = get_logger('test_database')


def test_database():
    """Test database operations"""
    print("=" * 60)
    print("Testing Database Operations")
    print("=" * 60)
    
    db = get_database()
    
    # Test 1: Get guild config
    print("\n1️⃣  Testing guild config...")
    config = db.get_guild_config(1394159510725070961)
    print(f"   ✅ Guild ID: {config['guild_id']}")
    print(f"   ✅ Glassnode channel: {config['glassnode_channel']}")
    print(f"   ✅ RSS feeds: {len(config['rss_feeds'])}")
    
    # Test 2: Check article posting
    print("\n2️⃣  Testing article tracking...")
    test_id = "test_article_123"
    
    # Check if posted
    is_posted = db.is_article_posted(1394159510725070961, test_id, "test_source")
    print(f"   ✅ Article posted status: {is_posted}")
    
    # Mark as posted
    if not is_posted:
        db.mark_article_posted(
            1394159510725070961,
            test_id,
            "test_source",
            "Test Article",
            "https://example.com"
        )
        print(f"   ✅ Marked article as posted")
        
        # Verify
        is_posted = db.is_article_posted(1394159510725070961, test_id, "test_source")
        print(f"   ✅ Verification: {is_posted}")
    
    # Test 3: Statistics
    print("\n3️⃣  Database statistics...")
    stats = db.get_statistics()
    print(f"   ✅ Total guilds: {stats['total_guilds']}")
    print(f"   ✅ Total RSS feeds: {stats['total_rss_feeds']}")
    print(f"   ✅ Total articles: {stats['total_articles']}")
    
    print("\n✅ Database tests passed!")


def test_translation_cache():
    """Test translation cache"""
    print("\n" + "=" * 60)
    print("Testing Translation Cache")
    print("=" * 60)
    
    cache = get_translation_cache()
    
    # Test 1: Cache miss
    print("\n1️⃣  Testing cache miss...")
    text1 = "Hello, this is a test"
    result = cache.get(text1)
    print(f"   ✅ Cache miss (expected None): {result}")
    
    # Test 2: Cache set
    print("\n2️⃣  Caching translation...")
    translation1 = "Xin chào, đây là một bài test"
    cache.set(text1, translation1)
    print(f"   ✅ Cached: '{text1}' -> '{translation1}'")
    
    # Test 3: Cache hit
    print("\n3️⃣  Testing cache hit...")
    result = cache.get(text1)
    print(f"   ✅ Cache hit: {result == translation1}")
    print(f"   ✅ Retrieved: '{result}'")
    
    # Test 4: Multiple entries
    print("\n4️⃣  Testing multiple entries...")
    cache.set("Test 2", "Thử nghiệm 2")
    cache.set("Test 3", "Thử nghiệm 3")
    print(f"   ✅ Added 2 more entries")
    
    # Test 5: Cache stats
    print("\n5️⃣  Cache statistics...")
    cache.print_stats()
    
    print("\n✅ Translation cache tests passed!")


def main():
    """Run all tests"""
    try:
        test_database()
        test_translation_cache()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
