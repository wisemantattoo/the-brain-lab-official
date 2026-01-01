import os

# 1. מפתחות וסיקרטים (Secrets)
SECRETS = {
    "GEMINI_KEY": os.environ.get("GEMINI_API_KEY"),
    "UNSPLASH_KEY": os.environ.get("UNSPLASH_ACCESS_KEY"),
    "CLIENT_SECRET_RAW": os.environ.get("CLIENT_SECRET_JSON"),
    "REFRESH_TOKEN": os.environ.get("YOUTUBE_REFRESH_TOKEN"),
    "TIKTOK_TOKEN": os.environ.get("TIKTOK_ACCESS_TOKEN")
}

# 2. לינקים והגדרות ערוץ
GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

OFFICIAL_DESCRIPTION = """Welcome to The Brain Lab. 🧠
We decode high-stakes human intelligence into daily protocols. Our mission is to give you the psychological edge in career, social influence, and mental performance.

🔬 The Laboratory: We translate elite psychological tactics into simple habits you can use today.

⚡ Get Started with Protocol #001: Download our official Morning Protocol here: https://thebrainlabofficial.gumroad.com/l/vioono

Subscribe to join the experiment and start decoding your mind."""
