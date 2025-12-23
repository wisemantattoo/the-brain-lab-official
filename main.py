import os
import json
import time
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

# --- הלינק שלך ---
GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

# --- מאגר עובדות לחודשיים (60 עובדות) ---
facts = [
    "Psychology says: Your brain does more creative work when you are tired.",
    "Smart people tend to have fewer friends than the average person.",
    "The way you dress is linked to your mood.",
    "Pretending not to care is the habit of someone who generally cares the most.",
    "The type of music you listen to affects the way you perceive the world.",
    "Your brain treats rejection like physical pain.",
    "If you announce your goals to others, you are less likely to make them happen.",
    "90% of people text things they can't say in person.",
    "Singing reduces feelings of anxiety and depression.",
    "Your favorite song is likely associated with an emotional event.",
    "Sarcasm is a sign of a healthy brain.",
    "We are the most imaginative in the night and the least creative in the day.",
    "It takes about 66 days for an average individual to make a new habit.",
    "People who try to keep everyone happy often end up feeling the loneliest.",
    "The happier you are, the less sleep you require.",
    "Being with positive and happy people makes you happier.",
    "Eating chocolate discharges the same chemical into your body as falling in love.",
    "Men are not funnier than women: they just make more jokes, not caring if people like it.",
    "People look more attractive when they speak about the things they are really interested in.",
    "When you hold the hand of a loved one, you feel less pain and worry.",
    "Intelligent people tend to have a messier desk.",
    "People who swear a lot tend to be more loyal, open, and honest.",
    "Liars usually have more eye contact than truth-tellers.",
    "Traveling boosts brain health and also decreases a person's risk of heart attack and depression.",
    "Hearing your name when no one is calling you is a sign of a healthy mind.",
    "You can't read in a dream because reading and dreaming are functions of different sides of the brain.",
    "Talking to yourself can actually make you smarter.",
    "Your brain can't lie to you about who you love.",
    "Good liars are also good at detecting lies from others.",
    "Thinking in a second language forces you to make more rational decisions.",
    "Spending money on others yields more happiness than spending it on yourself.",
    "The very last person on your mind before you fall asleep is either the reason for your happiness or your pain.",
    "Comedians and funny people are actually more depressed than others.",
    "People with high self-esteem are more likely to stay in a relationship.",
    "When you sneeze, your brain shuts down for a microsecond.",
    "Your brain uses 20% of the total oxygen and blood in your body.",
    "Multitasking is impossible; your brain just switches tasks very quickly.",
    "You are more likely to remember something if you write it down.",
    "The smell of chocolate increases theta brain waves, which triggers relaxation.",
    "People who sleep on their stomach have more intense dreams.",
    "Your brain continues to develop until your late 40s.",
    "Being ignored causes the same chemical reaction in the brain as a physical injury.",
    "Depression is often the result of overthinking; the mind creates problems that didn't exist.",
    "Tears caused by sadness, happiness, and onions all look different under a microscope.",
    "Hugging for 20 seconds releases oxytocin, which can make you trust someone more.",
    "People who are prone to guilt are better at understanding other people's thoughts and feelings.",
    "If you want to know if someone is watching you, yawn. If they yawn too, they were watching.",
    "A crush only lasts for a maximum of 4 months. If it exceeds, you are in love.",
    "The average person tells 4 lies a day.",
    "Women have twice as many pain receptors on their bodies as men, but a much higher pain tolerance.",
    "People are more honest when they are tired.",
    "Writing down negative thoughts and tossing them in a trash can can improve your mood.",
    "Your brain perceives the future as a variant of the past.",
    "Generally, people who give the best advice are the ones with the most problems.",
    "It is impossible to hum while holding your nose.",
    "People read faster with longer lines, but prefer shorter lines.",
    "We're only capable of being close with about 150 people.",
    "The sharper your brain, the more you dream.",
    "Optimism can be learned.",
    "Meditation can physically change your brain structure."
]

# --- פונקציה לבחירת עובדה ---
def get_daily_fact():
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    fact_index = day_of_year % len(facts)
    selected_fact = facts[fact_index]
    print(f"📅 Day {day_of_year}: Selected fact #{fact_index}", flush=True)
    return selected_fact

# --- יצירת תמונת טמנייל ---
def create_thumbnail_image(fact):
    print("🖼️ Creating blue thumbnail image...", flush=True)
    bg = ColorClip(size=(1080, 1920), color=(0, 50, 200), duration=1)
    
    txt = TextClip(
        fact, 
        fontsize=70,
        color='white', 
        font='Liberation-Sans-Bold', 
        size=(850, None), 
        method='caption'
    )
    # תיקון מיקום: חזרה למרכז המסך
    txt = txt.set_position('center')
    
    thumb_clip = CompositeVideoClip([bg, txt])
    thumb_file = "custom_thumbnail.png"
    thumb_clip.save_frame(thumb_file, t=0.1)
    print("✅ Thumbnail image saved!", flush=True)
    return thumb_file

# --- יצירת הסרטון ---
def create_video(fact):
    print("🎥 Starting video creation...", flush=True)
    bg = ColorClip(size=(1080, 1920), color=(20, 20, 20), duration=5)
    
    txt = TextClip(
        fact, 
        fontsize=70,
        color='white', 
        font='Liberation-Sans-Bold', 
        size=(850, None), 
        method='caption'
    )
    # תיקון מיקום: חזרה למרכז המסך
    txt = txt.set_position('center').set_duration(5)
    
    final = CompositeVideoClip([bg, txt])
    final.write_videofile("short_video.mp4", fps=30, codec="libx264", audio=False, preset='medium', threads=4)
    print("✅ Video created successfully!", flush=True)
    return "short_video.mp4"

def get_authenticated_service():
    print("🔑 Authenticating...", flush=True)
    client_config = json.loads(os.environ.get('CLIENT_SECRET_JSON'))
    config = next(iter(client_config.values()))
    creds = Credentials(
        token=None,
        refresh_token=os.environ.get('YOUTUBE_REFRESH_TOKEN'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config['client_id'],
        client_secret=config['client_secret']
    )
    return build('youtube', 'v3', credentials=creds)

def upload_video_and_thumbnail(youtube, video_path, thumbnail_path, fact):
    print("🚀 Starting video upload...", flush=True)
    
    base_title = fact.split(':')[0]
    if len(base_title) > 50: base_title = base_title[:50]
    title = "Brain Fact: " + base_title + "... #TheBrainLab"
    
    description = (
        f"{fact}\n\n"
        "🧠 STOP OPERATING ON AUTOPILOT. REWIRE YOUR CIRCUITRY.\n"
        "Get our official Morning Protocol #001 here: 👇\n"
        f"{GUMROAD_LINK}\n\n"
        "#Neuroscience #Mindset #Success #Shorts"
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": "27"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(video_path)
    )
    response = request.execute()
    video_id = response.get('id')
    print(f"✅ Video Uploaded! ID: {video_id}", flush=True)
    
    print("⏳ Waiting for YouTube to process before setting thumbnail...", flush=True)
    time.sleep(5)

    print(f"🖼️ Uploading custom thumbnail for video {video_id}...", flush=True)
    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()
        print("✅ Custom thumbnail set successfully!", flush=True)
    except Exception as e:
        print(f"⚠️ Warning: Could not set thumbnail. Error: {e}")

if __name__ == "__main__":
    try:
        service = get_authenticated_service()
        current_fact = get_daily_fact()
        video_file = create_video(current_fact)
        thumbnail_file = create_thumbnail_image(current_fact)
        upload_video_and_thumbnail(service, video_file, thumbnail_file, current_fact)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
