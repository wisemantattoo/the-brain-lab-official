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

OFFICIAL_DESCRIPTION = """Welcome to The Brain Lab. 🧠
We decode high-stakes human intelligence into daily protocols. Our mission is to give you the psychological edge in career, social influence, and mental performance.

🔬 The Laboratory: We translate elite psychological tactics into simple habits you can use today.

⚡ Get Started with Protocol #001: Download our official Morning Protocol to prime your brain for peak focus: https://thebrainlabofficial.gumroad.com/l/vioono

Subscribe to join the experiment and start decoding your mind."""

def get_viral_content():
    # נושאי הליבה: שילוב של טקטיקה ויישום בחיים
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
    print(f"🧠 ACTIVATING FIELD PROFILER DNA (v1.1 Accessible): {selected_topic}...")

    # DNA 1.1: נגיש, פרקטי, ורלוונטי לכל אדם
    instruction = """
    IDENTITY: You are the Lead Strategist for 'The Brain Lab'. You leak psychological protocols used by elite operators, but you translate them for the EVERYDAY civilian.
    
    THE "ACCESSIBILITY" RULES:
    1. STREET SMART: Use tactical words like 'The Signal', 'The Power Move', but apply them to work, dating, and social life.
    2. THE "YOU" FACTOR: Explain why this helps the viewer GET something (money, status, respect, truth).
    3. ANTI-ACADEMIC: No science talk. Only raw, actionable intelligence.
    4. LANGUAGE: English ONLY. High impact, raw, and direct.
    
    FORMAT:
    ANALYSIS: [3 sentences explaining the tactic and how a normal person can use it at work or socially]
    ---TITLE: [Viral cinematic title]
    ---INSIGHT: [The tactical fact for the screen, 7-10 words maximum. Focus on the ACTION]
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            config=types.GenerateContentConfig(
                system_instruction=instruction, 
                temperature=0.7
            ),
            contents=f"Translate this protocol for a general audience: {selected_topic}"
        )
        
        full_text = response.text.strip()
        print(f"\n--- LAB ANALYSIS ---\n{full_text}\n-------------------")
        
        if "---TITLE:" in full_text and "---INSIGHT:" in full_text:
            title = full_text.split("---TITLE:")[1].split("---INSIGHT:")[0].strip()
            insight = full_text.split("---INSIGHT:")[1].strip()
        else:
            title = "Power Protocol"
            insight = "Use silence to gain the upper hand"
        
        final_insight = " ".join(insight.split()[:10]).upper()
        final_title = " ".join(title.split()[:10])

        return final_insight, final_title, selected_topic
    
    except Exception as e:
        print(f"❌ PROTOCOL ERROR: {e}")
        return "SILENCE IS POWER: WAIT 4 SECONDS", "Strategic Silence", selected_topic

def get_background_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query},minimalist,cinematic&orientation=portrait&client_id={UNSPLASH_KEY}"
        res = requests.get(url).json()
        img_url = res['urls']['regular']
        with open("bg.jpg", 'wb') as f: f.write(requests.get(img_url).content)
        return "bg.jpg"
    except: return None

def create_video():
    insight, title, topic = get_viral_content()
    fps = 25 
    duration = 8 
    print(f"🎬 RENDERING V1.1 UNIT...")
    
    bg_file = get_background_image(topic)
    if bg_file:
        bg = ImageClip(bg_file).set_duration(duration).resize(height=1920)
        bg = bg.crop(x1=bg.w/2-540, y1=0, x2=bg.w/2+540, y2=1920)
    else:
        bg = ColorClip(size=(1080, 1920), color=(15, 15, 15)).set_duration(duration)

    txt = TextClip(insight, fontsize=65, color='white', font='Arial-Bold', method='caption', size=(950, None)).set_duration(duration).set_position('center')
    video = CompositeVideoClip([bg, txt])
    video.fps = fps
    
    audio_file = "Resolution - Wayne Jones.mp3"
    if os.path.exists(audio_file):
        video = video.set_audio(AudioFileClip(audio_file).set_duration(duration))
        
    output = "final_shorts.mp4"
    video.write_videofile(output, fps=fps, codec="libx264", audio_codec="aac")
    return output, insight, title

def upload_to_youtube(file_path, insight, title):
    print("🚀 DEPLOYING TO YOUTUBE...")
    try:
        config = json.loads(CLIENT_SECRET_RAW)
        creds_data = config.get('installed') or config.get('web')
        creds = Credentials(
            token=None, refresh_token=REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token",
            client_id=creds_data['client_id'], client_secret=creds_data['client_secret']
        )
        creds.refresh(Request())
        youtube = build("youtube", "v3", credentials=creds)
        
        full_desc = f"{title}\n\n{OFFICIAL_DESCRIPTION}"
        
        body = {
            "snippet": {"title": title, "description": full_desc, "categoryId": "27"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        }
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        video_id = response['id'] 
        print(f"✅ UPLOAD SUCCESSFUL! ID: {video_id}")

        # התיקון הקריטי: textDisplay במקום textOriginal כדי שהלינק יהיה לחיץ
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textDisplay": f"⚡ Get Started with Protocol #001: Download our official Morning Protocol here: {GUMROAD_LINK}"
                        }
                    }
                }
            }
        ).execute()
        print("💬 CLICKABLE COMMENT DEPLOYED.")
    except Exception as e: print(f"❌ DEPLOYMENT ERROR: {e}")

if __name__ == "__main__":
    if all([GEMINI_KEY, REFRESH_TOKEN, CLIENT_SECRET_RAW]):
        file, insight, title = create_video()
        upload_to_youtube(file, insight, title)
        print("✨ ACCESSIBLE UNIT MISSION COMPLETE.")
