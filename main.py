import os
import random
import json
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

# --- הגדרות ---
# כרגע שמתי כאן הנעה להרשמה לערוץ. כ שיהיה לך לינק, פשוט תחליף את הטקסט למטה.
CTA_TEXT = "🧠 Subscribe to The Brain Lab for your daily dose of psychology!" 

# --- מחסן של 50 עובדות פסיכולוגיות ---
FACTS = [
    "Psychology says: Your brain does more creative work when you are tired.",
    "Smart people tend to have fewer friends than the average person.",
    "The way you dress is linked to your mood.",
    "Pretending not to care is the habit of someone who generally cares the most.",
    "The type of music you listen to affects the way you perceive the world.",
    "Your brain treats rejection like physical pain.",
    "If you announce your goals to others, you are less likely to succeed.",
    "Most people have a favorite song because they associate it with an emotional event.",
    "The beginning and the end are easier to remember than the middle.",
    "It only takes 4 minutes to fall in love.",
    "90% of people text things they can't say in person.",
    "People who spend more time in the sun tend to be happier.",
    "Sarcasm is a sign of a healthy brain.",
    "The longer you hide your feelings for someone, the harder you fall for them.",
    "Closing your eyes helps you remember things better.",
    "People who laugh more are better able to tolerate pain.",
    "If a person laughs at even the most stupid jokes, they are lonely deep inside.",
    "When you hold the hand of a loved one, you feel less pain and worry less.",
    "Smart people under-rate themselves; ignorant people think they are brilliant.",
    "Travel boosts brain health and decreases the risk of heart attack and depression.",
    "You can't multi-task. Your brain just switches between tasks very fast.",
    "Our brains are more creative at night.",
    "If you have a backup plan, your first plan is less likely to succeed.",
    "We can only be close to about 150 people at most.",
    "Crying makes you feel better, reduces stress, and helps the body's health.",
    "Chocolate discharges the same chemical in your body as when you start falling in love.",
    "The brain stays active for about 7 minutes after death.",
    "Being alone for a long time is as bad for your health as smoking 15 cigarettes a day.",
    "Your mind wanders 30% of the time.",
    "Anxiety is a feeling that can be contagious.",
    "We are more likely to remember things if we are tested on them.",
    "Thinking about your goals in a second language makes you more rational.",
    "We prefer shorter lines of text but read longer ones faster.",
    "People aged 18 to 33 carry the most stress in the world.",
    "The broken heart syndrome is a real condition.",
    "We are attracted to people who smell like our parents.",
    "Our brain likes to 'edit' boring speeches to make them sound interesting.",
    "Loneliness is not about being alone, it's the feeling that no one cares.",
    "If you talk to yourself, you are actually making your brain more efficient.",
    "People who are bilingual can switch personalities when they switch languages.",
    "The feeling of being ignored has the same effect as an injury.",
    "Your favorite song is likely your favorite because of an emotional memory.",
    "People who have a strong sense of guilt are better at understanding others' feelings.",
    "A hug longer than 20 seconds releases chemicals that make you trust the person.",
    "Being with happy people makes you happier.",
    "If you suspect someone is watching you, just yawn. If they yawn back, they were.",
    "Validation from others is a temporary fix for low self-esteem.",
    "We find people more attractive when they are hard to get.",
    "The average human brain has about 50,000 to 70,000 thoughts a day.",
    "Memories are not like videos; they are reconstructed every time we think of them."
]

def create_video(fact):
    bg = ColorClip(size=(1080, 1920), color=(20, 20, 20), duration=5)
    txt = TextClip(fact, fontsize=70, color='white', font='Liberation-Sans', size=(900, None), method='caption')
    txt = txt.set_position('center').set_duration(5)
    final = CompositeVideoClip([bg, txt])
    final.write_videofile("short_video.mp4", fps=24, codec="libx264", audio=False)
    return "short_video.mp4"

def get_authenticated_service():
    client_config = json.loads(os.environ.get('CLIENT_SECRET_JSON'))['installed']
    creds = google.oauth2.credentials.Credentials(
        None,
        refresh_token=os.environ.get('YOUTUBE_REFRESH_TOKEN'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_config['client_id'],
        client_secret=client_config['client_secret']
    )
    return build('youtube', 'v3', credentials=creds)

def upload_and_comment(youtube, file_path, fact):
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f"The Brain Lab: {fact[:50]}...",
                "description": "Daily Psychology Facts. Subscribe for more! #shorts #psychology",
                "categoryId": "27"
            },
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        },
        media_body=MediaFileUpload(file_path)
    )
    response = request.execute()
    video_id = response['id']
    
    youtube.commentThreads().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {"textOriginal": CTA_TEXT}
                }
            }
        }
    ).execute()
    print(f"🚀 Success! Video ID: {video_id} uploaded.")

if __name__ == "__main__":
    try:
        service = get_authenticated_service()
        fact = random.choice(FACTS)
        video_file = create_video(fact)
        upload_and_comment(service, video_file, fact)
    except Exception as e:
        print(f"Error: {e}")
