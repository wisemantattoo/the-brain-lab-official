import os
import json
import time
import datetime
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, ImageClip

# --- הלינק שלך ---
GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

# --- מאגר עובדות לחודשיים (זוגות: עובדה + מילת מפתח לתמונה) ---
facts_data = [
    ("Psychology says: Your brain does more creative work when you are tired.", "creative night"),
    ("Smart people tend to have fewer friends than the average person.", "alone thinking"),
    ("The way you dress is linked to your mood.", "fashion mood"),
    ("Pretending not to care is the habit of someone who generally cares the most.", "sad face"),
    ("The type of music you listen to affects the way you perceive the world.", "headphones listening"),
    ("Your brain treats rejection like physical pain.", "heartbreak"),
    ("If you announce your goals to others, you are less likely to make them happen.", "silence secret"),
    ("90% of people text things they can't say in person.", "smartphone texting"),
    ("Singing reduces feelings of anxiety and depression.", "singing microphone"),
    ("Your favorite song is likely associated with an emotional event.", "music concert"),
    ("Sarcasm is a sign of a healthy brain.", "brain art"),
    ("We are the most imaginative in the night and the least creative in the day.", "night sky stars"),
    ("It takes about 66 days for an average individual to make a new habit.", "calendar clock"),
    ("People who try to keep everyone happy often end up feeling the loneliest.", "lonely crowd"),
    ("The happier you are, the less sleep you require.", "happy energy"),
    ("Being with positive and happy people makes you happier.", "friends laughing"),
    ("Eating chocolate discharges the same chemical into your body as falling in love.", "chocolate"),
    ("Men are not funnier than women: they just make more jokes, not caring if people like it.", "laughing man"),
    ("People look more attractive when they speak about the things they are really interested in.", "passion speaking"),
    ("When you hold the hand of a loved one, you feel less pain and worry.", "holding hands"),
    ("Intelligent people tend to have a messier desk.", "messy desk workspace"),
    ("People who swear a lot tend to be more loyal, open, and honest.", "honest face"),
    ("Liars usually have more eye contact than truth-tellers.", "eyes looking"),
    ("Traveling boosts brain health and also decreases a person's risk of heart attack and depression.", "travel nature"),
    ("Hearing your name when no one is calling you is a sign of a healthy mind.", "mind confusion"),
    ("You can't read in a dream because reading and dreaming are functions of different sides of the brain.", "surreal dream"),
    ("Talking to yourself can actually make you smarter.", "mirror reflection"),
    ("Your brain can't lie to you about who you love.", "love couple"),
    ("Good liars are also good at detecting lies from others.", "detective"),
    ("Thinking in a second language forces you to make more rational decisions.", "languages"),
    ("Spending money on others yields more happiness than spending it on yourself.", "gift giving"),
    ("The very last person on your mind before you fall asleep is either the reason for your happiness or your pain.", "sleeping bed"),
    ("Comedians and funny people are actually more depressed than others.", "clown sad"),
    ("People with high self-esteem are more likely to stay in a relationship.", "confident person"),
    ("When you sneeze, your brain shuts down for a microsecond.", "sneezing"),
    ("Your brain uses 20% of the total oxygen and blood in your body.", "anatomy brain"),
    ("Multitasking is impossible; your brain just switches tasks very quickly.", "chaos busy"),
    ("You are more likely to remember something if you write it down.", "writing notebook"),
    ("The smell of chocolate increases theta brain waves, which triggers relaxation.", "hot chocolate"),
    ("People who sleep on their stomach have more intense dreams.", "sleeping person"),
    ("Your brain continues to develop until your late 40s.", "aging growth"),
    ("Being ignored causes the same chemical reaction in the brain as a physical injury.", "ignored alone"),
    ("Depression is often the result of overthinking; the mind creates problems that didn't exist.", "stressed thinking"),
    ("Tears caused by sadness, happiness, and onions all look different under a microscope.", "eye tear"),
    ("Hugging for 20 seconds releases oxytocin, which can make you trust someone more.", "hugging"),
    ("People who are prone to guilt are better at understanding other people's thoughts and feelings.", "empathy"),
    ("If you want to know if someone is watching you, yawn. If they yawn too, they were watching.", "yawning"),
    ("A crush only lasts for a maximum of 4 months. If it exceeds, you are in love.", "romantic dates"),
    ("The average person tells 4 lies a day.", "fingers crossed"),
    ("Women have twice as many pain receptors on their bodies as men, but a much higher pain tolerance.", "strong woman"),
    ("People are more honest when they are tired.", "tired sleepy"),
    ("Writing down negative thoughts and tossing them in a trash can can improve your mood.", "crumpled paper"),
    ("Your brain perceives the future as a variant of the past.", "time hourglass"),
    ("Generally, people who give the best advice are the ones with the most problems.", "advice talking"),
    ("It is impossible to hum while holding your nose.", "funny face"),
    ("People read faster with longer lines, but prefer shorter lines.", "books reading"),
    ("We're only capable of being close with about 150 people.", "crowd people"),
    ("The sharper your brain, the more you dream.", "dream abstract"),
    ("Optimism can be learned.", "sunshine happy"),
    ("Meditation can physically change your brain structure.", "meditation yoga")
]

