"""
🎬 Demo Data Generator for The Brain Lab Dashboard
מייצר נתונים לדוגמה כדי להציג את הדאשבורד
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = "brain_lab.db"

def create_demo_videos():
    """
    יוצר 15 סרטונים לדוגמה עם נתונים ריאליסטיים
    """
    
    # רשימת הוקים לדוגמה
    demo_hooks = [
        "למה המוח שלך שוכח שמות? 🧠",
        "הטריק שישנה את הזיכרון שלך לנצח",
        "5 דקות ביום = מוח של גאון",
        "איך לזכור 100 מילים בשעה אחת",
        "הסוד של אנשים עם IQ גבוה",
        "למה אתה לומד איטי? התשובה תדהים אותך",
        "הטכניקה שכל סטודנט חייב לדעת",
        "איך ללמוד לבחינה ב-24 שעות",
        "המדע מאחורי זיכרון פוטוגרפי",
        "3 הרגלים שהורסים את המוח שלך",
        "איך לשפר ריכוז ב-10 דקות",
        "הטריק של Einstein ללמידה מהירה",
        "למה אתה שוכח מה למדת אתמול?",
        "איך לזכור שמות של אנשים חדשים",
        "המדיטציה שמשפרת זיכרון ב-50%"
    ]
    
    # רשימת כותרות מפורטות
    demo_titles = [
        "למה המוח שלך שוכח שמות? המדע מאחורי הזיכרון | The Brain Lab",
        "הטריק הפסיכולוגי שישנה את הזיכרון שלך לנצח",
        "5 דקות ביום יהפכו אותך לגאון - מדע מוכח!",
        "איך לזכור 100 מילים בשעה אחת - טכניקת הארמון",
        "הסוד של אנשים עם IQ 140+ שאף אחד לא מספר לך",
        "למה אתה לומד איטי? התשובה תדהים אותך | מדע המוח",
        "הטכניקה שכל סטודנט צריך לדעת לפני הבחינה",
        "איך ללמוד לבחינה ב-24 שעות - המדריך המלא",
        "המדע מאחורי זיכרון פוטוגרפי - האם זה אפשרי?",
        "3 הרגלים יומיומיים שהורסים את המוח שלך",
        "איך לשפר ריכוז ב-10 דקות - טכניקות מוכחות",
        "הטריק של Einstein ללמידה מהירה שאף אחד לא מלמד",
        "למה אתה שוכח מה למדת אתמול? ואיך לתקן את זה",
        "איך לזכור שמות של אנשים חדשים בפעם הראשונה",
        "המדיטציה הפשוטה שמשפרת זיכרון ב-50% תוך שבוע"
    ]
    
    # רשימת דומיינים
    domains = [
        "זיכרון וריכוז",
        "טכניקות למידה",
        "מדע המוח",
        "פרודוקטיביות",
        "נוירו-סיינס"
    ]
    
    # רשימת guides לדוגמה
    demo_guides = [
        "מדריך מלא לשיפור הזיכרון",
        "טכניקות למידה מתקדמות",
        "מדע המוח למתחילים",
        "איך לשפר ריכוז",
        "הרגלים יומיומיים לשיפור המוח"
    ]
    
    # יצירת חיבור למסד נתונים
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # יצירת סרטונים לדוגמה
    print("🎬 Creating demo videos...")
    
    for i in range(15):
        video_id = f"DEMO_{i+1:03d}_{random.randint(1000, 9999)}"
        hook = demo_hooks[i]
        title = demo_titles[i]
        guide = random.choice(demo_guides)
        domain = random.choice(domains)
        
        # תאריך אקראי בחודש האחרון
        days_ago = random.randint(1, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        # נתוני צפיות ריאליסטיים
        # סרטונים ישנים יותר יקבלו יותר צפיות
        base_views = random.randint(500, 5000)
        views = int(base_views * (1 + (30 - days_ago) / 10))
        
        likes = int(views * random.uniform(0.03, 0.08))  # 3-8% likes
        comments = int(views * random.uniform(0.005, 0.02))  # 0.5-2% comments
        
        try:
            # הוספת הסרטון
            c.execute('''
                INSERT INTO videos (video_id, hook, title, guide, domain, created_at, views, likes, comments, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (video_id, hook, title, guide, domain, created_at, views, likes, comments, datetime.now()))
            
            # הוספת נתונים היסטוריים (כמה snapshots לאורך זמן)
            for j in range(3):
                history_days_ago = days_ago - (j * 3)
                if history_days_ago > 0:
                    history_date = datetime.now() - timedelta(days=history_days_ago)
                    history_views = int(views * (0.3 + (j * 0.3)))
                    history_likes = int(history_views * random.uniform(0.03, 0.08))
                    history_comments = int(history_views * random.uniform(0.005, 0.02))
                    
                    c.execute('''
                        INSERT INTO performance_history (video_id, views, likes, comments, recorded_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (video_id, history_views, history_likes, history_comments, history_date))
            
            print(f"✅ Added: {hook[:50]}... ({views} views)")
            
        except sqlite3.IntegrityError:
            print(f"⚠️ Video {video_id} already exists, skipping...")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Demo data created successfully!")
    print(f"📊 Total videos: 15")
    print(f"📈 Ready to view in dashboard!")


def check_if_demo_needed():
    """
    בודק אם יש צורך ליצור נתונים לדוגמה
    """
    if not os.path.exists(DB_PATH):
        return True
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM videos")
    count = c.fetchone()[0]
    
    conn.close()
    
    # אם אין סרטונים או יש פחות מ-5, ניצור דמו
    return count < 5


if __name__ == "__main__":
    print("🧠 The Brain Lab - Demo Data Generator")
    print("=" * 50)
    
    if check_if_demo_needed():
        print("📊 No data found. Creating demo data...")
        create_demo_videos()
    else:
        print("✅ Database already has data. Skipping demo creation.")
        print("💡 To recreate demo data, delete brain_lab.db and run again.")
