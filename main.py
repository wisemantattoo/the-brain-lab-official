import os
import json
import requests
import google.generativeai as genai
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# 1. חיבור ל-Secrets מה-GitHub (הכל כבר מוגדר אצלך)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
CLIENT_SECRET_RAW = os.environ.get("CLIENT_SECRET_JSON")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

# הקישור המעודכן שלך ל-GUMROAD
GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

# הגדרת Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_viral_content():
    print("🤖 מייצר תוכן ויראלי עם Gemini...")
    try:
        prompt = (
            "Create a viral 7-word hook about Social Intelligence for a YouTube Short. "
            "Also, write a short 2-line description. "
            "Format: Hook: [text] | Description: [text]. No emojis."
        )
        response = model.generate_content(prompt)
        raw = response.text.strip().split("|")
        hook = raw[0].replace("Hook:", "").strip().replace('"', '')
        desc = raw[1].replace("Description:", "").strip() if len(raw) > 1 else "Master your social skills."
        return hook, desc
    except Exception as e:
        print(f"⚠️ שגיאה ב-AI: {e}")
        return "Listening is the ultimate social power move", "Learn why master communicators focus on listening more than speaking."

def get_background_image():
    print("🖼️ מוריד תמונה מ-Unsplash...")
    try:
        url = f"https://api.unsplash.com/photos/random?query=minimalist,human,connection&orientation=portrait&client_id={UNSPLASH_KEY}"
        res = requests.get(url).json()
        img_url = res['urls']['regular']
        img_data = requests.get(img_url).content
        with open("bg.jpg", 'wb') as f:
            f.write(img_data)
        return "bg.jpg"
    except Exception as e:
        print(f"⚠️ שגיאה בהורדת תמונה: {e}")
        return None

def create_video():
    hook, desc = get_viral_content()
    fps = 25 # מוגדר ל-25 FPS כפי שביקשת
    duration = 6
    
    print(f"🎬 מרנדר וידאו ב-{fps} FPS...")
    
    # רקע: Unsplash או רקע כהה כגיבוי
    bg_file = get_background_image()
    if bg_file:
        bg = ImageClip(bg_file).set_duration(duration).resize(height=1920)
        bg = bg.crop(x1=bg.w/2-540, y1=0, x2=bg.w/2+540, y2=1920)
    else:
        bg = ColorClip(size=(1080, 1920), color=(20, 20, 20)).set_duration(duration)

    # טקסט מרכזי
    txt = TextClip(hook, fontsize=90, color='white', font='Arial-Bold',
