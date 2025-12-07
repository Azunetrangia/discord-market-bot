"""
Cleanup old JSON backup files after successful migration
Only run this after 7+ days of verified bot operation
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger_config import get_logger

logger = get_logger('cleanup')


def check_database_age():
    """Check if database file is old enough"""
    db_path = Path('data/news_bot.db')
    
    if not db_path.exists():
        print("❌ Database file not found!")
        print("   Migration might not be complete.")
        return False
    
    # Check file age
    file_time = datetime.fromtimestamp(db_path.stat().st_mtime)
    age = datetime.now() - file_time
    
    print(f"\n📅 Database Age: {age.days} days, {age.seconds // 3600} hours")
    
    if age.days < 7:
        print(f"⚠️  Database is only {age.days} days old")
        print("   Recommended to wait at least 7 days before cleanup")
        return False
    
    print("✅ Database is old enough for cleanup")
    return True


def list_files_to_delete():
    """List files that will be deleted"""
    files = []
    
    # Old JSON files
    for pattern in ['data/news_config.json', 'data/last_post_ids.json']:
        path = Path(pattern)
        if path.exists():
            files.append(path)
    
    # Old backups (except recent ones)
    backup_dir = Path('data/backups')
    if backup_dir.exists():
        cutoff = datetime.now() - timedelta(days=7)
        
        for backup_file in backup_dir.glob('*.json.backup'):
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_time < cutoff:
                files.append(backup_file)
    
    return files


def calculate_space_freed(files):
    """Calculate total space that will be freed"""
    total_size = sum(f.stat().st_size for f in files if f.exists())
    return total_size


def delete_files(files, dry_run=True):
    """Delete files (or show what would be deleted)"""
    if dry_run:
        print("\n🔍 DRY RUN - No files will be deleted")
    else:
        print("\n🗑️  DELETING FILES...")
    
    deleted_count = 0
    failed = []
    
    for file in files:
        try:
            size = file.stat().st_size
            size_kb = size / 1024
            
            if dry_run:
                print(f"   Would delete: {file} ({size_kb:.1f} KB)")
            else:
                file.unlink()
                print(f"   ✅ Deleted: {file} ({size_kb:.1f} KB)")
                logger.info(f"Deleted: {file}")
                deleted_count += 1
        
        except Exception as e:
            failed.append((file, str(e)))
            print(f"   ❌ Failed: {file} - {e}")
    
    return deleted_count, failed


def main():
    """Main cleanup function"""
    print("=" * 70)
    print("OLD FILES CLEANUP")
    print("=" * 70)
    print("\n⚠️  This will delete old JSON files after migration")
    print("   Only run this after 7+ days of verified bot operation!")
    
    # Check database age
    if not check_database_age():
        print("\n❌ Cleanup aborted - database too new")
        print("   Wait at least 7 days after migration")
        return 1
    
    # List files
    print("\n📋 Finding files to delete...")
    files = list_files_to_delete()
    
    if not files:
        print("✅ No old files found - nothing to cleanup!")
        return 0
    
    print(f"\nFound {len(files)} files:")
    for f in files:
        size_kb = f.stat().st_size / 1024
        print(f"   • {f} ({size_kb:.1f} KB)")
    
    # Calculate space
    total_size = calculate_space_freed(files)
    total_kb = total_size / 1024
    print(f"\n💾 Total space to free: {total_kb:.1f} KB")
    
    # Dry run first
    print("\n" + "=" * 70)
    delete_files(files, dry_run=True)
    print("=" * 70)
    
    # Confirm deletion
    print("\n⚠️  Are you sure you want to delete these files?")
    print("   This action CANNOT be undone!")
    response = input("\nType 'DELETE' to confirm: ")
    
    if response != 'DELETE':
        print("\n✅ Cleanup cancelled - no files deleted")
        return 0
    
    # Actually delete
    print("\n" + "=" * 70)
    deleted_count, failed = delete_files(files, dry_run=False)
    print("=" * 70)
    
    # Summary
    print(f"\n✅ Deleted {deleted_count} files ({total_kb:.1f} KB freed)")
    
    if failed:
        print(f"\n⚠️  {len(failed)} files failed to delete:")
        for file, error in failed:
            print(f"   • {file}: {error}")
    
    print("\n🎉 Cleanup complete!")
    print(f"📝 Log file: logs/cleanup.log")
    
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
