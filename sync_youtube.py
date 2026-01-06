"""
🎬 YouTube Data Sync - The Brain Lab
מושך נתונים אמיתיים מהערוץ ביוטיוב ומעדכן את הדאשבורד
"""

import streamlit as st
from googleapiclient.discovery import build
from datetime import datetime
from modules.database import save_video, update_video_stats
import time

def get_youtube_service():
    """
    יוצר חיבור ל-YouTube API
    """
    try:
        API_KEY = st.secrets["YOUTUBE_API_KEY"]
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        return youtube
    except Exception as e:
        st.error(f"❌ Failed to connect to YouTube API: {e}")
        return None


def get_channel_videos(youtube, channel_id, max_results=50):
    """
    מושך את כל הסרטונים מהערוץ
    """
    try:
        videos = []
        
        # קבלת uploads playlist ID
        channel_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()
        
        if not channel_response['items']:
            st.warning("⚠️ No channel found with this ID")
            return []
        
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # משיכת כל הסרטונים
        next_page_token = None
        
        while True:
            playlist_response = youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
            
            for item in playlist_response['items']:
                video_id = item['contentDetails']['videoId']
                title = item['snippet']['title']
                published_at = item['snippet']['publishedAt']
                
                videos.append({
                    'video_id': video_id,
                    'title': title,
                    'published_at': published_at
                })
            
            next_page_token = playlist_response.get('nextPageToken')
            
            if not next_page_token or len(videos) >= max_results:
                break
        
        return videos[:max_results]
        
    except Exception as e:
        st.error(f"❌ Error fetching videos: {e}")
        return []


def get_video_statistics(youtube, video_ids):
    """
    מושך סטטיסטיקות של סרטונים (צפיות, לייקים, תגובות)
    """
    try:
        # YouTube API מאפשר עד 50 IDs בבקשה אחת
        stats = {}
        
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            
            response = youtube.videos().list(
                part='statistics,snippet',
                id=','.join(batch_ids)
            ).execute()
            
            for item in response['items']:
                video_id = item['id']
                statistics = item['statistics']
                snippet = item['snippet']
                
                stats[video_id] = {
                    'views': int(statistics.get('viewCount', 0)),
                    'likes': int(statistics.get('likeCount', 0)),
                    'comments': int(statistics.get('commentCount', 0)),
                    'description': snippet.get('description', ''),
                    'tags': snippet.get('tags', [])
                }
        
        return stats
        
    except Exception as e:
        st.error(f"❌ Error fetching statistics: {e}")
        return {}


def extract_metadata(title, description, tags):
    """
    מנסה לחלץ hook, domain מהכותרת/תיאור
    """
    # Hook = בדרך כלל החלק הראשון של הכותרת לפני |
    hook = title.split('|')[0].strip() if '|' in title else title[:50]
    
    # ניסיון לחלץ domain מהתגים או מהתיאור
    domain = None
    common_domains = ['זיכרון', 'למידה', 'מוח', 'פרודוקטיביות', 'נוירו', 'ריכוז']
    
    for tag in tags:
        for d in common_domains:
            if d in tag:
                domain = tag
                break
        if domain:
            break
    
    if not domain:
        for d in common_domains:
            if d in description or d in title:
                domain = d
                break
    
    return hook, domain or "כללי"


def sync_youtube_data():
    """
    פונקציה ראשית לסנכרון נתונים מיוטיוב
    """
    st.subheader("🔄 Syncing YouTube Data...")
    
    # חיבור ל-API
    youtube = get_youtube_service()
    if not youtube:
        return False
    
    try:
        CHANNEL_ID = st.secrets["CHANNEL_ID"]
    except:
        st.error("❌ CHANNEL_ID not found in secrets!")
        return False
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # שלב 1: משיכת רשימת סרטונים
    status_text.text("📺 Fetching videos from channel...")
    progress_bar.progress(20)
    
    videos = get_channel_videos(youtube, CHANNEL_ID, max_results=50)
    
    if not videos:
        st.warning("⚠️ No videos found in channel")
        return False
    
    st.success(f"✅ Found {len(videos)} videos")
    
    # שלב 2: משיכת סטטיסטיקות
    status_text.text("📊 Fetching video statistics...")
    progress_bar.progress(40)
    
    video_ids = [v['video_id'] for v in videos]
    stats = get_video_statistics(youtube, video_ids)
    
    # שלב 3: שמירה במסד נתונים
    status_text.text("💾 Saving to database...")
    progress_bar.progress(60)
    
    saved_count = 0
    updated_count = 0
    
    for video in videos:
        video_id = video['video_id']
        title = video['title']
        
        if video_id in stats:
            video_stats = stats[video_id]
            
            # חילוץ metadata
            hook, domain = extract_metadata(
                title, 
                video_stats['description'], 
                video_stats['tags']
            )
            
            # ניסיון לשמור סרטון חדש
            success = save_video(
                video_id=video_id,
                hook=hook,
                title=title,
                guide="Auto-synced from YouTube",
                domain=domain
            )
            
            if success:
                saved_count += 1
            
            # עדכון סטטיסטיקות
            update_video_stats(
                video_id=video_id,
                views=video_stats['views'],
                likes=video_stats['likes'],
                comments=video_stats['comments']
            )
            updated_count += 1
        
        progress_bar.progress(60 + int((40 * (updated_count / len(videos)))))
    
    progress_bar.progress(100)
    status_text.text("✅ Sync completed!")
    
    st.success(f"""
    🎉 **Sync Completed Successfully!**
    
    - 📺 Videos found: {len(videos)}
    - 💾 New videos saved: {saved_count}
    - 🔄 Videos updated: {updated_count}
    """)
    
    return True


def delete_demo_data():
    """
    מוחק את כל נתוני הדמו
    """
    try:
        import sqlite3
        
        DB_PATH = "brain_lab.db"
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM videos WHERE video_id LIKE 'DEMO_%'")
        demo_count = c.fetchone()[0]
        
        if demo_count == 0:
            st.info("✅ No demo data found!")
            return
        
        c.execute("DELETE FROM videos WHERE video_id LIKE 'DEMO_%'")
        c.execute("DELETE FROM performance_history WHERE video_id LIKE 'DEMO_%'")
        
        conn.commit()
        conn.close()
        
        st.success(f"✅ Deleted {demo_count} demo videos!")
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ Error: {e}")


if __name__ == "__main__":
    st.title("🎬 YouTube Data Sync")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Sync Now", type="primary", use_container_width=True):
            sync_youtube_data()
    
    with col2:
        if st.button("🗑️ Delete Demo Data", type="secondary", use_container_width=True):
            delete_demo_data()
            st.rerun()
