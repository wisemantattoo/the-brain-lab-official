import os
import random
import json
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

# --- הלינק החדש והמעודכן ---
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
    bg = ColorClip(size=(1080, 1920), color=(20, 20, 20), duration=5)
    txt = TextClip(fact, fontsize=70, color='white', font='Liberation-Sans', size=(900, None), method='caption')
    txt = txt.set_position('center').set_duration(5)
    final = CompositeVideoClip([bg, txt])
    final.write_videofile("short_video.mp4", fps=24, codec="libx264", audio=False)
    return "short_video.mp4"

def get_authenticated_service():
    print("🔑 Authenticating with YouTube...", flush=True)
    client_config = json.loads(os.environ.get('CLIENT_SECRET_JSON'))
    scopes = ['https://www.googleapis.com/auth/youtube.upload']
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(client_config, scopes)
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    
    auth_code = os.environ.get('YOUTUBE_CODE')
    flow.fetch_token(code=auth_code)
    
    # --- הדפסת טוקן הזהב בצורה ברורה ---
    print("\n" + "="*50, flush=True)
    print("👇👇👇 COPY THIS TOKEN 👇👇👇", flush=True)
    print(f"REFRESH_TOKEN={flow.credentials.refresh_token}", flush=True)
    print("👆👆👆 COPY THIS TOKEN 👆👆👆", flush=True)
    print("="*50 + "\n", flush=True)
    
    return build('youtube', 'v3', credentials=flow.credentials)

def upload_video(youtube, file_path, fact):
    # קיצור הכותרת אם היא ארוכה מדי
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
    print(f"🚀 Success! Video uploaded. ID: {response.get('id')}", flush=True)

if __name__ == "__main__":
    try:
        service = get_authenticated_service()
        current_fact = random.choice(facts)
        video_file = create_video(current_fact)
        upload_video(service, video_file, current_fact)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
