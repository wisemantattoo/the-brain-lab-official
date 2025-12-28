import os
from google import genai

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_KEY)

# רשימת המודלים שנבדוק (הכי יציבים ב-Free Tier)
test_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-flash-latest"]

print("🔍 מתחיל בדיקת דופק למודלים...")

for model_name in test_models:
    print(f"\n--- בודק את המודל: {model_name} ---")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'Hello, The Brain Lab!'"
        )
        print(f"✅ הצלחה! המודל ענה: {response.text.strip()}")
    except Exception as e:
        if "429" in str(e):
            print(f"❌ חסימת מכסה (429): המודל לא זמין בחינם כרגע.")
        else:
            print(f"❌ שגיאה אחרת: {e}")

print("\n🔚 הבדיקה הסתיימה.")
