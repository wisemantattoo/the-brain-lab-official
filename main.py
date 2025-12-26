import os
import json
import google.generativeai as genai
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# 1. חיבור ל-Secrets
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
CLIENT_SECRET_RAW = os.environ.get("CLIENT_SECRET_JSON")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

# הגדרת Gemini - ניסיון לפתור את שגיאת ה-404 עם שם מודל מפורש
genai.configure(api_key=GEMINI_KEY)
# שימוש במודל היציב ביותר כרגע
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def get_real_content():
    print("🤖 מנסה לייצר תוכן אמיתי על אינטליגנציה חברתית...")
    try:
        # פרומפט ממוקד מאוד כדי שלא נקבל זבל
        prompt = (
            "Write a mind-blowing, viral 7-word tip about Social Intelligence (EQ) for a YouTube Short. "
            "Also, write a 2-sentence engaging description for YouTube. "
            "Format: Hook: [text] | Description: [text]. Use NO emojis."
        )
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # פירוק התוכן שחזר
        if "|" in raw_text:
            parts = raw_text.split("|")
            hook = parts[0].replace("Hook:", "").strip().replace('"', '')
            description = parts[1].replace("Description:", "").strip()
        else:
            hook = raw_text[:70].replace('"', '')
            description = "Deep dive into social intelligence secrets."
            
        print(f"✅ תוכן שנוצר: {hook}")
        return hook, description
    except Exception as e:
        print(f"❌ Gemini נכשל שוב: {e}")
        # גיבוי איכותי יותר אם ה-AI קורס
        return "Listening is the ultimate social power move", "Learn why master communicators focus on listening more than speaking."

def create_video():
    hook_text, description = get_real_content()
    fps = 25 # הסטנדרט שלך [cite: 2025-12-23]
    duration = 5
    
    print(f"🎬 מרנדר ב-{fps} FPS...")
    
    # רקע כהה נקי (עד שנוסיף תמונות)
    bg = ColorClip(size=(1080, 1920), color=(15, 15, 15)).set_duration(duration)
    
    # טקסט בולט ומרכזי
    txt = TextClip(hook_text, fontsize=85, color='white', font='Arial-Bold',
                   method='caption', size=(900, None)).set_duration(duration)
    txt = txt.set_position('center')

    video = CompositeVideoClip([bg, txt])
    video.fps = fps

    output = "final_video.mp4"
    video.write_videofile(output, fps=fps, codec="libx264", audio=False)
    return output, hook_text, description

def upload_to_youtube(file_path, title, desc):
    print("🚀 מעלה ליוטיוב...")
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
                "description": desc + "\n\n#shorts #socialintelligence #eq", 
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
    if all([GEMINI_KEY, CLIENT_SECRET_RAW, REFRESH_TOKEN]):
        file, hook, desc = create_video()
        upload_to_youtube(file, hook, desc)
    else:
        print("❌ חסרים Secrets!")
