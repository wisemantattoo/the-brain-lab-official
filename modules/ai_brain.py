import random
from google import genai
from google.genai import types
from modules.config import SECRETS

client = genai.Client(api_key=SECRETS["GEMINI_KEY"])

def get_viral_content():
    """
    יחידת הפרופיילר v1.4: מודל Hook & Protocol.
    מייצר כותרת עצירה (Hook) למסך ומדריך הפעלה (Guide) לתיאור [cite: 2026-01-01].
    """
    # נושאי הזהב מתוך הספרים שאתה אוהב [cite: 2026-01-01]
    topics = [
        "Kahneman’s Peak-End Rule", "Hill’s Auto-suggestion", "Brené Brown’s Strategic Reveal",
        "Greene’s Law 4", "Ruiz’s Second Agreement", "Mel Robbins’ Let Them Theory",
        "Greene’s Law 28", "Kahneman’s Loss Aversion"
    ]
    
    selected_topic = random.choice(topics)
    print(f"🧠 ACTIVATING HOOK DNA: {selected_topic}...")

    # הוראות לביצוע "עצירת נשימה" והסבר מעשי [cite: 2026-01-01]
    instruction = """
    IDENTITY: Tactical Strategist for 'The Brain Lab'.
    MISSION: Create a pattern-interrupting Short.
    
    RULES:
    1. THE HOOK (for video screen): 3-5 words max. High-stakes or mysterious. NO EXPLANATION. 
       Example: 'The 4-Second Silence Trap'.
    2. THE GUIDE (for description): 2-3 sentences maximum. Pure tactical steps on HOW to use it tomorrow. 
    3. LANGUAGE: English ONLY. High-impact.
    
    FORMAT:
    HOOK: [The 3-5 words for the screen]
    GUIDE: [The 2-3 sentences for the description]
    ---TITLE: [Viral YouTube Title]
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            config=types.GenerateContentConfig(system_instruction=instruction, temperature=0.8),
            contents=f"Generate a tactical hook and guide for: {selected_topic}"
        )
        
        full_text = response.text.strip()
        print(f"\n--- LAB ANALYSIS ---\n{full_text}\n-------------------")
        
        # חילוץ המידע לפי המבנה המודולרי החדש [cite: 2025-12-28]
        hook = full_text.split("HOOK:")[1].split("GUIDE:")[0].strip()
        guide = full_text.split("GUIDE:")[1].split("---TITLE:")[0].strip()
        title = full_text.split("---TITLE:")[1].strip()
        
        # מחזיר בדיוק את מה שה-main.py מצפה לקבל [cite: 2026-01-01]
        return hook.upper(), title, guide
    
    except Exception as e:
        print(f"❌ AI BRAIN ERROR: {e}")
        return "THE SILENCE TRAP", "Strategic Silence", "Wait 4 seconds. Silence is power."
