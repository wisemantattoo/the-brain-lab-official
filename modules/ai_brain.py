import random
from google import genai
from google.genai import types
from modules.config import SECRETS

# ייבוא רשימת ה-hooks המוכחים
try:
    from winning_hooks import PROVEN_HOOKS, get_random_proven_hook
    HOOKS_AVAILABLE = True
except ImportError:
    HOOKS_AVAILABLE = False
    print("⚠️ winning_hooks.py not found, using fallback only")


def get_viral_content():
    """
    יחידת הפרופיילר v4.0: Data-Driven with REAL YouTube Analytics.
    מבוסס על ניתוח 55 סרטונים אמיתיים [2026-01-07].
    
    אסטרטגיה:
    - 80% מהזמן: בוחר מרשימה של 30 hooks מוכחים
    - 20% מהזמן: AI ממציא חדש (עם כללים מחמירים)
    """
    
    # 80% סיכוי לבחור מהרשימה המוכחת
    if HOOKS_AVAILABLE and random.random() < 0.8:
        print("🎯 Selecting from PROVEN hooks library...")
        hook, title, guide = get_random_proven_hook()
        print(f"✅ Selected proven content: {title}")
        return hook, title, guide
    
    # 20% סיכוי - AI ממציא (או fallback אם אין רשימה)
    print("🤖 AI generating new content with strict rules...")
    
    client = genai.Client(api_key=SECRETS["GEMINI_API_KEY"])
    
    # הכללים החדשים - מבוססים על 55 סרטונים אמיתיים!
    instruction = """
    IDENTITY: Chief Researcher for 'The Brain Lab'.
    MISSION: Create viral Short based on PROVEN data from 55 real videos.
    
    🔥 CRITICAL RULES (Based on REAL YouTube Analytics):
    
    1. THE HOOK (Video Screen Text):
       - MUST use ONE of these PROVEN formats:
         * "BRAIN FACT: [Short Statement]" (440 avg views - 104% better!)
         * "PSYCHOLOGY FACT: [Short Statement]" (2,044 avg views - BEST!)
         * "SOCIAL INTELLIGENCE: [Short Statement]" (287 avg views)
       
       - Examples that ACTUALLY WORKED:
         * "BRAIN FACT: Fewer Friends" ✅ (part of 2,246 view video)
         * "BRAIN FACT: Pretending Not To Care" ✅ (1,943 views)
         * "BRAIN FACT: Sharper Dreams" ✅ (352 views)
       
       - Hook should be 4-6 words AFTER the prefix
       - Focus on: Smart people, Brain patterns, Intelligence signals
       
    2. THE TITLE (YouTube Title):
       - MUST include: [Prefix]: [Full statement] #TheBrainLab
       - #TheBrainLab is MANDATORY (104% better performance!)
       - Total: 8-10 words + hashtag
       
       - PROVEN patterns:
         * "Brain Fact: [Intelligence trait]... #TheBrainLab"
         * "Amazing Psychology Fact: Smart people [behavior]... #TheBrainLab"
         * "Psychology says: [Pattern]... #TheBrainLab"
       
       - Examples that WORKED:
         * "Brain Fact: Pretending not to care is the habit of someone who cares deeply... #TheBrainLab"
         * "Amazing Psychology Fact: Smart people tend to have fewer friends than average... #TheBrainLab"
       
    3. THE GUIDE (Description):
       - 2-3 sentences MAX
       - Format: "[Scientific fact/research]. [What it means/application]."
       - MUST sound authoritative but accessible
       - Include words like: research, studies, neuroscience, brain
       
    4. WINNING THEMES (Use these topics - they're PROVEN):
       - Smart people behaviors ⭐⭐⭐ (TOP PERFORMER)
       - Pretending/emotional masking ⭐⭐⭐
       - Brain patterns & intelligence ⭐⭐
       - Social intelligence signals ⭐⭐
       - Learning & cognitive abilities ⭐
    
    5. POWER WORDS (Use these - they appear in top videos):
       - brain, smart, people, intelligence, fact
       - pretending, habit, sharper, more, your
    
    6. AVOID:
       - Generic statements without prefix
       - "THE [NOUN]" format (old system - doesn't work as well)
       - Body language focus (unless combined with intelligence)
       - Overly complex or vague statements
    
    LANGUAGE: English ONLY.
    
    STRICT OUTPUT FORMAT:
    HOOK: [Format MUST be "BRAIN FACT:" or "PSYCHOLOGY FACT:" + short statement]
    GUIDE: [2-3 sentences with research/science backing]
    ---TITLE: [Full title with #TheBrainLab at the end]
    
    EXAMPLES OF CORRECT OUTPUT:
    
    HOOK: BRAIN FACT: Overthinking
    GUIDE: Neuroscience shows intelligent brains process more variables simultaneously. This mental hyperactivity is actually advanced cognitive function, not anxiety.
    ---TITLE: Brain Fact: Overthinking is a sign of high intelligence... #TheBrainLab
    
    IMPORTANT: If you don't follow these EXACT formats, the content will fail!
    """
    
    # רשימת מודלים לנסות
    models_to_try = [
        "gemini-2.0-flash-thinking-exp-1219",
        "gemini-2.0-flash-exp",
        "gemini-flash-latest"
    ]
    
    for model_name in models_to_try:
        try:
            print(f"🤖 Trying model: {model_name}")
            response = client.models.generate_content(
                model=model_name, 
                config=types.GenerateContentConfig(
                    system_instruction=instruction, 
                    temperature=0.85
                ),
                contents="Generate a viral psychology insight about smart people or intelligence."
            )
            
            full_text = response.text.strip()
            print(f"\n--- AI GENERATION ---\n{full_text}\n-------------------")
            
            hook, title, guide = parse_response(full_text)
            
            if hook and title and guide:
                # בדיקת איכות מחמירה יותר
                if validate_new_rules(hook, guide, title):
                    print(f"✅ AI content validated!")
                    return hook, title, guide
                else:
                    print(f"⚠️ Content didn't pass validation, trying next model...")
                    continue
            else:
                print(f"⚠️ Parsing failed, trying next model...")
                continue
                
        except Exception as e:
            print(f"⚠️ Model {model_name} failed: {e}")
            continue
    
    # Fallback - בוחר מהרשימה המוכחת
    print(f"❌ AI generation failed. Using proven fallback.")
    return get_proven_fallback()


