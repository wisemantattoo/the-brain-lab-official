import os
import google.generativeai as genai
import cv2 # לשמירה על 25 FPS
# ... (שאר הספריות שלך)

# הגדרת ה-AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-pro')

def get_ai_content():
    try:
        # פנייה ל-Gemini לקבלת השראה ויראלית
        prompt = "Create a 7-word powerful hook about Social Intelligence for a YouTube Short. No emojis."
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '')
    except:
        return "Master Your Social Intelligence" # גיבוי למקרה של תקלה

def create_video():
    text = get_ai_content()
    # כאן הבוט מרנדר ב-25 FPS בדיוק כפי שאתה מצלם
    fps = 25 
    # הוספת המוזיקה: Resolution - Wayne Jones.mp3
    music_file = "Resolution - Wayne Jones.mp3"
    
    print(f"Generating video with text: {text} at {fps} FPS using {music_file}")
    # ... (כאן מגיע קוד הרינדור הקיים שלך)

# העלאה ונעיצת תגובה ל-Gumroad בעזרת ה-Refresh Token
# (הקוד משתמש ב-YOUTUBE_REFRESH_TOKEN שסידרנו ב-Colab)
