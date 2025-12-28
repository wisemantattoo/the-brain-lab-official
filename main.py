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

client = genai.Client(api_key=GEMINI_KEY)

def get_viral_content():
    topics = ["dark psychology", "interrogation tactics", "social dominance", "manipulation detection", "high-stakes rapport"]
    selected_topic = random.choice(topics)
    print(f"🧠 מפעיל מודל DNA אסטרטגי על: {selected_topic}...")
    
    # הגדרת הזהות החדשה - The Brain Lab Elite [cite: 2025-12-28]
    instruction = """
    ROLE: You are the Lead Intelligence Analyst for 'The Brain Lab Official'. 
    EXPERT IN: Dark Psychology, Social Engineering, FBI Interrogation, and Neural-Influence.
    MISSION: Provide raw, high-density value that gives the viewer 'unfair power'.
    
    STRICT RULES:
    1. LANGUAGE: Respond ONLY in English.
    2. NO FLUFF: No greetings, no summaries, no "Here is your content".
    3. VALUE DENSITY: Every word must represent a psychological law or tactical advantage.
    4. HOOK LIMIT: Exactly 7 words. Use 'power words' only.
    
    STRUCTURE:
    ANALYSIS: [Deep tactical analysis of the behavior/strategy]
    ---HOOK: [High-value 7-word scroll-stopper]
    ---DESC: [Viral YouTube description + keywords]
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            config=types.GenerateContentConfig(
                system_instruction=instruction, 
                temperature=0.9 # העלאת היצירתיות לתוכן ויראלי
            ),
            contents=f"Execute a deep psychological strike on the topic: {selected_topic}"
        )
        
        full_text = response.text.strip()
        print(f"\n--- DNA STRATEGIC ANALYSIS ---\n{full_text}\n-----------------------------")
        
        # חילוץ ה-Hook המזוקק
        if "---HOOK:" in full_text:
            hook = full_text.split("---HOOK:")[1].split("---DESC:")[0].strip().replace('"', '')
        else:
            hook = "Master your mind before they do it"
            
        desc = full_text.split("---DESC:")[1].strip() if "---DESC:" in full_text else "Strategic Social Intelligence."
        
        # וידוא אורך למניעת קריסת הרינדור
        final_hook = " ".join(hook.split()[:8]) 
        
        print(f"✨ ערך מזוקק לוידאו: {final_hook}")
        return final_hook, desc, selected_topic
    
    except Exception as e:
        print(f"❌ שגיאה בחיבור למודל: {e}")
        return "Silent power is the strongest force", "Dark psychology secrets.", selected_topic

def get_background_image(query):
    try:
        # חיפוש תמונות "אפלות" ומקצועיות יותר
        url = f"https://api.unsplash.com/photos/random?query={query},cinematic,dark&orientation=portrait&client_id={UNSPLASH_KEY}"
        res = requests.get(url).json()
        img_url = res['urls']['regular']
        with open("bg.jpg", 'wb') as f: f.write(requests.get(img_url).content)
        return "bg.jpg"
    except: return None

def create_video():
    hook, desc, topic = get_viral_content()
    fps = 25 
    duration = 6
    print(f"🎬 מרנדר וידאו ב-{fps} FPS - The Brain Lab Production...")
    
    bg_file = get_background_image(topic)
    if bg_file:
        bg = ImageClip(bg_file).set_duration(duration).resize(height=1920)
        bg = bg.crop(x1=bg.w/2-540, y1=0, x2=bg.w/2+540, y2=1920)
    else:
        bg = ColorClip(size=(1080, 1920), color=(10, 10, 10)).set_duration(duration)

    # עיצוב טקסט נקי וחד [cite: 2025-12-28]
    txt = TextClip(hook.upper(), fontsize=75, color='white', font='Arial-Bold', method='caption', size=(950, None)).set_duration(duration).set_position('center')
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
            token=None, refresh_token=REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token",
            client_id=creds_data['client_id'], client_secret=creds_data['client_secret']
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
    print("📱 שולח לטיקטוק...")
    if not TIKTOK_TOKEN: return
    print(f"✅ מוכן לטיקטוק עבור: {title}")

if __name__ == "__main__":
    if all([GEMINI_KEY, REFRESH_TOKEN, CLIENT_SECRET_RAW]):
        file, hook, desc = create_video()
        upload_to_youtube(file, hook, desc)
        upload_to_tiktok(file, hook)
        print("✨ ההרצה הושלמה!")
