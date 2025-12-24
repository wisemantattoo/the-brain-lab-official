import os
import json
import time
import datetime
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, ImageClip

# --- הלינק שלך ---
GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

# --- מאגר עובדות ממוקד: אינטליגנציה חברתית (התוכן שעובד הכי טוב) ---
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
    selected_fact, keyword = facts_data[index]
    return selected_fact, keyword

def download_unsplash_image(keyword):
    access_key = os.environ.get('UNSPLASH_ACCESS_KEY')
    url = f"https://api.unsplash.com/photos/random?query={keyword}&orientation=portrait&client_id={access_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            image_url = data['urls']['regular']
            img_data = requests.get(image_url).content
            with open('bg_image.jpg', 'wb') as handler:
                handler.write(img_data)
            return 'bg_image.jpg'
    except: return None

def create_video(fact, image_path):
    print("🎥 Creating video with full-screen overlay fix...", flush=True)
    video_size = (1080, 1920)
    
    if image_path:
        # התמונה מוגדלת לגובה 1920 וממורכזת
        bg = ImageClip(image_path).resize(height=1920).set_position('center').set_duration(5)
    else:
        bg = ColorClip(size=video_size, color=(20, 20, 20), duration=5)
    
    # השכבה השחורה מוגדרת בדיוק לגודל המסך המלא
    dim_layer = ColorClip(size=video_size, color=(0,0,0), duration=5).set_opacity(0.5)
    
    txt = TextClip(
        fact, 
        fontsize=70, 
        color='white', 
        font='Liberation-Sans-Bold', 
        size=(850, None), 
        method='caption'
    )
    txt = txt.set_position('center').set_duration(5)
    
    # התיקון הקריטי: הגדרת גודל (size) מפורש לקומפוזיציה
    final = CompositeVideoClip([bg, dim_layer, txt], size=video_size)
    
    # 25 FPS לפי העדפת המשתמש
    final.write_videofile("short_video.mp4", fps=25, codec="libx264", audio=False)
    return "short_video.mp4"

def get_authenticated_service():
    client_config = json.loads(os.environ.get('CLIENT_SECRET_JSON'))
    config = next(iter(client_config.values()))
    creds = Credentials(
        token=None, refresh_token=os.environ.get('YOUTUBE_REFRESH_TOKEN'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config['client_id'], client_secret=config['client_secret']
    )
    return build('youtube', 'v3', credentials=creds)

def post_comment(youtube, video_id):
    print(f"💬 Posting pinned comment for Gumroad link...", flush=True)
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
        print("✅ Comment posted!")
    except Exception as e:
        print(f"⚠️ Comment failed: {e}")

def upload_video(youtube, video_path, fact):
    title = "Social Intelligence: " + (fact[:40] + "..." if len(fact)>40 else fact)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title, 
                "description": fact + "\n\n#Psychology #SocialIntelligence #Shorts", 
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        },
        media_body=MediaFileUpload(video_path)
    )
    response = request.execute()
    video_id = response.get('id')
    print(f"✅ Uploaded! ID: {video_id}")
    post_comment(youtube, video_id)
    return video_id

if __name__ == "__main__":
    try:
        service = get_authenticated_service()
        fact, keyword = get_daily_content()
        image = download_unsplash_image(keyword)
        video = create_video(fact, image)
        upload_video(service, video, fact)
    except Exception as e:
        print(f"❌ Final Error Check: {e}")
