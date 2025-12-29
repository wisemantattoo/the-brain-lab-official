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

# שימוש במודל המנצח ששמור בזיכרון
client = genai.Client(api_key=GEMINI_KEY)

OFFICIAL_DESCRIPTION = """Welcome to The Brain Lab. 🧠
We decode the human mind, one fact at a time. Our mission is to provide you with science-backed insights and actionable protocols to rewire your brain for success, focus, and peak performance.

🔬 Explore the Laboratory: We take complex neuroscience and turn it into simple, daily habits that you can start using today.

⚡ Get Started with Protocol #001: Download our official Morning Protocol to eliminate mental fog and prime your brain for the day: https://thebrainlabofficial.gumroad.com/l/vioono

Subscribe to join the experiment and start decoding your mind."""

def get_viral_content():
    # 12 הפרוטוקולים של ה-DNA החדש (NLP, שב"כ, מנטליזם) [cite: 2025-12-28]
    topics = [
        "The Interrogator’s Silence: Truth extraction via 4-second pauses",
        "The 'Left Eye' Dominance: NLP command planting via gaze",
        "The False Choice Trap: Mentalist selection deception",
        "The Body Language Baseline: Lie detection in 20 seconds",
        "The Embedded Command: Hidden verbal directives",
        "The Throat Touch Leak: Instant stress and threat detection",
        "The Pacing & Leading Protocol: Hijacking conversation rhythm",
        "The Pupil Dilatation Read: Detecting visceral interest or lies",
        "The Misdirection Hack: Shifting focus to plant suggestions",
        "The Alter Ego Anchor: Biologically adopting a power identity",
        "The Feet Direction Power: Reading the room’s hidden exit intent",
        "The Compliance Trick: Small favors leading to total control"
    ]
    selected_topic = random.choice(topics)
    print(f"🧠 ACTIVATING FIELD PROFILER DNA: {selected_topic}...")

    # DNA מעודכן: אנטי-אקדמי, שפה טקטית מהשטח [cite: 2025-12-28]
    instruction = """
    IDENTITY: You are a Tactical Profiler for 'The Brain Lab'. You don't teach science; you leak intelligence protocols.
    
    THE "ANTI-ACADEMIC" RULES:
    1. STREET TACTICS: Never use words like 'Heuristics', 'Cognitive', or 'Neural'. Use words like 'The Signal', 'The Leak', 'The Trap', 'The Power Move'.
    2. THE 3-SECOND RULE: The insight must be something the viewer can do right now. 
    3. SHABAK VIBE: Every insight should feel like a secret technique used by interrogators or mentalists to exploit human psychology.
    4. LANGUAGE: English ONLY. High impact, raw, and cold.
    
    FORMAT:
    ANALYSIS: [3 sentences of raw tactical intelligence]
    ---TITLE: [Cinematic title for YouTube]
    ---INSIGHT: [The tactical fact for the screen, 7-10 words maximum]
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            config=types.GenerateContentConfig(
                system_instruction=instruction, 
                temperature=0.7
            ),
            contents=f"Extract a tactical psychological protocol from the topic: {selected_topic}"
        )
        
        full_text = response.text.strip()
        print(f"\n--- LAB ANALYSIS ---\n{full_text}\n-------------------")
        
        # חילוץ חכם של התובנה הטקטית (בדיוק לפי הקוד הקודם שעבד) [cite: 2025-12-28]
        if "---TITLE:" in full_text and "---INSIGHT:" in full_text:
            title = full_text.split("---TITLE:")[1].split("---INSIGHT:")[0].strip()
            insight = full_text.split("---INSIGHT:")[1].strip()
        else:
            title = "Tactical Protocol"
            insight = "Master the room with silent authority"
        
        # ניקוי וזיקוק לוידאו
        final_insight = " ".join(insight.split()[:10]).upper()
        final_title = " ".join(title.split()[:10])

        print(f"✨ TACTICAL INSIGHT READY: {final_insight}")
        return final_insight, final_title, selected_topic
    
    except Exception as e:
        print(f"❌ PROTOCOL ERROR: {e}")
        return "LOSS AVERSION: WE FEAR LOSS MORE THAN GAIN", "Brain Economics", selected_topic

def get_background_image(query):
    try:
        url = f"https://api.unsplash.com/photos/random?query={query},minimalist,intelligence&orientation=portrait&client_id={UNSPLASH_KEY}"
        res = requests.get(url).json()
        img_url = res['urls']['regular']
        with open("bg.jpg", 'wb') as f: f.write(requests.get(img_url).content)
        return "bg.jpg"
    except: return None

def create_video():
    insight, title, topic = get_viral_content()
    fps = 25 # מוגדר לפי דרישת המשתמש [cite: 2025-12-23]
    duration = 8 
    print(f"🎬 RENDERING TACTICAL SHORT...")
    
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
    print("🚀 UPLOADING PROTOCOL...")
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
        # מבצע העלאה ושומר את התשובה כדי לקבל את ה-ID של הסרטון [cite: 2025-12-28]
        response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        video_id = response['id'] 
        print(f"✅ MISSION SUCCESSFUL! Video ID: {video_id}")

        # הוספת תגובה אוטומטית עם הקישור ל-Gumroad [cite: 2025-12-28]
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": f"⚡ Get Started with Protocol #001: Download our official Morning Protocol here: {GUMROAD_LINK}"
                        }
                    }
                }
            }
        ).execute()
        print("💬 AUTOMATIC COMMENT DEPLOYED.")
        print("✅ MISSION SUCCESSFUL!")
    except Exception as e: print(f"❌ DEPLOYMENT ERROR: {e}")

if __name__ == "__main__":
    if all([GEMINI_KEY, REFRESH_TOKEN, CLIENT_SECRET_RAW]):
        file, insight, title = create_video()
        upload_to_youtube(file, insight, title)
        print("✨ TACTICAL UNIT COMPLETE.")
