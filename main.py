import os
import json
import time
import datetime
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, ImageClip, AudioFileClip

# --- הגדרות ---
GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"
VIDEO_DURATION = 5 # שניות
AUDIO_FILENAME = "Resolution - Wayne Jones.mp3" # השם המדויק שהעלית

# --- מאגר עובדות אינטליגנציה חברתית (מבוסס על הנתונים המצליחים ביותר) ---
facts_data = [
    ("Smart people tend to have fewer friends than the average person.", "smart alone"),
    ("If someone is laughing too much, even at stupid things, they are lonely deep inside.", "lonely person"),
    ("To know if someone is watching you, yawn. If they yawn too, they were watching.", "yawning eyes"),
    ("People who try to keep everyone happy often end up feeling the loneliest.", "lonely crowd"),
    ("Sarcasm is a sign of a healthy brain and high social intelligence.", "brain art"),
    ("Liars usually have more eye contact than truth-tellers to see if you believe them.", "eyes looking"),
    ("If a person speaks little but speaks fast, they are keeping a secret.", "secret whisper"),
    ("People are more honest when they are physically tired.", "tired evening"),
    ("The way you treat a waiter reveals a lot about your character.", "restaurant table"),
    ("Psychology says: Pretending not to care is the habit of someone who cares the most.", "sad face")
]

def get_daily_content():
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    index = day_of_year % len(facts_data)
    return facts_data[index]

def download_unsplash_image(keyword):
    access_key = os.environ.get('UNSPLASH_ACCESS_KEY')
    url = f"https://api.unsplash.com/photos/random?query={keyword}&orientation=portrait&client_id={access_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            img_data = requests.get(data['urls']['regular']).content
            with open('bg_image.jpg', 'wb') as h: h.write(img_data)
            return 'bg_image.jpg'
    except: return None

def create_video(fact, image_path):
    print(f"🎥 Creating video with music: {AUDIO_FILENAME}", flush=True)
    size = (1080, 1920)
    
    if image_path:
        bg = ImageClip(image_path).resize(height=1920).set_position('center').set_duration(VIDEO_DURATION)
    else:
        bg = ColorClip(size=size, color=(20, 20, 20), duration=VIDEO_DURATION)
    
    dim = ColorClip(size=size, color=(0,0,0), duration=VIDEO_DURATION).set_opacity(0.5)
    txt = TextClip(fact, fontsize=70, color='white', font='Liberation-Sans-Bold', size=(850, None), method='caption').set_position('center').set_duration(VIDEO_DURATION)
    
    video = CompositeVideoClip([bg, dim, txt], size=size)
    
    # הוספת מוזיקה מהקובץ הספציפי שלך
    try:
        if os.path.exists(AUDIO_FILENAME):
            audio = AudioFileClip(AUDIO_FILENAME).subclip(0, VIDEO_DURATION).volumex(0.2)
            video = video.set_audio(audio)
            print("🎵 Background music added successfully!", flush=True)
        else:
            print(f"⚠️ Music file {AUDIO_FILENAME} not found in repository.", flush=True)
    except Exception as e:
        print(f"⚠️ Audio processing error: {e}", flush=True)

    # 25 FPS לפי דרישת המשתמש
    video.write_videofile("short_video.mp4", fps=25, codec="libx264", audio_codec="aac")
    return "short_video.mp4"

def get_service():
    creds_json = json.loads(os.environ.get('CLIENT_SECRET_JSON'))
    config = next(iter(creds_json.values()))
    creds = Credentials(
        token=None, refresh_token=os.environ.get('YOUTUBE_REFRESH_TOKEN'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config['client_id'], client_secret=config['client_secret']
    )
    return build('youtube', 'v3', credentials=creds)

def post_comment(youtube, video_id):
    print("⏳ Waiting 20 seconds for YouTube processing...", flush=True)
    time.sleep(20)
    try:
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": f"🧠 STOP OPERATING ON AUTOPILOT. REWIRE YOUR CIRCUITRY. Get the Morning Protocol here: 👇 {GUMROAD_LINK}"
                        }
                    }
                }
            }
        ).execute()
        print("✅ Comment posted!", flush=True)
    except Exception as e:
        print(f"⚠️ Comment failed: {e}")

def upload_video(youtube, path, fact):
    title = "Social Intelligence: " + (fact[:40] + "..." if len(fact)>40 else fact)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": fact + "\n\n#Psychology #SocialIntelligence #Shorts", "categoryId": "27"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        },
        media_body=MediaFileUpload(path)
    )
    response = request.execute()
    v_id = response.get('id')
    print(f"✅ Uploaded! ID: {v_id}")
    post_comment(youtube, v_id)
    return v_id

if __name__ == "__main__":
    try:
        service = get_service()
        fact, keyword = get_daily_content()
        img = download_unsplash_image(keyword)
        video_file = create_video(fact, img)
        upload_video(service, video_file, fact)
    except Exception as e:
        print(f"❌ Error: {e}")
