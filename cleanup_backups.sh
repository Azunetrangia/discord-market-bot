#!/bin/bash
# Cleanup script for Discord bot backups

echo "🧹 Starting cleanup..."

# Step 1: Backup original news_cog.py
echo "📦 Creating final backup of original..."
cp cogs/news_cog.py cogs/news_cog_ORIGINAL.py

# Step 2: Delete old backups
echo "🗑️  Deleting old backup files..."
rm -f cogs/news_cog_backup_20251207_103313.py
rm -f cogs/news_cog_backup_refactor.py
rm -f cogs/news_cog_clean.py
rm -f cogs/news_cog_with_economic.py

# Step 3: Activate refactored version
echo "✨ Activating refactored version..."
rm -f cogs/news_cog.py
mv cogs/news_cog_refactored.py cogs/news_cog.py

# Step 4: Move test files to tests/
echo "📁 Moving test files to tests/ directory..."
mkdir -p tests/manual
mv test_research_rss.py tests/manual/ 2>/dev/null || true
mv test_santiment_cog.py tests/manual/ 2>/dev/null || true
mv test_santiment_queries.py tests/manual/ 2>/dev/null || true
mv test_vneconomy_rss.py tests/manual/ 2>/dev/null || true

# Step 5: Delete cleanup scripts
echo "🗑️  Removing completed cleanup scripts..."
rm -f remove_economic.py
rm -f remove_economic_v2.py

# Step 6: Show summary
echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 Space saved:"
du -sh cogs/ 2>/dev/null || true
echo ""
echo "📁 Files remaining in cogs/:"
ls -lh cogs/*.py 2>/dev/null | awk '{print $5, $9}' || true
echo ""
echo "📋 Backups kept:"
ls -lh cogs/news_cog_ORIGINAL.py 2>/dev/null | awk '{print $5, $9}' || true
