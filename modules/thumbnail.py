"""
modules/thumbnail.py
======================
Har video ke liye ek curiosity-driven thumbnail banata hai.

Tier 1: AI image generation (DALL-E/Bing Image Creator/Leonardo) se cinematic
        background banwana
Tier 2: PIL-based programmatic design (channel branding ke sath) - guaranteed
        fallback jo kabhi fail nahi hota, jaisa hum ne DP/Banner ke liye banaya
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

THUMB_W, THUMB_H = 1280, 720
GOLD = (212, 175, 55)
GOLD_LIGHT = (238, 210, 130)
NAVY_DARK = (8, 10, 20)


def generate_background_ai(prompt: str, api_key: str, output_path: str):
    """
    Tier 1: AI image generation se background banata hai.
    Prompt mein hamesha 'no real faces, no religious figures' constraint add hota hai.
    """
    safe_prompt = f"{prompt}, cinematic, no human faces, symbolic imagery, historical atmosphere"
    # Actual API call yahan aayegi (jo bhi image-gen service configure ho)
    # Placeholder structure - service-specific SDK docs ke mutabiq complete karna hoga
    raise NotImplementedError("AI image tier abhi configure nahi hui - PIL fallback use hoga")


def generate_background_fallback(output_path: str, seed: int = 0):
    """
    Tier 2: Guaranteed fallback - dark gradient + symbolic historical motif
    (jaisa hum ne channel DP/Banner mein banaya tha), koi external dependency nahi.
    """
    import numpy as np
    import math

    img = np.zeros((THUMB_H, THUMB_W, 3), dtype=np.float64)
    for y in range(THUMB_H):
        t = y / THUMB_H
        for c in range(3):
            img[y, :, c] = NAVY_DARK[c] + (30 - NAVY_DARK[c]) * (1 - t)
    bg = Image.fromarray(img.astype("uint8"))

    draw = ImageDraw.Draw(bg, "RGBA")
    rng = __import__("numpy").random.default_rng(seed)
    for _ in range(120):
        sx, sy = rng.integers(0, THUMB_W), rng.integers(0, THUMB_H)
        b = rng.integers(60, 160)
        draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(b, b, b, 150))

    # symbolic compass/globe motif (off-center, taake text ke liye jagah bache)
    cx, cy, r = int(THUMB_W * 0.75), int(THUMB_H * 0.5), 260
    for frac in [0.35, 0.68]:
        h_ = r * 2 * frac
        draw.ellipse([cx - r, cy - h_ / 2, cx + r, cy + h_ / 2], outline=(*GOLD, 90), width=3)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(*GOLD, 110), width=4)

    bg.save(output_path)
    return output_path


def add_hook_text(background_path: str, hook_text_ur: str, output_path: str):
    """
    Thumbnail par bold curiosity-hook Urdu text overlay karta hai
    (high contrast, mobile-readable size).
    """
    img = Image.open(background_path).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    font = ImageFont.truetype(config.URDU_FONT_PATH, 95, layout_engine=ImageFont.Layout.RAQM)
    bbox = draw.textbbox((0, 0), hook_text_ur, font=font, direction="rtl", language="ur")
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    x = 60 - bbox[0]
    y = (THUMB_H - h) / 2 - bbox[1]

    # Text ke peeche halka dark box (readability ke liye)
    pad = 20
    draw.rectangle([x - pad, y - pad, x + w + pad, y + h + pad], fill=(5, 6, 12, 160))
    draw.text((x, y), hook_text_ur, font=font, fill=GOLD_LIGHT, direction="rtl", language="ur")

    img.save(output_path)
    return output_path


def generate_thumbnail(video_project_id: str, hook_text_ur: str, image_prompt: str = ""):
    """
    Master function: config.THUMBNAIL_TIERS ke order mein background banata hai,
    phir hook-text overlay karke final thumbnail deta hai.
    """
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    bg_path = os.path.join(config.OUTPUT_DIR, f"{video_project_id}_thumb_bg.png")
    final_path = os.path.join(config.OUTPUT_DIR, f"{video_project_id}_thumbnail.png")

    tier_used = "pil_fallback"
    try:
        if "ai_generate" in config.THUMBNAIL_TIERS and config.RUNWAY_API_KEY:
            generate_background_ai(image_prompt, config.RUNWAY_API_KEY, bg_path)
            tier_used = "ai_generate"
        else:
            raise NotImplementedError
    except Exception:
        generate_background_fallback(bg_path, seed=hash(video_project_id) % 1000)

    add_hook_text(bg_path, hook_text_ur, final_path)
    return {"tier_used": tier_used, "path": final_path}


if __name__ == "__main__":
    print("Thumbnail module ready. Tier order:", config.THUMBNAIL_TIERS)