def parse_response(full_text):
    """מנתח את התגובה של ה-AI"""
    try:
        if "HOOK:" not in full_text or "GUIDE:" not in full_text:
            raise ValueError("Missing HOOK or GUIDE markers")
            
        hook_part = full_text.split("HOOK:")[1].split("GUIDE:")[0].strip()
        
        if "---TITLE:" not in full_text:
            raise ValueError("Missing TITLE marker")
            
        guide_part = full_text.split("GUIDE:")[1].split("---TITLE:")[0].strip()
        title_part = full_text.split("---TITLE:")[1].strip()
        
        # ניקוי
        hook = hook_part.strip('"\'').upper()
        guide = guide_part.strip('"\'')
        title = title_part.strip('"\'')
        
        if not hook or not guide or not title:
            raise ValueError("Empty field detected")
        
        return hook, title, guide
        
    except (IndexError, ValueError, AttributeError) as e:
        print(f"⚠️ Parsing error: {e}")
        return None, None, None


def validate_new_rules(hook, guide, title):
    """
    בדיקת איכות מבוססת על הכללים החדשים (55 סרטונים)
    """
    issues = []
    
    # בדיקה 1: Hook מתחיל עם הפורמט הנכון?
    valid_prefixes = ["BRAIN FACT:", "PSYCHOLOGY FACT:", "SOCIAL INTELLIGENCE:"]
    has_valid_prefix = any(hook.startswith(prefix) for prefix in valid_prefixes)
    
    if not has_valid_prefix:
        issues.append(f"Hook must start with: {', '.join(valid_prefixes)}")
    
    # בדיקה 2: Title כולל #TheBrainLab?
    if "#TheBrainLab" not in title and "#thebrainlab" not in title.lower():
        issues.append("Title MUST include #TheBrainLab hashtag")
    
    # בדיקה 3: Title לא ארוך מדי?
    title_words = len(title.replace("#TheBrainLab", "").split())
    if title_words > 15:
        issues.append(f"Title too long: {title_words} words (max 12 + hashtag)")
    
    # בדיקה 4: Guide לא ארוך מדי?
    guide_sentences = guide.split('. ')
    if len(guide_sentences) > 4:
        issues.append(f"Guide too long: {len(guide_sentences)} sentences (max 3)")
    
    # בדיקה 5: האם יש מילות כוח?
    power_words = ['brain', 'smart', 'intelligence', 'research', 'studies', 'neuroscience', 'people']
    text_lower = (hook + title + guide).lower()
    has_power_words = any(word in text_lower for word in power_words)
    
    if not has_power_words:
        issues.append(f"Content should include power words: {', '.join(power_words[:3])}")
    
    # אם יש בעיות - הדפס
    if issues:
        print("⚠️ Validation issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    return True


def get_proven_fallback():
    """
    תוכן גיבוי מבוסס על הסרטונים המצליחים ביותר מהדאטא
    """
    if HOOKS_AVAILABLE:
        return get_random_proven_hook()
    
    # אם אין גישה לקובץ - fallback קשיח
    proven_winners = [
        (
            "BRAIN FACT: Fewer Friends",
            "Brain Fact: Smart people tend to have fewer friends than average... #TheBrainLab",
            "Research shows highly intelligent people prefer deep connections over many superficial ones. Their brains process relationships differently, prioritizing quality over quantity."
        ),
        (
            "BRAIN FACT: Pretending Not To Care",
            "Brain Fact: Pretending not to care is the habit of someone who cares deeply... #TheBrainLab",
            "This emotional masking is a protective mechanism. Ironically, the more someone pretends not to care, the more they actually do."
        ),
        (
            "BRAIN FACT: Sharper Dreams",
            "Brain Fact: The sharper your brain, the more you dream... #TheBrainLab",
            "Neuroscientists discovered higher cognitive function correlates with more vivid dreams. Your brain stays active processing information even during sleep."
        ),
        (
            "BRAIN FACT: Optimism Learned",
            "Brain Fact: Optimism can be learned... #TheBrainLab",
            "Neuroplasticity research shows you can rewire your brain's response patterns. Optimism is a trainable skill, not just a personality trait."
        ),
        (
            "SOCIAL INTELLIGENCE: Waiter Test",
            "Social Intelligence: The way you treat a waiter reveals your true character... #TheBrainLab",
            "Behavioral psychologists use this as a key indicator. How someone treats those who can't benefit them shows their real personality."
        )
    ]
    
    hook, title, guide = random.choice(proven_winners)
    print(f"🔄 Using hardcoded fallback: {title}")
    return hook, title, guide
