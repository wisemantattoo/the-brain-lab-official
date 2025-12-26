import os
import json
import google.generativeai as genai
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# 1. הגדרות וחיבור ל-Secrets מה-GitHub Actions
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
CLIENT_SECRET_RAW = os.environ.get("CLIENT_SECRET_JSON")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

# הגדרת Gemini - עברנו ל-Flash כדי למנוע שגיאות 404
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_content():
    print("🤖 פונה ל-Gemini לקבלת תוכן...")
    try:
        prompt = "Create a powerful 7-word hook about Social Intelligence for a YouTube Short. No emojis."
        response = model.generate_content(prompt)
        text = response.text.strip().replace('"', '')
        print(f"✅ תוכן שנוצר: {text}")
        return text
    except Exception as e:
        print(f"⚠️ שגיאה ב-Gemini: {e}")
        return "Master Your Social Intelligence"

def create_video():
    text = get_ai_content()
    # מוגדר ל-25 FPS בדיוק כפי שאתה מצלם
    fps = 25 
    duration = 5 
    
    print(f"🎬 מרנדר וידאו ב-{fps} FPS...")
    
    # רקע כהה לסרטון
    background = ColorClip(size=(1080, 1920), color=(20, 20, 20)).set_duration(duration)
    
    # יצירת הטקסט במרכז המסך
    txt_clip = TextClip(text, fontsize=80, color='white', font='Arial-Bold', 
                        method='caption', size=(900, None)).set_duration(duration)
    txt_clip = txt_clip.set_position('center')
    
    video = CompositeVideoClip([background, txt_clip])
    video.fps = fps
    
    output_file = "final_video.mp4"
    # רינדור בפורמט שיוטיוב אוהב
    video.write_videofile(output_file, fps=fps, codec="libx264", audio=False)
    return output_file, text

def upload_to_youtube(file_path, title):
    print("🚀 מתחבר ל-YouTube API להעלאת הסרטון...")
    try:
        client_config = json.loads(CLIENT_SECRET_RAW)
        # זיהוי אם זה קובץ מ-OAuth Desktop או Web
        creds_data = client_config.get('installed') or client_config.get('web')
        
        creds = Credentials(
            token=None,
            refresh_token=REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret']
        )
        
        # רענון הגישה ליוטיוב
        creds.refresh(Request())
        
        youtube = build("youtube", "v3", credentials=creds)
        
        request_body = {
            "snippet": {
                "title": title[:100],
                "description": "Daily AI Generated Short #shorts #socialintelligence",
                "categoryId": "27" 
            },
            "status": {
                "privacyStatus": "public", 
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        upload = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
        
        print("📤 מעלה קובץ...")
        response = upload.execute()
        print(f"✅ הצלחה! הסרטון עלה לערוץ. ID: {response.get('id')}")
        
    except Exception as e:
        print(f"❌ שגיאה בתהליך ההעלאה: {e}")

# השורה שתיקנתי כדי למנוע את ה-SyntaxError
if __name__ == "__main__":
    print("🚀 הבוט יצא לדרך!")
    # בדיקה שכל הנתונים קיימים
    if not all([GEMINI_KEY, CLIENT_SECRET_RAW, REFRESH_TOKEN]):
        print("❌ חסרים Secrets בהגדרות ה-GitHub (Settings > Secrets)!")
    else:
        video_file, ai_text = create_video()
        upload_to_youtube(video_file, ai_text)
        print("🏁 הבוט סיים את העבודה היומית.")
