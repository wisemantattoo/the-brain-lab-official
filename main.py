import os
import json
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip

# ייבוא מהמודלים שלנו [cite: 2025-12-27]
from modules.config import SECRETS, GUMROAD_LINK, OFFICIAL_DESCRIPTION
from modules.ai_brain import get_viral_content

def get_background_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query},minimalist,cinematic&orientation=portrait&client_id={SECRETS['UNSPLASH_KEY']}"
        res = requests.get(url).json()
        with open("bg.jpg", 'wb') as f: f.write(requests.get(res['urls']['regular']).content)
        return "bg.jpg"
    except: return None

def create_video():
    insight, title, topic = get_viral_content() # נקרא כעת מהמודול
    fps = 25 # מוגדר לפי דרישת המשתמש [cite: 2025-12-23]
    duration = 8 
    print(f"🎬 RENDERING V1.1 ACCESSIBLE UNIT...")
    
    bg_file = get_background_image(topic)
    bg = ImageClip(bg_file).set_duration(duration).resize(height=1920).crop(x1=0, y1=0, x2=1080, y2=1920) if bg_file else ColorClip(size=(1080, 1920), color=(15, 15, 15)).set_duration(duration)
    txt = TextClip(insight, fontsize=65, color='white', font='Arial-Bold', method='caption', size=(950, None)).set_duration(duration).set_position('center')
    
    video = CompositeVideoClip([bg, txt])
    video.fps = fps
    if os.path.exists("Resolution - Wayne Jones.mp3"):
        video = video.set_audio(AudioFileClip("Resolution - Wayne Jones.mp3").set_duration(duration))
        
    video.write_videofile("final_shorts.mp4", fps=fps, codec="libx264", audio_codec="aac")
    return "final_shorts.mp4", insight, title

def upload_to_youtube(file_path, insight, title):
    print("🚀 DEPLOYING TO YOUTUBE...")
    try:
        config = json.loads(SECRETS["CLIENT_SECRET_RAW"])
        creds_data = config.get('installed') or config.get('web')
        creds = Credentials(token=None, refresh_token=SECRETS["REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token", client_id=creds_data['client_id'], client_secret=creds_data['client_secret'])
        creds.refresh(Request())
        youtube = build("youtube", "v3", credentials=creds)
        
        # העלאה עם תיאור רשמי
        response = youtube.videos().insert(part="snippet,status", body={"snippet": {"title": title, "description": f"{title}\n\n{OFFICIAL_DESCRIPTION}", "categoryId": "27"}, "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}, media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)).execute()
        
        # תגובה לחיצה (textDisplay) [cite: 2026-01-01]
        youtube.commentThreads().insert(part="snippet", body={"snippet": {"videoId": response['id'], "topLevelComment": {"snippet": {"textDisplay": f"⚡ Get Started with Protocol #001: Download our official Morning Protocol here: {GUMROAD_LINK}"}}}}).execute()
        print("💬 CLICKABLE COMMENT DEPLOYED.")
    except Exception as e: print(f"❌ DEPLOYMENT ERROR: {e}")

if __name__ == "__main__":
    if all([SECRETS["GEMINI_KEY"], SECRETS["REFRESH_TOKEN"], SECRETS["CLIENT_SECRET_RAW"]]):
        file, insight, title = create_video()
        upload_to_youtube(file, insight, title)
        print("✨ ACCESSIBLE DNA UNIT MISSION COMPLETE.")
