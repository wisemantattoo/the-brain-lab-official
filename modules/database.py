import sqlite3
import os
from datetime import datetime

DB_PATH = "brain_lab.db"

def init_database():
    """
    יוצר את מבנה הדאטה בייס אם הוא לא קיים.
    קורה פעם אחת בהתחלה.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # טבלת וידאואים ראשית
    c.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT UNIQUE NOT NULL,
            hook TEXT NOT NULL,
            title TEXT NOT NULL,
            guide TEXT,
            domain TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # טבלת ביצועים היסטורית (לגרפים לאורך זמן)
    c.execute('''
        CREATE TABLE IF NOT EXISTS performance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            views INTEGER,
            likes INTEGER,
            comments INTEGER,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos(video_id)
        )
    ''')
    
    # טבלת insights אוטומטיים
    c.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            insight_type TEXT,
            insight_text TEXT,
            confidence_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")


def save_video(video_id, hook, title, guide, domain):
    """
    שומר וידאו חדש שנוצר.
    נקרא אוטומטית אחרי העלאה ליוטיוב.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO videos (video_id, hook, title, guide, domain, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (video_id, hook, title, guide, domain, datetime.now()))
        
        conn.commit()
        conn.close()
        print(f"✅ Video saved to database: {video_id}")
        return True
        
    except sqlite3.IntegrityError:
        print(f"⚠️ Video {video_id} already exists in database")
        return False
    except Exception as e:
        print(f"❌ Database save error: {e}")
        return False


def update_video_stats(video_id, views=None, likes=None, comments=None):
    """
    מעדכן סטטיסטיקות של וידאו.
    יכול להיקרא ידנית או אוטומטית.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # עדכון הטבלה הראשית
        updates = []
        params = []
        
        if views is not None:
            updates.append("views = ?")
            params.append(views)
        if likes is not None:
            updates.append("likes = ?")
            params.append(likes)
        if comments is not None:
            updates.append("comments = ?")
            params.append(comments)
        
        updates.append("last_updated = ?")
        params.append(datetime.now())
        params.append(video_id)
        
        query = f"UPDATE videos SET {', '.join(updates)} WHERE video_id = ?"
        c.execute(query, params)
        
        # שמירת snapshot היסטורי
        if views is not None:
            c.execute('''
                INSERT INTO performance_history (video_id, views, likes, comments)
                VALUES (?, ?, ?, ?)
            ''', (video_id, views, likes or 0, comments or 0))
        
        conn.commit()
        conn.close()
        print(f"✅ Stats updated for {video_id}: {views} views")
        return True
        
    except Exception as e:
        print(f"❌ Stats update error: {e}")
        return False


def get_all_videos():
    """
    מחזיר רשימה של כל הוידאואים.
    משמש לדשבורד.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            SELECT video_id, hook, title, domain, views, likes, comments, created_at
            FROM videos
            ORDER BY created_at DESC
        ''')
        
        videos = c.fetchall()
        conn.close()
        
        return [{
            'video_id': v[0],
            'hook': v[1],
            'title': v[2],
            'domain': v[3],
            'views': v[4],
            'likes': v[5],
            'comments': v[6],
            'created_at': v[7]
        } for v in videos]
        
    except Exception as e:
        print(f"❌ Error fetching videos: {e}")
        return []


def get_top_performers(limit=10):
    """
    מחזיר את הוידאואים המצליחים ביותר לפי views.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            SELECT video_id, hook, title, domain, views, likes
            FROM videos
            WHERE views > 0
            ORDER BY views DESC
            LIMIT ?
        ''', (limit,))
        
        videos = c.fetchall()
        conn.close()
        
        return [{
            'video_id': v[0],
            'hook': v[1],
            'title': v[2],
            'domain': v[3],
            'views': v[4],
            'likes': v[5]
        } for v in videos]
        
    except Exception as e:
        print(f"❌ Error fetching top performers: {e}")
        return []


def get_domain_performance():
    """
    מחזיר ביצועים לפי domain/נושא.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            SELECT 
                domain,
                COUNT(*) as video_count,
                AVG(views) as avg_views,
                MAX(views) as max_views,
                SUM(views) as total_views
            FROM videos
            WHERE domain IS NOT NULL
            GROUP BY domain
            ORDER BY avg_views DESC
        ''')
        
        domains = c.fetchall()
        conn.close()
        
        return [{
            'domain': d[0],
            'video_count': d[1],
            'avg_views': round(d[2], 1),
            'max_views': d[3],
            'total_views': d[4]
        } for d in domains]
        
    except Exception as e:
        print(f"❌ Error analyzing domains: {e}")
        return []


def get_statistics():
    """
    מחזיר סטטיסטיקות כלליות למסך הבית.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # סה"כ וידאואים
        c.execute("SELECT COUNT(*) FROM videos")
        total_videos = c.fetchone()[0]
        
        # סה"כ צפיות
        c.execute("SELECT SUM(views) FROM videos")
        total_views = c.fetchone()[0] or 0
        
        # ממוצע צפיות
        c.execute("SELECT AVG(views) FROM videos WHERE views > 0")
        avg_views = c.fetchone()[0] or 0
        
        # הכי טוב
        c.execute('''
            SELECT hook, views FROM videos 
            WHERE views = (SELECT MAX(views) FROM videos)
            LIMIT 1
        ''')
        best = c.fetchone()
        
        conn.close()
        
        return {
            'total_videos': total_videos,
            'total_views': int(total_views),
            'avg_views': round(avg_views, 1),
            'best_performer': {
                'hook': best[0] if best else 'N/A',
                'views': best[1] if best else 0
            }
        }
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        return {
            'total_videos': 0,
            'total_views': 0,
            'avg_views': 0,
            'best_performer': {'hook': 'N/A', 'views': 0}
        }


def get_performance_timeline():
    """
    מחזיר דאטה לגרף צפיות לאורך זמן.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as videos_posted,
                SUM(views) as total_views
            FROM videos
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        ''')
        
        timeline = c.fetchall()
        conn.close()
        
        return [{
            'date': t[0],
            'videos_posted': t[1],
            'total_views': t[2]
        } for t in timeline]
        
    except Exception as e:
        print(f"❌ Error getting timeline: {e}")
        return []


# אתחול אוטומטי כשהמודול נטען
if not os.path.exists(DB_PATH):
    print("🔧 Creating database for the first time...")
    init_database()
