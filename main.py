from modules.config import SECRETS
from modules.ai_brain import get_viral_content
from modules.video_lab import create_video
from modules.youtube_unit import deploy_to_youtube

def run_lab_mission():
    # התאמה מדויקת לשמות הסודות שהגדרת ב-GitHub Codespaces [cite: 2026-01-05]
    required_keys = ["GEMINI_API_KEY", "YOUTUBE_REFRESH_TOKEN", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"]
    
    if not all(SECRETS.get(key) for key in required_keys):
        print("❌ ERROR: Missing YouTube OAuth credentials in GitHub Secrets.")
        print(f"Missing: {[k for k in required_keys if not SECRETS.get(k)]}")
        return

    print("--- ⚡ STARTING MISSION: HOOK & GUIDE v1.4 ---")
    try:
        # 1. ה-AI מייצר וו למסך ומדריך לתיאור (באישור ה-Thinking Model) [cite: 2026-01-01, 2026-01-05]
        hook, title, guide = get_viral_content()
        
        # 2. יצירת הוידאו עם ה-Hook (ב-25fps כפי שביקשת) [cite: 2025-12-23, 2026-01-05]
        video_file = create_video(hook, title, "minimalist psychology")
        
        # 3. העלאה ליוטיוב באמצעות המפתחות המאובטחים [cite: 2026-01-01, 2026-01-05]
        if video_file:
            deploy_to_youtube(video_file, title, guide)
            
        print("--- ✨ MISSION COMPLETE ---")
    except Exception as e:
        print(f"⚠️ FAILURE: {e}")

if __name__ == "__main__":
    run_lab_mission()
