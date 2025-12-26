import os
import requests
import google.generativeai as genai
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, AudioFileClip

# 1. הגדרות בסיסיות וחיבור ל-Secrets
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

def get_ai_content():
    print("🤖 פונה ל-Gemini לקבלת תוכן...")
    try:
        prompt = "Create a powerful 7-word hook about Social Intelligence for a YouTube Short. No emojis."
        response = model.generate_content(prompt)
        text = response.text.strip().replace('"', '')
        print(f"✅ תוכן שנוצר: {text}")
        return text
    except Exception as e:
        print(f"❌ שגיאה ב-Gemini: {e}")
        return "Master Your Social Intelligence"

def create_video():
    text = get_ai_content()
    fps = 25 # מוגדר ל-25 FPS בדיוק כפי שביקשת
    duration = 5 # אורך הסרטון בשניות
    
    print(f"🎬 מתחיל לרנדר וידאו ב-{fps} FPS...")
    
    # יצירת רקע צבעוני פשוט (אפשר להחליף בתמונה מ-Unsplash בהמשך)
    background = ColorClip(size=(1080, 1920), color=(30, 30, 30)).set_duration(duration)
    
    # הוספת הטקסט
    txt_clip = TextClip(text, fontsize=70, color='white', font='Arial-Bold', 
                        method='caption', size=(900, None)).set_duration(duration)
    txt_clip = txt_clip.set_position('center')
    
    # חיבור הסרטון
    video = CompositeVideoClip([background, txt_clip])
    video.fps = fps
    
    output_file = "final_video.mp4"
    video.write_videofile(output_file, fps=fps, codec="libx264")
    print(f"✅ הווידאו נוצר בהצלחה: {output_file}")
    return output_file

def upload_to_youtube(video_file):
    if not REFRESH_TOKEN:
        print("⚠️ אין Refresh Token, מדלג על העלאה.")
        return
    print("🚀 מתחיל תהליך העלאה ליוטיוב...")
    # כאן יבוא קוד ההעלאה ליוטיוב שלך (שסידרנו ב-Colab)
    # למען הבדיקה, כרגע זה רק מדפיס שהתהליך התחיל
    print(f"הסרטון {video_file} מוכן להעלאה!")

# --- השורה הכי חשובה: הפקודה שמריצה הכל ---
if __name__ == "__main__":
    print("🚀 הבוט התחיל לעבוד!")
    try:
        file = create_video()
        upload_to_youtube(file)
        print("🏁 הבוט סיים את העבודה בהצלחה!")
    except Exception as e:
        print(f"💥 קרסה שגיאה כללית: {e}")
