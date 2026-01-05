import random
from google import genai
from google.genai import types
from modules.config import SECRETS

def get_viral_content():
    """
    יחידת הפרופיילר v2.1: מודל Infinite Discovery.
    ה-AI סורק את מאגר הידע העולמי ושולף מחקר או תופעה מפתיעה בכל פעם.
    FIXED: Robust parsing + model fallback [cite: 2026-01-05]
    """
    
    # אתחול הלקוח בתוך הפונקציה למניעת קריסה בזמן הטעינה
    client = genai.Client(api_key=SECRETS["GEMINI_API_KEY"])
    
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
    4. AUTHORITY: Mention the researcher, study name, or book (e.g., 'Cialdini's rule', 'The Stanford effect').
    5. LANGUAGE: English ONLY. High-impact.
    
    FORMAT (STRICTLY FOLLOW THIS):
    HOOK: [The 3-5 words for the screen]
    GUIDE: [The 2-3 sentences for the description]
    ---TITLE: [Viral YouTube Title]
    """
    
    # רשימת מודלים לנסות (מהחדש לישן)
    models_to_try = [
        "gemini-2.0-flash-thinking-exp-1219",
        "gemini-2.0-flash-exp",
        "gemini-exp-1206",
        "gemini-flash-latest"
    ]
    
    for model_name in models_to_try:
        try:
            print(f"🤖 Trying model: {model_name}")
            response = client.models.generate_content(
                model=model_name, 
                config=types.GenerateContentConfig(
                    system_instruction=instruction, 
                    temperature=0.9
                ),
                contents="Execute an intelligence briefing on a new, surprising discovery."
            )
            
            full_text = response.text.strip()
            print(f"\n--- DISCOVERY BRIEFING ---\n{full_text}\n-------------------")
            
            # Parsing בטוח עם בדיקת שגיאות
            hook, title, guide = parse_response(full_text)
            
            if hook and title and guide:
                print(f"✅ Successfully parsed content!")
                return hook, title, guide
            else:
                print(f"⚠️ Parsing incomplete with {model_name}, trying next model...")
                continue
                
        except Exception as e:
            print(f"⚠️ Model {model_name} failed: {e}")
            continue
    
    # אם כל המודלים נכשלו
    print(f"❌ All models failed. Using fallback content.")
    return get_fallback_content()


def parse_response(full_text):
    """
    מנתח את התגובה מ-AI בצורה בטוחה.
    מחזיר: (hook, title, guide) או (None, None, None) אם נכשל.
    """
    try:
        # חילוץ HOOK
        if "HOOK:" not in full_text or "GUIDE:" not in full_text:
            raise ValueError("Missing HOOK or GUIDE markers")
            
        hook_part = full_text.split("HOOK:")[1].split("GUIDE:")[0].strip()
        
        # חילוץ GUIDE
        if "---TITLE:" not in full_text:
            raise ValueError("Missing TITLE marker")
            
        guide_part = full_text.split("GUIDE:")[1].split("---TITLE:")[0].strip()
        
        # חילוץ TITLE
        title_part = full_text.split("---TITLE:")[1].strip()
        
        # ניקוי (הסרת סימני ציטוט מיותרים)
        hook = hook_part.strip('"\'').upper()
        guide = guide_part.strip('"\'')
        title = title_part.strip('"\'')
        
        # וידוא שאף אחד לא ריק
        if not hook or not guide or not title:
            raise ValueError("Empty field detected")
        
        # וידוא אורך ה-HOOK (לא יותר מדי ארוך)
        if len(hook.split()) > 7:
            print(f"⚠️ Hook too long ({len(hook.split())} words), trimming...")
            hook = ' '.join(hook.split()[:5])
        
        return hook, title, guide
        
    except (IndexError, ValueError, AttributeError) as e:
        print(f"⚠️ Parsing error: {e}")
        print(f"Raw text received:\n{full_text[:500]}...")
        return None, None, None


def get_fallback_content():
    """תוכן גיבוי אם כל המודלים נכשלו"""
    fallback_options = [
        ("THE SILENCE TRAP", 
         "Strategic Silence in Social Dynamics", 
         "Research shows waiting 4 seconds before responding increases perceived authority by 60%. The silence creates tension that positions you as the decision-maker."),
        
        ("THE 3-SECOND RULE", 
         "Instant Charisma Protocol", 
         "FBI behavioral analysis reveals maintaining eye contact for exactly 3 seconds triggers oxytocin release. Any longer feels aggressive, any shorter seems weak."),
        
        ("THE DOOR-IN-FACE", 
         "Cialdini's Rejection Strategy", 
         "Start with an outrageous request. When rejected, your real ask seems reasonable. Studies show 50% higher compliance using this reciprocity exploit.")
    ]
    
    hook, title, guide = random.choice(fallback_options)
    print(f"🔄 Using fallback: {title}")
    return hook, title, guide
