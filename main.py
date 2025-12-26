import os
import json
import google.generativeai as genai
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# הגדרות Secrets
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
CLIENT_SECRET_RAW = os.environ.get("CLIENT_SECRET_JSON")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

# הגדרת Gemini - תיקון לגרסה יציבה
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_viral_content():
    print("🤖 מייצר תוכן ויראלי עם Gemini...")
    try:
        # ביקשנו מה-AI לייצר גם משפט לסרטון וגם תיאור מתאים
        prompt = (
            "Create a provocative 7-word hook about social intelligence or human psychology "
            "for a YouTube Short. Also, write a short 2-line description for the video. "
            "Format: Hook | Description. No emojis."
        )
        response = model.generate_content(prompt)
        content = response.text.strip().split('|')
        
        hook = content[0].strip().replace('"', '')
        description = content[1].strip() if len(content) > 1 else "Exploring the secrets of social intelligence."
        
        print(f"✅ משפט שנבחר: {hook}")
        return hook, description
    except Exception as e:
        print(f"⚠️ שגיאה ב-AI: {e}")
        return "The psychological trick to win any argument", "Mastering social intelligence for better connections."

def create_video():
    hook_text, description = get_viral_content()
    fps = 25 # שמירה על הסטנדרט שלך [cite: 2025-12-23]
    duration = 5
    
    print(f"🎬 מרנדר וידאו ב-{fps} FPS...")
    
    # רקע זמני (עד שנוסיף תמונות)
    bg = ColorClip(size=(1080, 1920), color=(20, 20, 20)).set_duration(duration)
    
    # טקסט משופר
    txt = TextClip(hook_text, fontsize=85, color='white', font='Arial-Bold',
                   method='caption', size=(950, None)).set_duration(duration)
    txt = txt.set_position('center')

    video = CompositeVideoClip([bg, txt])
    video.fps = fps

    output = "final_shorts.mp4"
    video.write_videofile(output, fps=fps, codec="libx264", audio=False)
    return output, hook_text, description

def upload_to_youtube(file_path, title, description):
    print("🚀 מעלה ליוטיוב עם תיאור מותאם...")
    try:
        client_config = json.loads(CLIENT_SECRET_RAW)
        creds_data = client_config.get('installed') or client_config.get('web')
        creds = Credentials(token=None, refresh_token=REFRESH_TOKEN, 
                            token_uri="https://oauth2.googleapis.com/token",
                            client_id=creds_data['client_id'], client_secret=creds_data['client_secret'])
        creds.refresh(Request())
        youtube = build("youtube", "v3", credentials=creds)
        
        body = {
            "snippet": {
                "title": title[:100], 
                "description": description + "\n\n#shorts #psychology #socialintelligence", 
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        }
        
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        print("✅ הסרטון עלה בהצלחה!")
    except Exception as e:
        print(f"❌ שגיאה בהעלאה: {e}")

if __name__ == "__main__":
    if all([GEMINI_KEY, REFRESH_TOKEN, CLIENT_SECRET_RAW]):
        file, hook, desc = create_video()
        upload_to_youtube(file, hook, desc)
    else:
        print("❌ חסרים Secrets!")
