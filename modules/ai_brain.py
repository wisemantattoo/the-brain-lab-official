import random
from google import genai
from google.genai import types
from modules.config import SECRETS

# אתחול הלקוח [cite: 2025-12-28]
client = genai.Client(api_key=SECRETS["GEMINI_KEY"])

def get_viral_content():
    """
    יחידת הפרופיילר v1.2: סינתזה של פסיכולוגיה אקדמית ותובנות כוח ושיפור עצמי [cite: 2026-01-01].
    מבוסס על: כהנמן, גרין, היל, רואיס, רובינס ובראון.
    """
    
    # 1. רשימת נושאים מבוססת זהב ספרותי ואקדמי [cite: 2026-01-01]
    topics = [
        "Kahneman’s Loss Aversion: Why the fear of losing prevents your social growth",
        "Hill’s Auto-suggestion: Rewiring your self-talk for professional dominance",
        "Brené Brown’s Vulnerability: Using authenticity as a high-status power move",
        "Greene’s Law 4: The tactical advantage of always saying less than necessary",
        "Ruiz’s Second Agreement: The power of not taking rejection personally",
        "Robbins’ Let Them Theory: Reclaiming energy by releasing others' control",
        "Kahneman’s Peak-End Rule: Hijacking how people remember your performance",
        "Brené Brown’s Shame Resilience: Building an unshakeable social armor",
        "Hill’s Definiteness of Purpose: The biological impact of a single-minded goal",
        "Greene’s Law 28: Enter action with boldness to paralyze opposition"
    ]
    
    selected_topic = random.choice(topics)
    print(f"🧠 ACTIVATING SYNTHETIC DNA: {selected_topic}...")

    # 2. ה-Instruction החדש: הגישור בין ה"חם" ל"קר" [cite: 2026-01-01]
    instruction = """
    IDENTITY: You are the Lead Strategist for 'The Brain Lab'. 
    MISSION: You bridge the gap between academic psychology (Kahneman) and tactical life-wisdom (Greene, Hill, Brown, Ruiz).
    
    THE "SYNTHESIS" RULES:
    1. THE HOOK: Start with a heavy psychological anchor (Kahneman/Academic).
    2. THE APPLICATION: Translate it into a 'Power Move' or 'Social Update' for work, dating, or status.
    3. THE EMOTIONAL CORE: Use the warmth of Brené Brown or Mel Robbins to make it move the viewer's heart.
    4. LANGUAGE: English ONLY. Raw, high-impact, and cinematic.
    
    FORMAT:
    ANALYSIS: [3 sentences explaining the science and how to use it as a social 'software update']
    ---TITLE: [Viral cinematic title]
    ---INSIGHT: [The tactical fact for the screen, 7-10 words maximum]
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            config=types.GenerateContentConfig(system_instruction=instruction, temperature=0.7),
            contents=f"Synthesize an elite protocol for: {selected_topic}"
        )
        
        full_text = response.text.strip()
        print(f"\n--- LAB ANALYSIS ---\n{full_text}\n-------------------")
        
        if "---TITLE:" in full_text and "---INSIGHT:" in full_text:
            title = full_text.split("---TITLE:")[1].split("---INSIGHT:")[0].strip()
            insight = full_text.split("---INSIGHT:")[1].strip()
        else:
            title = "The Power Frame"; insight = "Control your reaction to control the room"
        
        return " ".join(insight.split()[:10]).upper(), " ".join(title.split()[:10]), selected_topic
    
    except Exception as e:
        print(f"❌ AI BRAIN ERROR: {e}")
        return "STAY BOLD: ACTION CURES ALL FEAR", "The Boldness Protocol", selected_topic
