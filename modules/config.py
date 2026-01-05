import os

SECRETS = {
    "GEMINI_KEY": os.environ.get("GEMINI_API_KEY"),
    "UNSPLASH_KEY": os.environ.get("UNSPLASH_ACCESS_KEY"),
    # המפתחות החדשים והבטוחים של גוגל [cite: 2026-01-05]
    "CLIENT_ID": os.environ.get("GOOGLE_CLIENT_ID"),
    "CLIENT_SECRET": os.environ.get("GOOGLE_CLIENT_SECRET"),
    "REFRESH_TOKEN": os.environ.get("YOUTUBE_REFRESH_TOKEN"),
    # שמירה על נתוני הטיקטוק שלך [cite: 2025-12-26]
    "TIKTOK_KEY": os.environ.get("TIKTOK_CLIENT_KEY"),
    "TIKTOK_SECRET": os.environ.get("TIKTOK_CLIENT_SECRET")
}

GUMROAD_LINK = "https://thebrainlabofficial.gumroad.com/l/vioono"

# החתימה החדשה והחזקה שבחרת
OFFICIAL_DESCRIPTION = """---
Master the psychology others ignore. 🧠
⚡ Get the full protocol here: https://thebrainlabofficial.gumroad.com/l/vioono"""
