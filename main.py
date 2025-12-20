import random
import os
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

# רשימת עובדות (הבוט יבחר אחת כל יום)
facts = [
    "Psychology says: Being alone for a long time is as bad for your health as smoking 15 cigarettes a day.",
    "Your brain is more creative when you are tired.",
    "Smart people tend to have fewer friends than the average person.",
    "The way you dress is linked to your mood.",
    "Pretending not to care is the habit of someone who generally cares the most."
]

def create_video():
    # בחירת עובדה אקראית
    fact = random.choice(facts)
    
    # יצירת רקע שחור (בגודל סמארטפון)
    bg = ColorClip(size=(1080, 1920), color=(20, 20, 20), duration=5)
    
    # יצירת טקסט (עם הגדרות שמונעות שגיאות בשרת)
    txt = TextClip(fact, fontsize=70, color='white', font='Liberation-Sans', size=(900, None), method='caption')
    txt = txt.set_position('center').set_duration(5)
    
    # חיבור הכל לסרטון אחד
    final = CompositeVideoClip([bg, txt])
    
    # שמירת הקובץ
    final.write_videofile("short_video.mp4", fps=24, codec="libx264")
    print(f"Success! Video created: {fact}")

if __name__ == "__main__":
    try:
        create_video()
    except Exception as e:
        print(f"Error occurred: {e}")
