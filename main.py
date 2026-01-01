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

# ייבוא מהכספת שלנו [cite: 2025-12-27]
from modules.config import SECRETS, GUMROAD_LINK, OFFICIAL_DESCRIPTION

client = genai.Client(api_key=SECRETS["GEMINI_KEY"])

def get_viral_content():
    topics = [
        "The 4-Second Silence: Dominating high-stakes negotiations",
        "The NLP Eye-Gaze: Planting suggestions in social settings",
        "The Choice Architecture: Getting an 'Easy Yes' at work",
        "The Baseline Method: Spotting lies in daily conversations",
        "The Hidden Command: Subliminal influence in meetings",
        "The Stress Leak: Reading a person's true intent instantly",
        "The Pacing Protocol: Hijacking the rhythm of any room",
        "The Visual Interest Read: Detecting attraction or boredom",
        "The Focus Misdirection: Moving attention like a pro mentalist",
        "The Power Identity: Biologically adopting high-status body language",
        "The Exit Intent: Reading feet to know when someone wants to leave",
        "The Compliance Ladder: Getting major favors through small 'Yes' moves"
    ]
    selected_topic = random.choice(topics)
    print(f"🧠 ACTIVATING ACCESSIBLE DNA: {selected_topic}...")

    instruction = """
    IDENTITY: You are the Lead Strategist for 'The Brain Lab'. You leak psychological protocols for the EVERYDAY civilian.
    THE "ACCESSIBILITY" RULES:
    1. STREET SMART: Apply tactics to work, dating, and social life.
    2. THE "YOU" FACTOR: Explain how this helps the viewer GET money, status, or respect.
    3. ANTI-ACADEMIC: No science talk. Actionable intelligence only.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            config=types.GenerateContentConfig(system_instruction=instruction, temperature=0.7),
            contents=f"Translate this protocol for a general audience: {selected_topic}"
        )
        full_text = response.text.strip()
        
        if "---TITLE:" in full_text and "---INSIGHT:" in full_text:
            title = full_text.split("---TITLE:")[1].split("---INSIGHT:")[0].strip()
            insight = full_text.split("---INSIGHT:")[1].strip()
        else:
            title = "Power Protocol"; insight = "Use silence to gain the upper hand"
        
        return " ".join(insight.split()[:10]).upper(), " ".join(title.split()[:10]), selected_topic
    except Exception as e:
        return "SILENCE IS POWER: WAIT 4 SECONDS", "Strategic Silence", selected_topic

def get_background_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query},minimalist,cinematic&orientation=portrait&client_id={SECRETS['UNSPLASH_KEY']}"
        res = requests.get(url).json()
        with open("bg.jpg", 'wb') as f: f.write(requests.get(res['urls']['regular']).content)
        return "bg.jpg"
    except: return None

def create_video():
    insight, title, topic = get_viral_content()
    fps = 25 # הגדרת משתמש [cite: 2025-12-23]
    duration = 8 
    print(f"🎬 RENDERING V1.1 UNIT...")
    
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
        
        response = youtube.videos().insert(part="snippet,status", body={"snippet": {"title": title, "description": f"{title}\n\n{OFFICIAL_DESCRIPTION}", "categoryId": "27"}, "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}, media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)).execute()
        
        # התיקון הקריטי ללינק לחיץ [cite: 2026-01-01]
        youtube.commentThreads().insert(part="snippet", body={"snippet": {"videoId": response['id'], "topLevelComment": {"snippet": {"textDisplay": f"⚡ Get Started with Protocol #001: Download our official Morning Protocol here: {GUMROAD_LINK}"}}}}).execute()
        print("💬 CLICKABLE COMMENT DEPLOYED.")
    except Exception as e: print(f"❌ DEPLOYMENT ERROR: {e}")

if __name__ == "__main__":
    if all([SECRETS["GEMINI_KEY"], SECRETS["REFRESH_TOKEN"], SECRETS["CLIENT_SECRET_RAW"]]):
        file, insight, title = create_video()
        upload_to_youtube(file, insight, title)
        print("✨ ACCESSIBLE UNIT MISSION COMPLETE.")
