import os
import random
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- הגדרת הלינק החדש שלך ---
GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

# --- רשימת העובדות (המאגר שלך) ---
FACTS = [
    "Did you know? Your brain uses 20% of your body's energy while resting. 🧠⚡ #Neuroscience",
    "Psychology Fact: We are more creative when we are tired. 🎨😴 #Mindset",
    "Neuroplasticity means your brain changes physically with every new thought. 🔄🧬 #Growth",
    "Dopamine isn't just about pleasure; it's about the anticipation of reward. 🎯🍬 #Motivation",
    "Your brain processes images 60,000 times faster than text. 📸⚡ #Facts"
]

def get_video_metadata(fact):
    """יוצר כותרת ותיאור עם הלינק החדש"""
    title = f"Brain Fact: {fact.split(':')[0]} | #TheBrainLab"
    
    description = (
        f"{fact}\n\n"
        f"🧠 STOP OPERATING ON AUTOPILOT. REWIRE YOUR CIRCUITRY.\n"
        f"Get our official Morning Protocol #001 here: 👇\n"
        f"{GUMROAD_LINK}\n\n"
        f"Join the experiment. Decode your mind. 🔬\n"
        f"#Neuroscience #Mindset #Success #Shorts"
    )
    return title, description

def upload_video():
    # חיבור ליוטיוב (וודא שה-SECRETS מוגדרים ב-GitHub)
    api_key = os.environ.get("YOUTUBE_API_KEY") # אם אתה משתמש ב-OAuth זה שונה, אבל זה המבנה הכללי
    
    # בחירת עובדה רנדומלית
    fact = random.choice(FACTS)
    title, description = get_video_metadata(fact)
    
    print(f"Preparing to upload: {title}")
    print(f"Link used: {GUMROAD_LINK}")
    
    # כאן יבוא קוד ההעלאה הטכני שלך (שכבר עובד לפי ה-V הירוק!)
    # אל תמחק את החלק הטכני של ההעלאה שיש לך כבר בקובץ, רק עדכן את הטקסטים למעלה.

if __name__ == "__main__":
    upload_video()
