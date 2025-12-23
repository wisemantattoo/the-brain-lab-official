import os
import json
import time
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

# --- הלינק שלך ---
GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

# --- מאגר עובדות לחודשיים (60 עובדות) ---
facts = [
    "Psychology says: Your brain does more creative work when you are tired.",
    "Smart people tend to have fewer friends than the average person.",
    "The way you dress is linked to your mood.",
    "Pretending not to care is the habit of someone who generally cares the most.",
    "The type of music you listen to affects the way you perceive the world.",
    "Your brain treats rejection like physical pain.",
    "If you announce your goals to others, you are less likely to make them happen.",
    "90% of people text things they can't say in person.",
    "Singing reduces feelings of anxiety and depression.",
    "Your favorite song is likely associated with an emotional event.",
    "Sarcasm is a sign of a healthy brain.",
    "We are the most imaginative in the night and the least creative in the day.",
    "It takes about 66 days for an average individual to make a new habit.",
    "People who try to keep everyone happy often end up feeling the loneliest.",
    "The happier you are, the less sleep you require.",
    "Being with positive and happy people makes you happier.",
    "Eating chocolate discharges the same chemical into your body as falling in love.",
    "Men are not funnier than women: they just make more jokes, not caring if people like it.",
    "People look more attractive when they speak about the things they are really interested in.",
    "When you hold the hand of a loved one, you feel less pain and worry.",
    "Intelligent people tend to have a messier desk.",
    "People who swear a lot tend to be more loyal, open, and honest.",
    "Liars usually have more eye contact than truth-tellers.",
    "Traveling boosts brain health and also decreases a person's risk of heart attack and depression.",
    "Hearing your name when no one is calling you is a sign of a healthy mind.",
    "You can't read in a dream because reading and dreaming are functions of different sides of the brain.",
    "Talking to yourself can actually make you smarter.",
    "Your brain can't lie to you about who you love.",
    "Good liars are also good at detecting lies from others.",
    "Thinking in a second language forces you to make more rational decisions.",
    "Spending money on others yields more happiness than spending it on yourself.",
    "The very last person on your mind before you fall asleep is either the reason for your happiness or your pain.",
    "Comedians and funny people are actually more depressed than others.",
    "People with high self-esteem are more likely to stay in a relationship.",
    "When you sneeze, your brain shuts down for a microsecond.",
    "Your brain uses 20% of the total oxygen and blood in your body.",
    "Multitasking is impossible; your brain just switches tasks very quickly.",
    "You are more likely to remember something if you write it down.",
    "The smell of chocolate increases theta brain waves, which triggers relaxation.",
    "People who sleep on their stomach have more intense dreams.",
    "Your brain continues to develop until your late 40s.",
    "Being ignored causes the same chemical
