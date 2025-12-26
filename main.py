import os
import json
import requests
import google.generativeai as genai
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# 1. חיבור ל-Secrets (הכל כבר מוגדר אצלך ב-GitHub)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
CLIENT_SECRET_RAW = os.environ.get("CLIENT_SECRET_JSON")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

# הגדרת Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_viral_content():
    print("🤖 מייצר תוכן ויראלי עם Gemini...")
    try:
        prompt = (
            "Write a viral 7-word hook about Social Intelligence. "
            "Also, write a 2-line description. "
            "Format: Hook: [text] | Description: [text]. No emojis."
        )
        response = model.generate_content(prompt)
        raw = response.text.strip().split("|")
        hook = raw[0].replace("Hook:", "").strip().replace('"', '')
        desc = raw[1].replace("Description:", "").strip() if len(raw) > 1 else "Master your social skills."
        return hook, desc
    except:
        return "Listening is the ultimate social power move", "Learn why master communicators focus on listening more than speaking."

def get_background_image():
    print("🖼️ מוריד תמונה מ-Unsplash...")
    try:
        url = f"https://api.unsplash.com/photos/random?query=minimalist,psychology&orientation=portrait&client_id={UNSPLASH_KEY}"
        res = requests.get(url).json()
        img_url = res['urls']['regular']
        with open("bg.jpg", 'wb') as f:
            f.write(requests.get(img_url).content)
        return "bg.jpg"
    except:
        return None

def create_video():
    hook, desc = get_viral_content()
    fps = 25 # מותאם אישית עבורך
    duration = 6
    
    # 2. שילוב התמונה
    bg_file = get_background_image()
    if bg_file:
        bg = ImageClip(bg_file).set_duration(duration).resize(height=1920)
        bg = bg.crop(x1=bg.w/2-540, y1=0, x2=bg.w/2+540, y2=1920)
    else:
        bg = ColorClip(size=(1080, 1920), color=(20, 20, 20)).set_duration(duration)

    # 3. עיצוב הטקסט
    txt = TextClip(hook, fontsize=90, color='white', font='Arial-Bold',
                   method='caption', size=(900, None)).set_duration(duration).set_position('center')

    video = CompositeVideoClip([bg, txt])
    video.fps = fps

    # 4. שילוב המוזיקה (Resolution - Wayne Jones.mp3)
    audio_file = "Resolution - Wayne Jones.mp3"
    if os.path.exists(audio_file):
        print("🎵 מוסיף מוזיקת רקע...")
        audio = AudioFileClip(audio_file).set_duration(duration)
        video = video.set_audio(audio)

    output = "final_shorts.mp4"
    video.write_videofile(output, fps=fps, codec="libx264", audio_codec="aac")
    return output, hook, desc

def upload_and_pin(file_path, title, description):
    print("🚀 מעלה ליוטיוב ונועץ תגובה...")
    try:
        client_config = json.loads(CLIENT_SECRET_RAW)
        creds_data = client_config.get('installed') or client_config.get('web')
        creds = Credentials(token=None, refresh_token=REFRESH_TOKEN, 
                            token_uri="https://oauth2.googleapis.com/token",
                            client_id=creds_data['client_id'], client_secret=creds_data['client_secret'])
        creds.refresh(Request())
        youtube = build("youtube", "v3", credentials=creds)
        
        # העלאה
        body = {
            "snippet": {"title": title[:100], "description": description + "\n\n#shorts #socialintelligence", "categoryId": "27"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        }
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        video_id = response.get('id')
        print(f"✅ עלה! ID: {video_id}")

        # 5. נעיצת תגובה (Gumroad)
        comment_body = {
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {"snippet": {"textOriginal": "Get the full guide here: [YOUR_GUMROAD_LINK]"}}
            }
        }
        comment_res = youtube.commentThreads().insert(part="snippet", body=comment_body).execute()
        comment_id = comment_res['snippet']['topLevelComment']['id']
        youtube.comments().setModerationStatus(id=comment_id, moderationStatus="published").execute()
        print("📌 תגובה נוספה בהצלחה!")
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")

if __name__ == "__main__":
    if all([GEMINI_KEY, REFRESH_TOKEN, CLIENT_SECRET_RAW]):
        file, hook, desc = create_video()
        upload_and_pin(file, hook, desc)
