import random
from google import genai
from google.genai import types
from modules.config import SECRETS

client = genai.Client(api_key=SECRETS["GEMINI_KEY"])

def get_viral_content():
    """
    יחידת הפרופיילר v2.0: מודל Infinite Discovery.
    ה-AI סורק את מאגר הידע העולמי ושולף מחקר או תופעה מפתיעה בכל פעם [cite: 2026-01-01].
    """
    
    domains = [
        "Behavioral Economics (Nudge theory, Decision making)",
        "Social Psychology (Influence, Conformity, Group dynamics)",
        "Neuroscience (Dopamine loops, Brain plasticity, Stress response)",
        "Dark Psychology (Manipulation detection, Body language, FBI tactics)",
        "Evolutionary Psychology (Survival instincts, Status seeking, Attraction)",
        "Cognitive Biases (Kahneman/Tversky expanded research)",
        "Peak Performance (Flow state, Atomic habits, Mental toughness)"
    ]
    
    selected_domain = random.choice(domains)
    print(f"🧠 SEARCHING INFINITE ARCHIVE: {selected_domain}...")

    instruction = f"""
    IDENTITY: Chief Researcher for 'The Brain Lab'.
    MISSION: Discover an obscure but high-impact psychological study, academic concept, or human behavior protocol.
    SOURCE DOMAIN: {selected_domain}
    
    RULES:
    1. DISCOVERY: Find something specific and surprising. Don't repeat common knowledge. 
    2. THE HOOK (Video): 3-5 words max. High-stakes or mysterious. 
    3. THE GUIDE (Description): 2-3 sentences. A raw, actionable 'Social Software Update' based on the research.
    4. AUTHORITY: Mention the researcher, study name, or book (e.g., 'Cialdini’s rule', 'The Stanford effect').
    5. LANGUAGE: English ONLY. High-impact.
    
    FORMAT:
    HOOK: [The 3-5 words for the screen]
    GUIDE: [The 2-3 sentences for the description]
    ---TITLE: [Viral YouTube Title]
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            config=types.GenerateContentConfig(system_instruction=instruction, temperature=0.9),
            contents="Execute an intelligence briefing on a new, surprising discovery."
        )
        
        full_text = response.text.strip()
        print(f"\n--- DISCOVERY BRIEFING ---\n{full_text}\n-------------------")
        
        hook = full_text.split("HOOK:")[1].split("GUIDE:")[0].strip()
        guide = full_text.split("GUIDE:")[1].split("---TITLE:")[0].strip()
        title = full_text.split("---TITLE:")[1].strip()
        
        return hook.upper(), title, guide
    
    except Exception as e:
        print(f"❌ AI BRAIN ERROR: {e}")
        return "THE POWER OF SILENCE", "Strategic Silence", "Wait 4 seconds before reacting to gain dominance."
