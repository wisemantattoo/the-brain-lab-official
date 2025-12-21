import os
import time
# כאן יבואו הייבואים של הספריות שאתה משתמש בהן (כמו googleapiclient)

# --- הגדרות המותג והמכירות ---
GUMROAD_LINK = "https://wisemantattoo.gumroad.com/l/vioono"
CHANNEL_NAME = "The Brain Lab"

def get_video_metadata(fact_title):
    """יוצר כותרת ותיאור שיווקי לכל סרטון"""
    title = f"{fact_title} | #TheBrainLab"
    
    # תיאור הסרטון הכולל את הלינק למוצר ב-4.99$
    description = (
        f"{fact_title}\n\n"
        f"🧠 STOP OPERATING ON AUTOPILOT. REWIRE YOUR CIRCUITRY.\n"
        f"Get our official Morning Protocol #001 here:\n"
        f"{GUMROAD_LINK}\n\n"
        f"Join the experiment. Decode your mind, one fact at a time. 🔬\n"
        f"#Neuroscience #Mindset #Success #Shorts"
    )
    return title, description

def get_automated_comment():
    """התגובה שהבוט יפרסם וינעץ (Pin) בתגובות"""
    comment = (
        f"🧠 Ready to rewire your brain for success? \n"
        f"Download the official Morning Protocol #001 here: {GUMROAD_LINK} \n\n"
        f"Decode your mind, one fact at a time! 🔬"
    )
    return comment

# --- לוגיקת העלאה (כאן נמצא הקוד הטכני שלך) ---
def upload_to_youtube():
    # כאן נמצאת הפונקציה שמעלה את הסרטון שלך.
    # וודא שהיא משתמשת ב-title, description ו-comment שהגדרנו למעלה.
    print(f"Uploading video with link: {GUMROAD_LINK}")

if __name__ == "__main__":
    # הבוט מתחיל לעבוד
    upload_to_youtube()
