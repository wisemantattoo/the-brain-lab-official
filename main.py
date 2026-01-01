# The Brain Lab - Main Commander v1.1 (Accessible & Modular) [cite: 2026-01-01]

from modules.config import SECRETS
from modules.ai_brain import get_viral_content
from modules.video_lab import create_video
from modules.youtube_unit import deploy_to_youtube

def run_lab_mission():
    """מנהל את משימת ייצור התוכן והפצתו [cite: 2025-12-28]."""
    
    # 1. אימות נתוני כניסה (Safety Check) [cite: 2025-12-28]
    if not all([SECRETS["GEMINI_KEY"], SECRETS["REFRESH_TOKEN"], SECRETS["CLIENT_SECRET_RAW"]]):
        print("❌ MISSION ABORTED: Missing critical secrets in config.")
        return

    print("--- ⚡ STARTING BRAIN LAB MISSION v1.1 ---")

    try:
        # 2. שלב המודיעין: יצירת תוכן עם DNA נגיש [cite: 2026-01-01]
        insight, title, topic = get_viral_content()
        
        # 3. שלב הייצור: רינדור וידאו ב-25 FPS [cite: 2025-12-23]
        video_file = create_video(insight, title, topic)
        
        # 4. שלב ההפצה: העלאה ליוטיוב עם לינק לחיץ [cite: 2026-01-01]
        if video_file:
            deploy_to_youtube(video_file, title)
            
        print("--- ✨ MISSION COMPLETE: ACCESSIBLE UNIT DEPLOYED ---")

    except Exception as e:
        print(f"⚠️ CRITICAL SYSTEM FAILURE: {e}")

if __name__ == "__main__":
    run_lab_mission()
