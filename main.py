import os
import json
import requests
import random
from google import genai
from google.genai import types
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, AudioFileClip, ImageClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# 1. משיכת Secrets
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
CLIENT_SECRET_RAW = os.environ.get("CLIENT_SECRET_JSON")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")
TIKTOK_TOKEN = os.environ.get("TIKTOK_ACCESS_TOKEN")
GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

client = genai.Client(api_key=GEMINI_KEY)

OFFICIAL_DESCRIPTION = """Welcome to The Brain Lab. 🧠
We decode the human mind, one fact at a time. Our mission is to provide you with science-backed insights and actionable protocols to rewire your brain for success, focus, and peak performance.

🔬 Explore the Laboratory: We take complex neuroscience and turn it into simple, daily habits that you can start using today.

⚡ Get Started with Protocol #001: Download our official Morning Protocol to eliminate mental fog and prime your brain for the day: https://thebrainlabofficial.gumroad.com/l/vioono

Subscribe to join the experiment and start decoding your mind."""

def get_viral_content():
    # 12 הפרוטוקולים החדשים: NLP, שב"כ ומנטליזם
    topics = [
        "The Interrogator’s Silence: Truth extraction via 4-second pauses",
        "The 'Left Eye' Dominance: NLP command planting via gaze",
        "The False Choice Trap: Mentalist selection deception",
        "The Body Language Baseline: Lie detection in 20 seconds",
        "The Embedded Command: Hidden verbal directives",
        "The Throat Touch Leak: Instant stress and threat detection",
        "The Pacing & Leading Protocol: Hijacking conversation rhythm",
        "The Pupil Dilatation Read: Detecting visceral interest or lies",
        "The Misdirection Hack: Shifting focus to plant suggestions",
        "The Alter Ego Anchor: Biologically adopting a power identity",
        "The Feet Direction Power: Reading the room’s hidden exit intent",
        "The Compliance Trick: Small favors leading to total control"
    ]
    selected_topic = random.choice(topics)
    print(f"🧠 ACTIVATING FIELD PROFILER DNA: {selected_topic}...")

    # הנחיות המערכת החדשות: ללא אקדמיה, רק שטח
    instruction = """
    IDENTITY: You are a Tactical Profiler for 'The Brain Lab'. You don't teach science; you leak intelligence protocols.
    
    THE "ANTI-ACADEMIC" RULES:
    1. STREET TACTICS: Never use words like 'Heuristics', 'Cognitive', or 'Neural'. Use words like 'The Signal', 'The Leak', 'The Trap', 'The Power Move'.
    2. THE 3-SECOND RULE: The insight must be something the viewer can do right now. 
    3. SHABAK VIBE: Every insight should feel like a secret technique used by interrogators or mentalists to exploit human psychology.
    4. LANGUAGE: English ONLY. High impact, raw, and cold.
    
    FORMAT:
    ANALYSIS: [3 sentences of raw tactical intelligence]
    ---TITLE: [Cinematic title for YouTube]
    ---INSIGHT: [The tactical fact for the screen, 7-10 words maximum]
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            config=types.GenerateContentConfig(
                system_instruction=instruction, 
                temperature=0.7
            ),
            contents=f"Execute an intelligence briefing on: {selected_topic}"
        )
        
        full_text = response.text.strip()
        print(f"\n--- INTELLIGENCE BRIEFING ---\n{full_text}\n-------------------")
        
        title = full_text.split("---TITLE:")[1].split("---INSIGHT:")[0].strip() if "---TITLE:" in full_text else "Tactical Protocol"
        insight = full_text.split("---INSIGHT:")[1].strip() if "---INSIGHT:" in full_text else "Master the room with silent authority"
        
        # זיקוק סופי למסך
        final_insight = " ".join(insight.split()[:10]).upper()
        final_title = " ".join(title.split()[:10])

        print(f"✨ FIELD SIGNAL READY: {final_insight}")
        return final_insight, final_
