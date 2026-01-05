"""
סקריפט למשיכת כל הוידאואים מיוטיוב ושמירה ב-database.
להרצה: python3 sync_youtube.py
"""

from googleapiclient.discovery import build
from modules.database import init_database, save_video, update_video_stats
import re

# ה-API Key הציבורי של YouTube (לא צריך OAuth לקריאה!)
YOUTUBE_API_KEY = "AIzaSyAa8yW_M1g_rkDdKQ8GkZd4G6dOqB9vu9M"  # זה key ציבורי לדוגמה
CHANNEL_ID = "UC1d1tnZCzVEc2AJJowHh3bw"  # ה-Channel ID שלך

def extract_hook_from_title(title):
    """
    מנסה לחלץ את ה-Hook מהכותרת.
    לדוגמה: "THE NEGATIVE WEIGHT: Secret Tactic..." → "THE NEGATIVE WEIGHT"
    """
    # חיפוש של "THE [משהו]:" או עד הנקודתיים הראשונות
    match = re.match(r'^(THE [^:]+)', title, re.IGNORECASE)
    if match:
        return match.group(1).strip().upper()
    
    # אם אין נקודתיים, קח את 3-5 המילים הראשונות
    words = title.split()
    if len(words) >= 3:
        return ' '.join(words[:min(5, len(words))]).upper()
    
    return title[:50].upper()  # fallback


def identify_domain_from_text(text):
    """מזהה domain על בסיס מילות מפתח"""
    text_lower = text.lower()
    
    domain_keywords = {
        "Neuroscience": ["brain", "neuroscience", "pupil", "dopamine", "neural", "cognitive"],
        "Body Language": ["eye", "gaze", "body", "neck", "gesture", "flex", "posture"],
        "Dark Psychology": ["manipulation", "fbi", "interrogation", "detect", "lie", "deception"],
        "Social Psychology": ["social", "influence", "persuasion", "cialdini", "conformity"],
        "Vulnerability": ["vulnerability", "brown", "authentic", "boundary", "reveal"],
        "Cognitive Bias": ["bias", "kahneman", "thinking", "glitch", "error", "fallacy"],
        "Behavioral Economics": ["behavioral", "economics", "nudge", "choice", "decision"],
        "Peak Performance": ["performance", "focus", "flow", "habit", "productivity"]
    }
    
    for domain, keywords in domain_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return domain
    
    return "General Psychology"


def sync_youtube_to_database():
    """
    משיכת כל הוידאואים מיוטיוב ושמירה ב-database.
    """
    print("🔄 Starting YouTube sync...")
    
    # אתחול database
    init_database()
    
    try:
        # בניית YouTube API client (ללא אימות!)
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # משיכת כל הוידאואים מהערוץ
        print(f"📺 Fetching videos from channel: {CHANNEL_ID}")
        
        request = youtube.search().list(
            part="id,snippet",
            channelId=CHANNEL_ID,
            maxResults=50,  # מקסימום 50 וידאואים
            order="date",
            type="video"
        )
        
        response = request.execute()
        
        if not response.get('items'):
            print("❌ No videos found on channel!")
            return
        
        print(f"✅ Found {len(response['items'])} videos")
        
        # עיבוד כל וידאו
        for item in response['items']:
            video_id = item['id']['videoId']
            snippet = item['snippet']
            title = snippet['title']
            description = snippet.get('description', '')
            
            # חילוץ hook ו-domain
            hook = extract_hook_from_title(title)
            domain = identify_domain_from_text(title + " " + description)
            
            # חילוץ guide מהתיאור (2-3 משפטים ראשונים)
            guide_sentences = description.split('.')[:2]
            guide = '. '.join(guide_sentences).strip()
            if not guide:
                guide = "No guide available"
            
            print(f"\n📹 Processing: {title}")
            print(f"   Hook: {hook}")
            print(f"   Domain: {domain}")
            
            # שמירה ב-database
            save_video(video_id, hook, title, guide, domain)
            
            # משיכת סטטיסטיקות
            stats_request = youtube.videos().list(
                part="statistics",
                id=video_id
            )
            stats_response = stats_request.execute()
            
            if stats_response['items']:
                stats = stats_response['items'][0]['statistics']
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))
                comments = int(stats.get('commentCount', 0))
                
                print(f"   📊 Views: {views}, Likes: {likes}, Comments: {comments}")
                
                # עדכון סטטיסטיקות
                update_video_stats(video_id, views, likes, comments)
        
        print("\n" + "="*50)
        print("✅ Sync completed successfully!")
        print(f"📊 Total videos synced: {len(response['items'])}")
        print("="*50)
        print("\n💡 Now refresh your dashboard to see the data!")
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🧠 The Brain Lab - YouTube Sync Tool")
    print("="*50)
    sync_youtube_to_database()
