import os
import random
import json
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

facts = [
    "Psychology says: Your brain does more creative work when you are tired.",
    "Smart people tend to have fewer friends than the average person.",
    "The way you dress is linked to your mood.",
    "Pretending not to care is the habit of someone who generally cares the most.",
    "The type of music you listen to affects the way you perceive the world."
]

def create_video(fact):
    bg = ColorClip(size=(1080, 1920), color=(20, 20, 20), duration=5)
    txt = TextClip(fact, fontsize=70, color='white', font='Liberation-Sans', size=(900, None), method='caption')
    txt = txt.set_position('center').set_duration(5)
    final = CompositeVideoClip([bg, txt])
    final.write_videofile("short_video.mp4", fps=24, codec="libx264")
    return "short_video.mp4"

def get_authenticated_service():
    client_config = json.loads(os.environ.get('CLIENT_SECRET_JSON'))
    scopes = ['https://www.googleapis.com/auth/youtube.upload']
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(client_config, scopes)
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    auth_code = os.environ.get('YOUTUBE_CODE')
    if not auth_code:
        auth_url, _ = flow.authorization_url(prompt='consent')
        print(f"\n\n👉👉👉 הנה הקישור שלך לאישור (תעתיק לדפדפן):\n\n{auth_url}\n\n")
        raise Exception("עצור! תעתיק את הלינק למעלה, תקבל קוד מגוגל ותשים אותו ב-Secrets תחת YOUTUBE_CODE")
    flow.fetch_token(code=auth_code)
    return build('youtube', 'v3', credentials=flow.credentials)

if __name__ == "__main__":
    try:
        service = get_authenticated_service()
        current_fact = random.choice(facts)
        video = create_video(current_fact)
        print("Success! System ready to upload.")
    except Exception as e:
        print(e)
        exit(1)
