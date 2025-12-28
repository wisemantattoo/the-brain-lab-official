import os
from google import genai
from google.genai import types

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_KEY)

# הנחיות המערכת (System Instructions) - ה"מוח" של הבוט
instruction = """
אתה המוח האסטרטגי מאחורי 'The Brain Lab Official'. 
תפקידך לייצר תוכן ויראלי קצר ומתוחכם על פסיכולוגיה ושפת גוף.
לפני הכתיבה, נתח מהו הטריגר שיגרום לאנשים לעצור את הגלילה.
פורמט תשובה: Hook: [טקסט] | Description: [טקסט]
"""

print("🧠 שולח שאילתת תוכן למודל: gemini-flash-latest...")

try:
    response = client.models.generate_content(
        model="gemini-flash-latest",
        config=types.GenerateContentConfig(
            system_instruction=instruction,
            temperature=0.8
        ),
        contents="צור הוק ויראלי בן 7 מילים על הנושא: 'איך לזהות שקרים באמצעות שפת גוף'"
    )
    
    print("\n--- תשובת המודל ---")
    print(response.text.strip())
    print("------------------")
    
except Exception as e:
    print(f"❌ הבדיקה נכשלה: {e}")

print("\n🔚 הבדיקה הסתיימה.")