# --- פונקציה לבחירת עובדה + תמונה ---
def get_daily_content():
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    index = day_of_year % len(facts_data)
    selected_fact, keyword = facts_data[index]
    print(f"📅 Day {day_of_year}: Fact: {selected_fact[:20]}... | Keyword: {keyword}", flush=True)
    return selected_fact, keyword

# --- פונקציה להורדת תמונה מ-Unsplash ---
def download_unsplash_image(keyword):
    print(f"🖼️ Searching Unsplash for: {keyword}...", flush=True)
    access_key = os.environ.get('UNSPLASH_ACCESS_KEY')
    
    if not access_key:
        print("⚠️ No Unsplash Key found! Using black background.")
        return None
        
    url = f"https://api.unsplash.com/photos/random?query={keyword}&orientation=portrait&client_id={access_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            image_url = data['urls']['regular']
            img_data = requests.get(image_url).content
            with open('bg_image.jpg', 'wb') as handler:
                handler.write(img_data)
            print("✅ Image downloaded successfully!", flush=True)
            return 'bg_image.jpg'
        else:
            print(f"⚠️ Unsplash Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Error downloading image: {e}")
        return None

# --- יצירת הסרטון (משולב תמונה) ---
def create_video(fact, image_path):
    print("🎥 Starting video creation...", flush=True)
    
    if image_path:
        # תמונה ממורכזת בגובה מלא
        bg = ImageClip(image_path).resize(height=1920).set_position('center').set_duration(5)
    else:
        bg = ColorClip(size=(1080, 1920), color=(20, 20, 20), duration=5)

    # שכבת כהות - 50% שחור כדי שהטקסט יבלוט
    dim_layer = ColorClip(size=(1080, 1920), color=(0,0,0), duration=5).set_opacity(0.5)

    txt = TextClip(
        fact, 
        fontsize=70,
        color='white', 
        font='Liberation-Sans-Bold', 
        size=(850, None), 
        method='caption'
    )
    txt = txt.set_position('center').set_duration(5)
    
    final = CompositeVideoClip([bg, dim_layer, txt])
    final.write_videofile("short_video.mp4", fps=30, codec="libx264", audio=False, preset='medium', threads=4)
    print("✅ Video created successfully!", flush=True)
    return "short_video.mp4"

# --- יצירת טמנייל ---
def create_thumbnail_image(fact, image_path):
    print("🖼️ Creating thumbnail...", flush=True)
    
    if image_path:
        bg = ImageClip(image_path).resize(height=1920).set_position('center')
    else:
        bg = ColorClip(size=(1080, 1920), color=(0, 50, 200), duration=1)
        
    dim_layer = ColorClip(size=(1080, 1920), color=(0,0,0), duration=1).set_opacity(0.5)

    txt = TextClip(
        fact, 
        fontsize=70,
        color='white', 
        font='Liberation-Sans-Bold', 
        size=(850, None), 
        method='caption'
    )
    txt = txt.set_position('center')
    
    thumb_clip = CompositeVideoClip([bg, dim_layer, txt])
    thumb_file = "custom_thumbnail.png"
    thumb_clip.save_frame(thumb_file, t=0.1)
    print("✅ Thumbnail image saved!", flush=True)
    return thumb_file

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

    if thumbnail_path:
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
        current_fact, keyword = get_daily_content()
        bg_image = download_unsplash_image(keyword)
        video_file = create_video(current_fact, bg_image)
        thumbnail_file = create_thumbnail_image(current_fact, bg_image)
        upload_video_and_thumbnail(service, video_file, thumbnail_file, current_fact)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
