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



# שימוש במודל המנצח ששמור בזיכרון

client = genai.Client(api_key=GEMINI_KEY)



OFFICIAL_DESCRIPTION = """Welcome to The Brain Lab. 🧠

We decode the human mind, one fact at a time. Our mission is to provide you with science-backed insights and actionable protocols to rewire your brain for success, focus, and peak performance.



🔬 Explore the Laboratory: We take complex neuroscience and turn it into simple, daily habits that you can start using today.



⚡ Get Started with Protocol #001: Download our official Morning Protocol to eliminate mental fog and prime your brain for the day: https://thebrainlabofficial.gumroad.com/l/vioono



Subscribe to join the experiment and start decoding your mind."""



def get_viral_content():

    # נושאי מחקר עמוקים יותר [cite: 2025-12-28]

    topics = [

        "The Anchoring Effect in negotiation", "Dopamine reward prediction error", 

        "Loss aversion psychology", "Micro-expressions of contempt",

        "The Zeigarnik Effect on focus", "Neural pathways of social dominance"

    ]

    selected_topic = random.choice(topics)

    print(f"🧠 ANALYZING TACTICAL PROTOCOL: {selected_topic}...")



    # DNA מעודכן: התמקדות בערך עובדתי (Micro-Lesson) [cite: 2025-12-28]

    instruction = """

    ROLE: You are the Lead Neuro-Strategist at The Brain Lab Official. 

    MISSION: Deliver high-stakes psychological value. Do not market. Educate.

    

    STRICT OPERATIONAL RULES:

    1. LANGUAGE: English only.

    2. TACTICAL INSIGHT: Instead of a marketing 'Hook', provide one concrete, actionable psychological fact.

    3. FACT DENSITY: The insight must be a 'Micro-Lesson' that gives the viewer an advantage.

    

    FORMAT:

    ANALYSIS: [Deep 3-sentence scientific breakdown]

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

            contents=f"Extract a tactical psychological protocol from the topic: {selected_topic}"

        )

        

        full_text = response.text.strip()

        print(f"\n--- LAB ANALYSIS ---\n{full_text}\n-------------------")

        

        # חילוץ חכם של התובנה הטקטית

        title = full_text.split("---TITLE:")[1].split("---INSIGHT:")[0].strip() if "---TITLE:" in full_text else "Neuro-Strategy"

        insight = full_text.split("---INSIGHT:")[1].strip() if "---INSIGHT:" in full_text else "Master your neural baseline for focus"

        

        # ניקוי וזיקוק לוידאו [cite: 2025-12-28]

        final_insight = " ".join(insight.split()[:10]).upper()

        final_title = " ".join(title.split()[:10])



        print(f"✨ TACTICAL INSIGHT READY: {final_insight}")

        return final_insight, final_title, selected_topic

    

    except Exception as e:

        print(f"❌ PROTOCOL ERROR: {e}")

        return "LOSS AVERSION: WE FEAR LOSS MORE THAN GAIN", "Brain Economics", selected_topic



def get_background_image(query):

    try:

        url = f"https://api.unsplash.com/photos/random?query={query},minimalist,intelligence&orientation=portrait&client_id={UNSPLASH_KEY}"

        res = requests.get(url).json()

        img_url = res['urls']['regular']

        with open("bg.jpg", 'wb') as f: f.write(requests.get(img_url).content)

        return "bg.jpg"

    except: return None



def create_video():

    insight, title, topic = get_viral_content()

    fps = 25 

    duration = 8 # הגדלתי מעט כדי לתת זמן לקרוא את העובדה

    print(f"🎬 RENDERING TACTICAL SHORT...")

    

    bg_file = get_background_image(topic)

    if bg_file:

        bg = ImageClip(bg_file).set_duration(duration).resize(height=1920)

        bg = bg.crop(x1=bg.w/2-540, y1=0, x2=bg.w/2+540, y2=1920)

    else:

        bg = ColorClip(size=(1080, 1920), color=(15, 15, 15)).set_duration(duration)
        
