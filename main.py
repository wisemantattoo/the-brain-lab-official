import os
import time
# כאן יבואו הייבואים של הספריות (כמו googleapiclient וכו') - וודא שהם קיימים בקובץ המקורי שלך

# --- הגדרות המותג והמכירות ---
GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"
CHANNEL_NAME = "The Brain Lab"

def get_video_metadata(fact_title):
    """יוצר כותרת ותיאור שיווקי לכל סרטון"""
    title = f"{fact_title} | #TheBrainLab"
    
    # תיאור הסרטון הכולל את הלינק החדש
    description = (
        f"{fact_title}\n\n"
        f"🧠 STOP OPERATING ON AUTOPILOT. REWIRE YOUR CIRCUITRY.\n"
        f"Get our official Morning Protocol #001 here:\n"
        f"{GUMROAD_LINK}\n\n"
        f"Join the experiment. Decode your mind. 🔬\n"
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

# --- לוגיקת העלאה ---
def upload_to_youtube():
    # שים לב: כאן אמורה להיות הפונקציה הטכנית שלך להעלאה.
    # הקוד הזה רק מגדיר את הטקסטים. וודא ששאר הקוד הטכני (התחברות ליוטיוב וכו') נשמר.
    print(f"Uploading video with link: {GUMROAD_LINK}")
    # ... כאן ממשיך הקוד של העלאת הסרטון ...

if __name__ == "__main__":
    upload_to_youtube()
