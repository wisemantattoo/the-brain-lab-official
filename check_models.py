import google.generativeai as genai
import os

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
print("🔍 Checking available models for your API Key...")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Available model: {m.name}")
except Exception as e:
    print(f"❌ Error: {e}")
