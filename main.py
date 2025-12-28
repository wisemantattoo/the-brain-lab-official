import os
import json
import requests
import random
from google import genai
from google.genai import types
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# 1. משיכת Secrets
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
CLIENT_SECRET_RAW = os.environ.get("CLIENT_SECRET_JSON")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")
TIKTOK_TOKEN = os.environ.get("TIKTOK_ACCESS_TOKEN")
GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

# הגדרת הקליינט החדש
client = genai.Client(api_key=GEMINI_KEY)

def get_viral_content():
    topics = ["body language", "social cues", "persuasion", "rapport", "leadership"]
    selected_topic = random.choice(topics)
    print(f"🧠 מפעיל מודל חשיבה (Gemini 2.0 Flash) על: {selected_topic}...")
    
    instruction = """
    אתה המוח האסטרטגי מאחורי 'The Brain Lab Official'. 
    לפני כתיבת התסריט, בצע ניתוח מהיר:
    1. מהו הטריגר הפסיכולוגי שיגרום לאנשים לעצור (Scroll-stopper)?
    2. איך להעביר ערך מקסימלי ב-7 מילים בלבד?
    3. כתוב את התוצאה בפורמט הבא בלבד: Hook: [טקסט] | Description: [טקסט]
    """
    
    try:
        # מעבר למודל פלאש לפתרון בעיית ה-Quota
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            config=types.GenerateContentConfig(
                system_instruction=instruction, 
                temperature=0.8
            ),
            contents=f"צור תוכן ויראלי עבור Shorts בנושא {selected_topic}"
        )
        
        raw = response.text.strip().split("|")
        hook = raw[0].replace("Hook:", "").strip().replace('"', '')
        desc = raw[1].replace("Description:", "").strip() if len(raw) > 1 else "Neuroscience and Social Intelligence."
        
        print(f"✨ מודל החשיבה הצליח! הוק נבחר: {hook}")
        return hook, desc, selected_topic
    
    except Exception as e:
        print(f"❌ שגיאה בחיבור למודל: {e}")
        fallbacks = [
            ("Your posture speaks before you do", "Master non-verbal authority."),
            ("Eyes tell what words try to hide", "Read emotions like a pro.")
        ]
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
    fps = 25 
    duration = 6
    print(f"🎬 מרנדר וידאו ב-{fps} FPS עבור The Brain Lab Official...")
    
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
        youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        print("✅ עלה ליוטיוב בהצלחה!")
    except Exception as e: print(f"❌ שגיאה ביוטיוב: {e}")

def upload_to_tiktok(file_path, title):
    print("📱 שולח לטיקטוק (The Brain Lab Official)...")
    if not TIKTOK_TOKEN:
        print("⚠️ חסר TIKTOK_ACCESS_TOKEN, מדלג על טיקטוק.")
        return
    print(f"✅ מערכת טיקטוק מוכנה להעלאה בעתיד עבור: {title}")

if __name__ == "__main__":
    if all([GEMINI_KEY, REFRESH_TOKEN, CLIENT_SECRET_RAW]):
        file, hook, desc = create_video()
        upload_to_youtube(file, hook, desc)
        upload_to_tiktok(file, hook)
        print("✨ ההרצה הושלמה ב-25fps!")
