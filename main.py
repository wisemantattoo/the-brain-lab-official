from modules.config import SECRETS
from modules.ai_brain import get_viral_content
from modules.video_lab import create_video
from modules.youtube_unit import deploy_to_youtube
from modules.database import init_database, save_video

def run_lab_mission():
    # אתחול database אם צריך
    init_database()
    
    # בדיקת secrets
    required_keys = ["GEMINI_API_KEY", "YOUTUBE_REFRESH_TOKEN", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"]
    
    if not all(SECRETS.get(key) for key in required_keys):
        print("❌ ERROR: Missing YouTube OAuth credentials in GitHub Secrets.")
        print(f"Missing: {[k for k in required_keys if not SECRETS.get(k)]}")
        return
    
    print("--- ⚡ STARTING MISSION: HOOK & GUIDE v3.0 + DATABASE ---")
    
    try:
        # 1. ה-AI מייצר תוכן מבוסס דאטה [cite: 2026-01-05]
        hook, title, guide = get_viral_content()
        print(f"✅ Content generated: {title}")
        
        # 2. יצירת וידאו
        video_file = create_video(hook, title, "minimalist psychology")
        
        if not video_file:
            print("❌ Video creation failed")
            return
        
        print(f"✅ Video created: {video_file}")
        
        # 3. העלאה ליוטיוב
        video_id = deploy_to_youtube(video_file, title, guide)
        
        if not video_id:
            print("❌ YouTube upload failed")
            return
        
        print(f"✅ Deployed successfully: https://youtube.com/shorts/{video_id}")
        
        # 4. ✨ NEW! שמירה ב-database [cite: 2026-01-05]
        # נזהה את ה-domain מתוך המידע שיש
        domain = identify_domain(hook, title)
        save_video(video_id, hook, title, guide, domain)
        print(f"✅ Saved to database with domain: {domain}")
        
        print("--- ✨ MISSION COMPLETE ---")
        
    except Exception as e:
        print(f"⚠️ FAILURE: {e}")
        import traceback
        traceback.print_exc()


def identify_domain(hook, title):
    """
    מזהה את ה-domain/נושא על בסיס keywords.
    פונקציה פשוטה - בעתיד אפשר לשפר עם AI.
    """
    text = (hook + " " + title).lower()
    
    # מילות מפתח לכל domain
    domain_keywords = {
        "Neuroscience": ["brain", "neuroscience", "pupil", "dopamine", "neural", "cognitive"],
        "Body Language": ["eye", "gaze", "body", "neck", "gesture", "flex", "posture"],
        "Dark Psychology": ["manipulation", "fbi", "interrogation", "detect", "lie", "deception"],
        "Social Psychology": ["social", "influence", "persuasion", "cialdini", "conformity"],
        "Vulnerability": ["vulnerability", "brown", "authentic", "boundary", "reveal"],
        "Cognitive Bias": ["bias", "kahneman", "thinking", "glitch", "error", "fallacy"],
        "Peak Performance": ["performance", "focus", "flow", "habit", "productivity"]
    }
    
    # חיפוש התאמה
    for domain, keywords in domain_keywords.items():
        if any(keyword in text for keyword in keywords):
            return domain
    
    return "General Psychology"


if __name__ == "__main__":
    run_lab_mission()
