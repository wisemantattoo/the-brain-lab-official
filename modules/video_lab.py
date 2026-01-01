import os
import requests
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
from modules.config import SECRETS

def get_background_image(query):
    """משיכת רקע ויזואלי התואם לנושא [cite: 2025-12-28]."""
    try:
        url = f"https://api.unsplash.com/photos/random?query={query},minimalist,cinematic&orientation=portrait&client_id={SECRETS['UNSPLASH_KEY']}"
        res = requests.get(url).json()
        img_url = res['urls']['regular']
        with open("bg.jpg", 'wb') as f: f.write(requests.get(img_url).content)
        return "bg.jpg"
    except Exception as e:
        print(f"⚠️ Media Scout Error: {e}")
        return None

def create_video(insight, title, topic):
    """הפיכת התובנה לקובץ MP4 ב-25 FPS [cite: 2025-12-23]."""
    fps = 25 
    duration = 8 
    print(f"🎬 RENDERING V1.1 ACCESSIBLE UNIT...")
    
    bg_file = get_background_image(topic)
    if bg_file:
        bg = ImageClip(bg_file).set_duration(duration).resize(height=1920)
        bg = bg.crop(x1=bg.w/2-540, y1=0, x2=bg.w/2+540, y2=1920)
    else:
        bg = ColorClip(size=(1080, 1920), color=(15, 15, 15)).set_duration(duration)

    txt = TextClip(insight, fontsize=65, color='white', font='Arial-Bold', method='caption', size=(950, None)).set_duration(duration).set_position('center')
    video = CompositeVideoClip([bg, txt])
    video.fps = fps
    
    audio_file = "Resolution - Wayne Jones.mp3"
    if os.path.exists(audio_file):
        video = video.set_audio(AudioFileClip(audio_file).set_duration(duration))
        
    output = "final_shorts.mp4"
    video.write_videofile(output, fps=fps, codec="libx264", audio_codec="aac")
    return output
