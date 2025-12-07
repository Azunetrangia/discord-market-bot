"""
Flask Web Dashboard for Discord News Bot
Real-time monitoring and management interface
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from functools import wraps
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

from database import Database
from translation_cache import TranslationCache
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.getenv('DASHBOARD_SECRET_KEY', 'your-secret-key-change-in-production')

# Initialize database and cache
db = Database('data/news_bot.db')
cache = TranslationCache()  # No argument needed

# Load credentials from environment variables (fallback to defaults)
USERNAME = os.getenv('DASHBOARD_USERNAME', 'admin')
PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'admin123')

def check_auth(username, password):
    """Check if username/password combination is valid"""
    return username == USERNAME and password == PASSWORD

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return ('Could not verify your access level. '
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/')
@requires_auth
def index():
    """Dashboard homepage with statistics"""
    stats = db.get_statistics()
    cache_stats = cache.get_stats()
    
    # Calculate cache hit rate
    total_cache_calls = cache_stats['session_hits'] + cache_stats['session_misses']
    cache_hit_rate = (cache_stats['session_hits'] / total_cache_calls * 100) if total_cache_calls > 0 else 0
    
    # Get cache size from cache stats or database
    cache_entries = cache_stats.get('total_entries', stats.get('cache', {}).get('total_entries', 0))
    
    # Calculate database size
    import os
    db_path = 'data/news_bot.db'
    db_size_mb = round(os.path.getsize(db_path) / (1024 * 1024), 2) if os.path.exists(db_path) else 0
    
    return render_template('index.html',
        guilds=stats['total_guilds'],
        feeds=stats['total_rss_feeds'],
        articles=stats['total_articles'],
        cache_entries=cache_entries,
        cache_hit_rate=round(cache_hit_rate, 1),
        articles_by_source=stats['articles_by_source'],
        db_size_mb=db_size_mb
    )


@app.route('/guilds')
@requires_auth
def guilds():
    """List all guild configurations"""
    guild_configs = db.get_all_guild_configs()
    return render_template('guilds.html', guilds=guild_configs)


@app.route('/feeds')
@requires_auth
def feeds():
    """Manage RSS feeds"""
    all_feeds = db.get_all_rss_feeds()
    return render_template('feeds.html', feeds=all_feeds)


@app.route('/feeds/add', methods=['POST'])
@requires_auth
def add_feed():
    """Add new RSS feed"""
    guild_id = request.form.get('guild_id', type=int)
    url = request.form.get('url')
    source_name = request.form.get('source_name')
    
    if not all([guild_id, url, source_name]):
        flash('All fields are required', 'error')
        return redirect(url_for('feeds'))
    
    try:
        # Use channel_id = 0 as placeholder, will be configured in bot
        db.add_rss_feed(guild_id, source_name, url, 0)
        flash(f'RSS feed "{source_name}" added successfully', 'success')
    except Exception as e:
        flash(f'Error adding feed: {str(e)}', 'error')
    
    return redirect(url_for('feeds'))


@app.route('/feeds/toggle/<int:feed_id>', methods=['POST'])
@requires_auth
def toggle_feed(feed_id):
    """Enable/disable RSS feed"""
    try:
        # Get current feed status
        with db.connect() as conn:
            cursor = conn.execute('SELECT enabled FROM rss_feeds WHERE id = ?', (feed_id,))
            row = cursor.fetchone()
            if row:
                new_status = not bool(row['enabled'])
                conn.execute('UPDATE rss_feeds SET enabled = ? WHERE id = ?', (new_status, feed_id))
                flash(f'Feed {"enabled" if new_status else "disabled"} successfully', 'success')
            else:
                flash('Feed not found', 'error')
    except Exception as e:
        flash(f'Error toggling feed: {str(e)}', 'error')
    
    return redirect(url_for('feeds'))


@app.route('/feeds/delete/<int:feed_id>', methods=['POST'])
@requires_auth
def delete_feed(feed_id):
    """Delete RSS feed"""
    try:
        db.delete_rss_feed(feed_id)
        flash('Feed deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting feed: {str(e)}', 'error')
    
    return redirect(url_for('feeds'))


@app.route('/articles')
@requires_auth
def articles():
    """View recent articles"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page
    
    with db.connect() as conn:
        cursor = conn.execute('''
            SELECT source, article_hash, posted_at
            FROM posted_articles
            ORDER BY posted_at DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        articles_list = cursor.fetchall()
        
        # Get total count for pagination
        cursor = conn.execute('SELECT COUNT(*) FROM posted_articles')
        total = cursor.fetchone()[0]
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('articles.html',
        articles=articles_list,
        page=page,
        total_pages=total_pages,
        total=total
    )


@app.route('/api/stats')
@requires_auth
def api_stats():
    """API endpoint for real-time stats (for AJAX updates)"""
    stats = db.get_statistics()
    cache_stats = cache.get_stats()
    
    total_cache_calls = cache_stats['session_hits'] + cache_stats['session_misses']
    cache_hit_rate = (cache_stats['session_hits'] / total_cache_calls * 100) if total_cache_calls > 0 else 0
    
    # Calculate database size
    import os
    db_path = 'data/news_bot.db'
    db_size_mb = round(os.path.getsize(db_path) / (1024 * 1024), 2) if os.path.exists(db_path) else 0
    
    # Get cache entries
    cache_entries = cache_stats.get('total_entries', stats.get('cache', {}).get('total_entries', 0))
    
    return jsonify({
        'guilds': stats['total_guilds'],
        'feeds': stats['total_rss_feeds'],
        'articles': stats['total_articles'],
        'cache_entries': cache_entries,
        'cache_hit_rate': round(cache_hit_rate, 1),
        'db_size_mb': db_size_mb,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/cache')
@requires_auth
def cache_view():
    """View translation cache statistics"""
    cache_stats = cache.get_stats()
    
    # Get sample cached translations
    with db.connect() as conn:
        cursor = conn.execute('''
            SELECT text_hash, 
                   substr(translated_text, 1, 100) as preview,
                   created_at,
                   use_count
            FROM translation_cache
            ORDER BY use_count DESC
            LIMIT 20
        ''')
        cached_items = cursor.fetchall()
    
    return render_template('cache.html',
        cache_stats=cache_stats,
        cached_items=cached_items
    )


@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        with db.connect() as conn:
            conn.execute('SELECT 1')
        
        # Get basic stats
        guilds = db.get_all_guild_configs()
        feeds = db.get_all_rss_feeds()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'guilds': len(guilds),
            'feeds': len([f for f in feeds if f.get('enabled', False)])
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 503


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Discord Bot Dashboard Starting...")
    print("=" * 60)
    print(f"📊 Dashboard URL: http://localhost:5000")
    print(f"👤 Username: {USERNAME}")
    print(f"🔑 Password: {PASSWORD}")
    print(f"🏥 Health Check: http://localhost:5000/health")
    print("=" * 60)
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
