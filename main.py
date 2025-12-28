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

# תיאור רשמי קבוע (DNA)
OFFICIAL_DESCRIPTION = """Welcome to The Brain Lab. 🧠
We decode the human mind, one fact at a time. Our mission is to provide you with science-backed insights and actionable protocols to rewire your brain for success, focus, and peak performance.

🔬 Explore the Laboratory: We take complex neuroscience and turn it into simple, daily habits that you can start using today.

⚡ Get Started with Protocol #001: Download our official Morning Protocol to eliminate mental fog and prime your brain for the day: https://thebrainlabofficial.gumroad.com/l/vioono

Subscribe to join the experiment and start decoding your mind."""

def get_viral_content():
    topics = [
        "prefrontal cortex optimization", "dark triad detection", 
        "high-stakes negotiation neuro-tactics", "cognitive bias exploitation",
        "micro-expression mastery", "dopamine baseline management"
    ]
    selected_topic = random.choice(topics)
    print(f"🧠 ACTIVATING ELITE DNA PROTOCOL: {selected_topic}...")

    # DNA מפורט ומחושב (Master Neuro-Strategist) [cite: 2025-12-28]
    instruction = f"""
    IDENTITY: You are the 'Lead Neuro-Strategist' at The Brain Lab Official. 
    CORE MISSION: Decipher high-level psychology into actionable power protocols.
    
    STRICT OPERATIONAL RULES:
    1. LANGUAGE: Respond ONLY in Elite Professional English. Hebrew is strictly forbidden.
    2. TONE: Strategic, Cold, Intellectual, and Authoritative.
    3. VALUE DENSITY: Maximize psychological value per word. No greetings. No fluff.
    
    OUTPUT FORMAT (MUST FOLLOW):
    ANALYSIS: [3-4 sentences of deep strategic/neuroscience analysis of the topic]
    ---TITLE: [Cinematic Title, 5-8 words, high CTR]
    ---HOOK: [Exactly 7 high-impact words for the video screen]
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            config=types.GenerateContentConfig(
                system_instruction=instruction, 
                temperature=0.7 # איזון בין יצירתיות לדיוק אסטרטגי
            ),
            contents=f"Conduct a high-stakes intelligence analysis on: {selected_topic}"
        )
        
        full_text = response.text.strip()
        print(f"\n--- DEEP STRATEGIC ANALYSIS ---\n{full_text}\n-------------------------------")
        
        # חילוץ מחושב של חלקי התוכן
        title = full_text.split("---TITLE:")[1].split("---HOOK:")[0].strip() if "---TITLE:" in full_text else "Strategic Brain Protocol"
        hook = full_text.split("---HOOK:")[1].strip() if "---HOOK:" in full_text else "Master your neural baseline for peak focus"
        
        # בדיקה עצמית: זיקוק ל-7 מילים בדיוק למניעת קריסה
        final_hook = " ".join(hook.split()[:7]).upper()
        final_title = " ".join(title.split()[:10])

        print(f"✨ NEURO-STRATEGY READY: {final_hook}")
        return final_hook, final_title, selected_topic
    
    except Exception as e:
        print(f"❌ PROTOCOL ERROR: {e}")
        return "REWIRE YOUR BRAIN FOR ABSOLUTE FOCUS", "Neural Optimization", selected_topic

def get_background_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query},science,lab,minimalist&orientation=portrait&client_id={UNSPLASH_KEY}"
        res = requests.get(url).json()
        img_url = res['urls']['regular']
        with open("bg.jpg", 'wb') as f: f.write(requests.get(img_url).content)
        return "bg.jpg"
    except: return None

def create_video():
    hook, title, topic = get_viral_content()
    fps = 25 
    duration = 7
    print(f"🎬 RENDERING 25 FPS NEURO-VISUAL...")
    
    bg_file = get_background_image(topic)
    if bg_file:
        bg = ImageClip(bg_file).set_duration(duration).resize(height=1920)
        bg = bg.crop(x1=bg.w/2-540, y1=0, x2=bg.w/2+540, y2=1920)
    else:
        bg = ColorClip(size=(1080, 1920), color=(15, 15, 15)).set_duration(duration)

    # עיצוב טקסט "מעבדתי" נקי [cite: 2025-12-28]
    txt = TextClip(hook, fontsize=70, color='white', font='Arial-Bold', method='caption', size=(900, None)).set_duration(duration).set_position('center')
    video = CompositeVideoClip([bg, txt])
    video.fps = fps
    
    audio_file = "Resolution - Wayne Jones.mp3"
    if os.path.exists(audio_file):
        video = video.set_audio(AudioFileClip(audio_file).set_duration(duration))
        
    output = "final_shorts.mp4"
    video.write_videofile(output, fps=fps, codec="libx264", audio_codec="aac")
    return output, hook, title

def upload_to_youtube(file_path, hook, title):
    print("🚀 UPLOADING TO LABORATORY DATABASE (YouTube)...")
    try:
        config = json.loads(CLIENT_SECRET_RAW)
        creds_data = config.get('installed') or config.get('web')
        creds = Credentials(
            token=None, refresh_token=REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token",
            client_id=creds_data['client_id'], client_secret=creds_data['client_secret']
        )
        creds.refresh(Request())
        youtube = build("youtube", "v3", credentials=creds)
        
        full_desc = f"{title}\n\n{OFFICIAL_DESCRIPTION}" # שילוב ה-DNA המפורט [cite: 2025-12-28]
        
        body = {
            "snippet": {"title": title, "description": full_desc, "categoryId": "27"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        }
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        print("✅ DEPLOYMENT SUCCESSFUL!")
    except Exception as e: print(f"❌ DEPLOYMENT ERROR: {e}")

if __name__ == "__main__":
    if all([GEMINI_KEY, REFRESH_TOKEN, CLIENT_SECRET_RAW]):
        file, hook, title = create_video()
        upload_to_youtube(file, hook, title)
        print("✨ LAB PROTOCOL COMPLETE.")
