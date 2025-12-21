import os
import random
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

# --- הלינק שלך ---
GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

# רשימת העובדות
facts = [
    "Psychology says: Your brain does more creative work when you are tired.",
    "Smart people tend to have fewer friends than the average person.",
    "The way you dress is linked to your mood.",
    "Pretending not to care is the habit of someone who generally cares the most.",
    "The type of music you listen to affects the way you perceive the world."
]

def create_video(fact):
    print("🎥 Starting video creation...", flush=True)
    # יצירת רקע שחור
    bg = ColorClip(size=(1080, 1920), color=(20, 20, 20), duration=5)
    
    # יצירת הטקסט
    txt = TextClip(fact, fontsize=70, color='white', font='Liberation-Sans', size=(900, None), method='caption')
    txt = txt.set_position('center').set_duration(5)
    
    # חיבור לסרטון
    final = CompositeVideoClip([bg, txt])
    final.write_videofile("short_video.mp4", fps=24, codec="libx264", audio=False)
    print("✅ Video created successfully!", flush=True)
    return "short_video.mp4"

def get_authenticated_service():
    print("🔑 Authenticating with Refresh Token...", flush=True)
    
    # טעינת פרטי האפליקציה (Client ID & Secret)
    client_config = json.loads(os.environ.get('CLIENT_SECRET_JSON'))
    # חילוץ הפרטים מתוך המבנה של הקובץ (בין אם זה installed או web)
    config = next(iter(client_config.values()))
    
    # יצירת אישור כניסה באמצעות ה-Refresh Token
    creds = Credentials(
        token=None,
        refresh_token=os.environ.get('YOUTUBE_REFRESH_TOKEN'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config['client_id'],
        client_secret=config['client_secret']
    )
    
    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, file_path, fact):
    print("🚀 Starting upload...", flush=True)
    
    # קיצור כותרת אם היא ארוכה מדי (חובה ליוטיוב)
    base_title = fact.split(':')[0]
    if len(base_title) > 50:
        base_title = base_title[:50]
    
    title = f"Brain Fact: {base_title}... #TheBrainLab"
    
    description = (
        f"{fact}\n\n"
        f"🧠 STOP OPERATING ON AUTOPILOT. REWIRE YOUR CIRCUITRY.\n"
        f"Get our official Morning Protocol #001 here: 👇\n"
        f"{GUMROAD_LINK}\n\n"
        f"#Neuroscience #Mindset #Success #Shorts"
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "27"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(file_path)
    )
    response = request.execute()
    print(f"✅ Upload Successful! Video ID: {response.get('id')}", flush=True)

if __name__ == "__main__":
    try:
        service = get_authenticated_service()
        current_fact = random.choice(facts)
        video_file = create_video(current_fact)
        upload_video(service, video_file, current_fact)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
