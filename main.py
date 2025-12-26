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

# 1. הגדרות וחיבור ל-Secrets
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
CLIENT_SECRET_RAW = os.environ.get("CLIENT_SECRET_JSON")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")
TIKTOK_KEY = os.environ.get("TIKTOK_CLIENT_KEY")
TIKTOK_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET")

GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

# תיקון המודל לגרסה היציבה ביותר
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_viral_content():
    topics = [
        "body language secrets", "active listening", "emotional regulation", 
        "persuasion techniques", "building instant rapport", "social cues",
        "charismatic speaking", "conflict resolution", "empathy in leadership"
    ]
    selected_topic = random.choice(topics)
    
    # רשימת גיבוי אקראית למקרה שג'מיני נכשל - שלא יחזור על עצמו
    fallbacks = [
        ("Your posture speaks before you do", "Master the art of non-verbal authority."),
        ("Eyes tell what words try to hide", "How to read emotions like a pro."),
        ("The power of a strategic pause", "Why silence is often your best response."),
        ("Small talk leads to big doors", "Networking secrets for the socially smart."),
        ("Master the art of the subtle nod", "Show engagement without saying a word."),
        ("Mirrored movements build trust fast", "Use psychology to connect instantly.")
    ]
    
    print(f"🤖 מייצר תוכן חדש על: {selected_topic}...")
    try:
        prompt = (
            f"Write a unique, viral 7-word hook about {selected_topic} specifically. "
            "Make it punchy and surprising. Also, write a 2-line YouTube description. "
            "Format: Hook: [text] | Description: [text]. No emojis."
        )
        response = model.generate_content(prompt)
        raw = response.text.strip().split("|")
        hook = raw[0].replace("Hook:", "").strip().replace('"', '')
        desc = raw[1].replace("Description:", "").strip() if len(raw) > 1 else "Master your social skills."
        return hook, desc, selected_topic
    except Exception as e:
        print(f"⚠️ שגיאה ב-AI: {e} - משתמש בגיבוי אקראי למניעת כפילות")
        f_hook, f_desc = random.choice(fallbacks)
        return f_hook, f_desc, selected_topic

def get_background_image(query):
    print(f"🖼️ מוריד תמונה מ-Unsplash עבור: {query}")
    try:
        url = f"https://api.unsplash.com/photos/random?query={query},minimalist&orientation=portrait&client_id={UNSPLASH_KEY}"
        res = requests.get(url).json()
        img_url = res['urls']['regular']
        with open("bg.jpg", 'wb') as f:
            f.write(requests.get(img_url).content)
        return "bg.jpg"
    except:
        return None

def create_video():
    hook, desc, topic = get_viral_content()
    fps = 25 # שומרים על הקצב שלך
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
        audio = AudioFileClip(audio_file).set_duration(duration)
        video = video.set_audio(audio)

    output = "final_shorts.mp4"
    video.write_videofile(output, fps=fps, codec="libx264", audio_codec="aac")
    return output, hook, desc

def upload_to_youtube(file_path, title, description):
    print("🚀 מעלה ליוטיוב...")
    try:
        client_config = json.loads(CLIENT_SECRET_RAW)
        creds_data = client_config.get('installed') or client_config.get('web')
        creds = Credentials(token=None, refresh_token=REFRESH_TOKEN,
