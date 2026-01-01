from modules.config import SECRETS
from modules.ai_brain import get_viral_content
from modules.video_lab import create_video
from modules.youtube_unit import deploy_to_youtube

def run_lab_mission():
    if not all([SECRETS["GEMINI_KEY"], SECRETS["REFRESH_TOKEN"]]):
        print("❌ Missing secrets.")
        return

    print("--- ⚡ STARTING MISSION: HOOK & GUIDE v1.4 ---")
    try:
        # 1. ה-AI מייצר וו למסך ומדריך לתיאור [cite: 2026-01-01]
        hook, title, guide = get_viral_content()
        
        # 2. יצירת הוידאו עם ה-Hook (הכותרת הקצרה) [cite: 2025-12-23]
        video_file = create_video(hook, title, "minimalist psychology")
        
        # 3. העלאה עם המדריך הטקטי והחתימה החדשה [cite: 2026-01-01]
        if video_file:
            deploy_to_youtube(video_file, title, guide)
            
        print("--- ✨ MISSION COMPLETE ---")
    except Exception as e:
        print(f"⚠️ FAILURE: {e}")

if __name__ == "__main__":
    run_lab_mission()
