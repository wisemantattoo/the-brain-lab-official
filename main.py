import os
import random
import json
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

# רשימת עובדות (אפשר להוסיף עוד מאות בהמשך)
facts = [
    "Psychology says: Your brain does more creative work when you are tired.",
    "Smart people tend to have fewer friends than the average person.",
    "The way you dress is linked to your mood.",
    "Pretending not to care is the habit of someone who generally cares the most.",
    "The type of music you listen to affects the way you perceive the world."
]

def create_video(fact):
    # יצירת רקע שחור
    bg = ColorClip(size=(1080, 1920), color=(20, 20, 20), duration=5)
    # יצירת הטקסט
    txt = TextClip(fact, fontsize=70, color='white', font='Liberation-Sans', size=(900, None), method='caption')
    txt = txt.set_position('center').set_duration(5)
    # חיבור לסרטון
    final = CompositeVideoClip([bg, txt])
    final.write_videofile("short_video.mp4", fps=24, codec="libx264", audio=False)
    return "short_video.mp4"

def get_authenticated_service():
    client_config = json.loads(os.environ.get('CLIENT_SECRET_JSON'))
    scopes = ['https://www.googleapis.com/auth/youtube.upload']
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(client_config, scopes)
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    
    # שימוש בקוד שהכנסת ל-Secrets
    auth_code = os.environ.get('YOUTUBE_CODE')
    flow.fetch_token(code=auth_code)
    
    # הדפסת ה-Refresh Token לשימוש עתידי (זה יופיע ב-Logs)
    print(f"\n✅ REFRESH_TOKEN: {flow.credentials.refresh_token}\n")
    return build('youtube', 'v3', credentials=flow.credentials)

def upload_video(youtube, file_path, fact):
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f"Amazing Psychology Fact: {fact[:50]}...",
                "description": "Daily dose of psychology. #shorts #psychology #facts",
                "categoryId": "27"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=MediaFileUpload(file_path)
    )
    response = request.execute()
    print(f"🚀 Success! Video uploaded. ID: {response.get('id')}")

if __name__ == "__main__":
    try:
        service = get_authenticated_service()
        current_fact = random.choice(facts)
        video_file = create_video(current_fact)
        upload_video(service, video_file, current_fact)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
