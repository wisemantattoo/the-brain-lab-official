import os
import random
import json
import google_auth_oauthlib.flow
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

def get_authenticated_service():
    # הבוט מחפש את המפתח בכספת
    json_str = os.environ.get('CLIENT_SECRET_JSON')
    
    if not json_str:
        print("\n❌ שגיאה: המפתח לא נמצא בכספת! ודא ששם ה-Secret הוא CLIENT_SECRET_JSON")
        return None

    try:
        client_config = json.loads(json_str)
    except Exception as e:
        print(f"\n❌ שגיאה בתוכן הכספת: {e}")
        return None

    scopes = ['https://www.googleapis.com/auth/youtube.upload']
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(client_config, scopes)
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    
    auth_code = os.environ.get('YOUTUBE_CODE')
    if not auth_code:
        auth_url, _ = flow.authorization_url(prompt='consent')
        print(f"\n\n👉👉👉 הנה הקישור שלך (תעתיק לדפדפן):\n\n{auth_url}\n\n")
        return "WAITING_FOR_CODE"
    return "READY"

if __name__ == "__main__":
    status = get_authenticated_service()
    if status == "WAITING_FOR_CODE":
        exit(1)
