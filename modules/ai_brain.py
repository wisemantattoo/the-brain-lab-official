import random
from google import genai
from google.genai import types
from modules.config import SECRETS

# אתחול הלקוח בתוך המודול שלו [cite: 2025-12-28]
client = genai.Client(api_key=SECRETS["GEMINI_KEY"])

def get_viral_content():
    """
    יחידת הפרופיילר: מייצרת תוכן פסיכולוגי נגיש ופרקטי [cite: 2026-01-01].
    """
    topics = [
        "The 4-Second Silence: Dominating high-stakes negotiations",
        "The NLP Eye-Gaze: Planting suggestions in social settings",
        "The Choice Architecture: Getting an 'Easy Yes' at work",
        "The Baseline Method: Spotting lies in daily conversations",
        "The Hidden Command: Subliminal influence in meetings",
        "The Stress Leak: Reading a person's true intent instantly",
        "The Pacing Protocol: Hijacking the rhythm of any room",
        "The Visual Interest Read: Detecting attraction or boredom",
        "The Focus Misdirection: Moving attention like a pro mentalist",
        "The Power Identity: Biologically adopting high-status body language",
        "The Exit Intent: Reading feet to know when someone wants to leave",
        "The Compliance Ladder: Getting major favors through small 'Yes' moves"
    ]
    
    selected_topic = random.choice(topics)
    print(f"🧠 ACTIVATING ACCESSIBLE DNA: {selected_topic}...")

    # הנחיות ה-DNA הנגיש: מהשטח אל החיים [cite: 2026-01-01]
    instruction = """
    IDENTITY: You are the Lead Strategist for 'The Brain Lab'. You leak psychological protocols for the EVERYDAY civilian.
    
    THE "ACCESSIBILITY" RULES:
    1. STREET SMART: Apply tactics to work, dating, and social life.
    2. THE "YOU" FACTOR: Explain why this helps the viewer GET status, respect, or results.
    3. ANTI-ACADEMIC: No science talk. Only raw, actionable intelligence.
    4. LANGUAGE: English ONLY. High impact and direct.
    
    FORMAT:
    ANALYSIS: [3 sentences explaining the tactic and its daily application]
    ---TITLE: [Viral cinematic title]
    ---INSIGHT: [The tactical fact for the screen, 7-10 words maximum]
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            config=types.GenerateContentConfig(system_instruction=instruction, temperature=0.7),
            contents=f"Execute an intelligence briefing on: {selected_topic}"
        )
        
        full_text = response.text.strip()
        print(f"\n--- LAB ANALYSIS ---\n{full_text}\n-------------------")
        
        if "---TITLE:" in full_text and "---INSIGHT:" in full_text:
            title = full_text.split("---TITLE:")[1].split("---INSIGHT:")[0].strip()
            insight = full_text.split("---INSIGHT:")[1].strip()
        else:
            title = "Power Protocol"; insight = "Master the room with silent authority"
        
        return " ".join(insight.split()[:10]).upper(), " ".join(title.split()[:10]), selected_topic
    
    except Exception as e:
        print(f"❌ AI BRAIN ERROR: {e}")
        return "SILENCE IS POWER: WAIT 4 SECONDS", "Strategic Silence", selected_topic
