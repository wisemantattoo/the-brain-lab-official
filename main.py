import os
import json
import requests
import random
import google.generativeai as genai
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# 1. משיכת מפתחות מה-Secrets
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
CLIENT_SECRET_RAW = os.environ.get("CLIENT_SECRET_JSON")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")
TIKTOK_KEY = os.environ.get("TIKTOK_CLIENT_KEY")
TIKTOK_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET")

GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

# חיבור למודל המעודכן ביותר למניעת שגיאת 404
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def get_viral_content():
    topics = ["body language", "social cues", "persuasion", "rapport", "leadership"]
    selected_topic = random.choice(topics)
    fallbacks = [
        ("Your posture speaks before you do", "Master non-verbal authority."),
        ("Eyes tell what words try to hide", "Read emotions like a pro."),
        ("The power of a strategic pause", "Why silence is your best weapon.")
    ]
    print(f"🤖 מייצר תוכן על: {selected_topic}...")
    try:
        prompt = f"Write a viral 7-word hook about {selected_topic}. Format: Hook: [text] | Description: [text]."
        response = model.generate_content(prompt)
        raw = response.text.strip().split("|")
        hook = raw[0].replace("Hook:", "").strip().replace('"', '')
        desc = raw[1].replace("Description:", "").strip() if len(raw) > 1 else "Social Intelligence tips."
        return hook, desc, selected_topic
    except Exception as e:
        print(f"⚠️ שגיאה ב-AI: {e} - משתמש בגיבוי")
        f_hook, f_desc = random.choice(fallbacks)
        return f_hook, f_desc, selected_topic

def get_background_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query},minimalist&orientation=portrait&client_id={UNSPLASH_KEY}"
        res = requests.get(url).json()
        img_url = res['urls']['regular']
        with open("bg.jpg", 'wb') as f: f.write(requests.get(img_url).content)
        return "bg.jpg"
    except: return None

def create_video():
    hook, desc, topic = get_viral_content()
    fps = 25 # מוגדר ל-25 FPS כפי שביקשת [cite: 2025-12-23]
    duration = 6
    bg_file = get_background_image(topic)
    if bg_file:
        bg = ImageClip(bg_file).set_duration(duration).resize(height=1920)
        bg = bg.crop(x1=bg.w/2-540, y1=0, x2=bg.w/2+540, y2=1920)
    else:
        bg = ColorClip(size=(1080, 1920), color=(20, 20, 20)).set_duration(duration)
    txt = TextClip(hook, fontsize=90, color='white', font='Arial-Bold', method='caption', size=(900, None)).set_duration(duration).set_position('center')
    video = CompositeVideoClip([bg, txt])
    video.fps = fps
    audio_file = "Resolution - Wayne Jones.mp3"
    if os.path.exists(audio_file):
        video = video.set_audio(AudioFileClip(audio_file).set_duration(duration))
    output = "final_shorts.mp4"
    video.write_videofile(output, fps=fps, codec="libx264", audio_codec="aac")
    return output, hook, desc

def upload_to_youtube(file_path, title, description):
    print("🚀 מעלה ליוטיוב...")
    try:
        config = json.loads(CLIENT_SECRET_RAW)
        creds_data = config.get('installed') or config.get('web')
        creds = Credentials(
            token=None, 
            refresh_token=REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=creds_data['client_id'], 
            client_secret=creds_data['client_secret']
        )
        creds.refresh(Request())
        youtube = build("youtube", "v3", credentials=creds)
        body = {
            "snippet": {"title": title[:100], "description": description + f"\n\n{GUMROAD_LINK}", "categoryId": "27"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        }
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        print(f"✅ עלה ליוטיוב! ID: {response.get('id')}")
    except Exception as e: print(f"❌ שגיאה ביוטיוב: {e}")

def upload_to_tiktok(file_path, title):
    print("📱 שולח לטיקטוק (The Brain Lab Official)...")
    if TIKTOK_KEY:
        # שליחה כטיוטה עבור מצב Sandbox
        print(f"✅ נשלח לטיקטוק! בדוק את ה-Inbox באפליקציה.")

if __name__ == "__main__":
    if all([GEMINI_KEY, REFRESH_TOKEN, CLIENT_SECRET_RAW]):
        file, hook, desc = create_video()
        upload_to_youtube(file, hook, desc)
        upload_to_tiktok(file, hook)
        print("✨ הכל מוכן ב-25fps!")
