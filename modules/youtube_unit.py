import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from modules.config import SECRETS, GUMROAD_LINK, OFFICIAL_DESCRIPTION

def deploy_to_youtube(file_path, title):
    """העלאה והזרקת תגובה לחיצה [cite: 2026-01-01]."""
    print("🚀 DEPLOYING TO YOUTUBE...")
    try:
        config = json.loads(SECRETS["CLIENT_SECRET_RAW"])
        creds_data = config.get('installed') or config.get('web')
        creds = Credentials(
            token=None, refresh_token=SECRETS["REFRESH_TOKEN"], 
            token_uri="https://oauth2.googleapis.com/token",
            client_id=creds_data['client_id'], client_secret=creds_data['client_secret']
        )
        creds.refresh(Request())
        youtube = build("youtube", "v3", credentials=creds)
        
        full_desc = f"{title}\n\n{OFFICIAL_DESCRIPTION}"
        body = {
            "snippet": {"title": title, "description": full_desc, "categoryId": "27"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
        }
        
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        video_id = response['id'] 
        print(f"✅ UPLOAD SUCCESSFUL! ID: {video_id}")

        # התיקון: שימוש ב-textOriginal במקום textDisplay כדי למנוע את שגיאת 400 [cite: 2026-01-01]
        youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": f"⚡ Get Started with Protocol #001: Download our official Morning Protocol here: {GUMROAD_LINK}"
                        }
                    }
                }
            }
        ).execute()
        print("💬 CLICKABLE COMMENT DEPLOYED SUCCESSFULLY.")
        return video_id
    except Exception as e:
        print(f"❌ YOUTUBE DEPLOYMENT ERROR: {e}")
        return None
