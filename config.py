"""
config.py
=========
Ye poore "Asrar-e-Dunia" AI agent ka control center hai.
Sab API keys, tool priorities (tiers), aur channel rules yahan set hote hain.

ZAROORI: Apni API keys neeche ".env" style variables mein daalain.
Kabhi bhi ye file GitHub par public mat karna (keys leak ho sakti hain).
"""

import os

# ---------------------------------------------------------------------------
# 1) API KEYS  (khali chhoro agar wo tool abhi tak signup nahi hua)
# ---------------------------------------------------------------------------
# Script Writing (LLM) Tier
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")        # Tier 1
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")        # Tier 2
# Tier 3 (Ollama/Llama) ko API key ki zaroorat nahi - local chalta hai

# Voiceover Tier
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")  # Tier 1
PLAYHT_API_KEY = os.getenv("PLAYHT_API_KEY", "")           # Tier 2
# Tier 3 (Edge TTS) ko bhi API key nahi chahiye - free & unlimited

# Visuals / Video Clips Tier
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")        # Stock footage (free)
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")      # Stock footage (free)
RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY", "")        # AI video Tier 1
PIKA_API_KEY = os.getenv("PIKA_API_KEY", "")            # AI video Tier 2

# YouTube Upload
YOUTUBE_CLIENT_SECRETS_FILE = "youtube_client_secret.json"  # Google Cloud Console se download hogi

# ---------------------------------------------------------------------------
# 2) TIER PRIORITY LISTS
#    Agent har module mein pehle Tier 1 try karega, fail/quota-exceed hone
#    par khud-b-khud agle tier par chala jayega.
# ---------------------------------------------------------------------------
SCRIPT_WRITER_TIERS = ["claude", "gemini", "local_llama"]
VOICEOVER_TIERS = ["elevenlabs", "playht", "edge_tts"]
VISUALS_TIERS = ["pexels", "pixabay", "archive_org", "ai_generate"]
THUMBNAIL_TIERS = ["ai_generate", "canva_style_pil"]

# ---------------------------------------------------------------------------
# 3) CHANNEL IDENTITY
# ---------------------------------------------------------------------------
CHANNEL_NAME = "Asrar-e-Dunia"
CHANNEL_LANGUAGE = "ur"          # Urdu
CHANNEL_NICHE = "world_history"  # islamic + general + science + wars + mysteries

# ---------------------------------------------------------------------------
# 4) CONTENT SAFETY RULES  (kabhi cross nahi karni)
# ---------------------------------------------------------------------------
CONTENT_RULES = {
    "no_religious_figure_depiction": True,   # Sahaba/Ambiya/etc ki face kabhi generate nahi
    "no_real_person_face_without_source": True,
    "require_multi_source_fact_check": True,
    "neutral_tone_for_comparative_religion": True,
    "min_sources_per_script": 2,
}

# ---------------------------------------------------------------------------
# 5) VIDEO SPECS
# ---------------------------------------------------------------------------
LONG_VIDEO_MIN_MINUTES = 20
LONG_VIDEO_MAX_MINUTES = 30
SHORT_VIDEO_MAX_SECONDS = 60
SCENE_BLOCK_SECONDS = 12          # har scene-block ka average duration (clip-matching ke liye)

# ---------------------------------------------------------------------------
# 6) UPLOAD SCHEDULE (jaisa discuss hua)
# ---------------------------------------------------------------------------
# Cycle: har 2 din -> 3 Shorts | har 3 din -> 1 Long Video
# LCM(2,3) = 6 din ka combined cycle
SCHEDULE = {
    "shorts_every_n_days": 2,
    "shorts_per_batch": 3,
    "long_video_every_n_days": 3,
    "cycle_length_days": 6,
}

# ---------------------------------------------------------------------------
# 7) PATHS
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(ASSETS_DIR, "output")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
DATABASE_PATH = os.path.join(DATA_DIR, "agent_memory.db")

URDU_FONT_PATH = os.path.join(FONTS_DIR, "urdu_font.ttf")  # Nastaliq/Naskh font yahan rakho
