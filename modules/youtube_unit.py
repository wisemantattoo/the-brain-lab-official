import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from modules.config import SECRETS, GUMROAD_LINK, OFFICIAL_DESCRIPTION

def deploy_to_youtube(file_path, title, guide):
    """העלאה ליוטיוב עם מדריך טקטי בתיאור [cite: 2026-01-01, FIXED: 2026-01-05]."""
    print("🚀 DEPLOYING TO YOUTUBE...")
    try:
        # בניית CLIENT_SECRET_JSON מהמפתחות הנפרדים
        client_config = {
            "installed": {
                "client_id": SECRETS["GOOGLE_CLIENT_ID"],
                "client_secret": SECRETS["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }
        
        creds = Credentials(
            token=None, 
            refresh_token=SECRETS["YOUTUBE_REFRESH_TOKEN"],  # ← תוקן!
            token_uri="https://oauth2.googleapis.com/token",
            client_id=SECRETS["GOOGLE_CLIENT_ID"],  # ← תוקן!
            client_secret=SECRETS["GOOGLE_CLIENT_SECRET"]  # ← תוקן!
        )
        
        print("🔄 Refreshing OAuth token...")
        creds.refresh(Request())
        
        youtube = build("youtube", "v3", credentials=creds)
        
        # שילוב המדריך המעשי יחד עם החתימה הרשמית
        full_desc = f"{guide}\n\n{OFFICIAL_DESCRIPTION}"
        
        body = {
            "snippet": {
                "title": title, 
                "description": full_desc, 
                "categoryId": "27"
            },
            "status": {
                "privacyStatus": "public", 
                "selfDeclaredMadeForKids": False
            }
        }
        
        print(f"📤 Uploading video: {title}")
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        response = youtube.videos().insert(
            part="snippet,status", 
            body=body, 
            media_body=media
        ).execute()
        
        video_id = response['id']
        print(f"✅ Video uploaded! ID: {video_id}")
        
        # תגובה אוטומטית
        try:
            youtube.commentThreads().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id, 
                        "topLevelComment": {
                            "snippet": {
                                "textOriginal": f"⚡ Get Started with Protocol #001: {GUMROAD_LINK}"
                            }
                        }
                    }
                }
            ).execute()
            print("💬 Auto-comment posted!")
        except Exception as comment_error:
            print(f"⚠️ Comment failed (non-critical): {comment_error}")
        
        print(f"🎉 DEPLOYED! https://youtube.com/shorts/{video_id}")
        return video_id
        
    except KeyError as e:
        print(f"❌ MISSING SECRET: {e}")
        print(f"Available keys: {list(SECRETS.keys())}")
        return None
    except Exception as e:
        print(f"❌ YOUTUBE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None
