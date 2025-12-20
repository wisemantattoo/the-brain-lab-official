import random
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

# רשימת עובדות (הבוט יבחר אחת באקראי בכל פעם)
facts = [
    "Psychology says: Being alone for a long time is as bad for your health as smoking 15 cigarettes a day.",
    "Your brain is more creative when you're tired.",
    "The way you dress is linked to your mood.",
    "Smart people tend to have fewer friends than the average person."
]

def create_video():
    fact = random.choice(facts)
    # יצירת רקע שחור אנכי (מתאים ל-Shorts)
    bg = ColorClip(size=(1080, 1920), color=(20, 20, 20), duration=5)
    # הוספת הטקסט
    txt = TextClip(fact, fontsize=70, color='white', size=(900, None), method='caption')
    txt = txt.set_position('center').set_duration(5)
    
    final = CompositeVideoClip([bg, txt])
    final.write_videofile("short_video.mp4", fps=24, codec="libx264")
    print(f"Video created successfully for: {fact}")

if __name__ == "__main__":
    create_video()
