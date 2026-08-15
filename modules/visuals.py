"""
modules/visuals.py
====================
Har scene-block ke "visual_tag" ke liye ek matching video clip dhoondta hai.

ZAROORI RULE: Ek video project ke andar koi bhi clip DOBARA use nahi hogi.
Ye database.py ke "used_clips" table se check hota hai.

Tier order:
1. Pexels        (free stock footage)
2. Pixabay       (free stock footage)
3. Archive.org   (public domain historical footage)
4. AI-generate   (Runway/Pika) - jab stock footage mein kuch match/unique na mile
"""

import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import database

PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"
PIXABAY_SEARCH_URL = "https://pixabay.com/api/videos/"


def search_pexels(query: str, api_key: str, per_page: int = 15):
    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": per_page, "orientation": "landscape"}
    resp = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return [
        {"source": "pexels", "id": str(v["id"]), "url": v["video_files"][0]["link"]}
        for v in data.get("videos", [])
    ]


def search_pixabay(query: str, api_key: str, per_page: int = 15):
    params = {"key": api_key, "q": query, "per_page": per_page}
    resp = requests.get(PIXABAY_SEARCH_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return [
        {"source": "pixabay", "id": str(v["id"]), "url": v["videos"]["large"]["url"]}
        for v in data.get("hits", [])
    ]


def generate_ai_clip_runway(prompt: str, api_key: str, output_path: str):
    """
    Tier 4: Jab koi stock clip unique/available na ho, Runway ML se
    naya AI video clip generate karta hai. Har clip prompt ki wajah se
    guaranteed unique hoti hai - isse repeat ka masla khatam ho jata hai.
    """
    import runwayml
    client = runwayml.RunwayML(api_key=api_key)
    task = client.image_to_video.create(
        model="gen3a_turbo",
        prompt_text=prompt,
    )
    # Poora implementation Runway ke async task-polling docs ke mutabiq karna hoga
    return {"source": "runway_ai", "id": task.id, "path": output_path}


def find_unique_clip_for_scene(video_project_id: str, visual_tag: str):
    """
    Master function - ek scene-block ke liye EK unique clip dhoondta hai jo
    is video project mein pehle kabhi use nahi hui.

    Logic:
    1. Pexels mein search karo -> pehla unused result lo
    2. Nahi mila -> Pixabay try karo
    3. Nahi mila -> AI-generate karo (hamesha unique, kyunki naya banta hai)
    """
    used_clips = database.get_used_clips_for_project(video_project_id)

    # Tier 1: Pexels
    if config.PEXELS_API_KEY:
        try:
            results = search_pexels(visual_tag, config.PEXELS_API_KEY)
            for clip in results:
                unique_id = f"pexels_{clip['id']}"
                if unique_id not in used_clips:
                    database.mark_clip_used(video_project_id, "pexels", unique_id)
                    return {"tier_used": "pexels", **clip}
        except Exception as e:
            print(f"[visuals.py] Pexels search failed: {e}")

    # Tier 2: Pixabay
    if config.PIXABAY_API_KEY:
        try:
            results = search_pixabay(visual_tag, config.PIXABAY_API_KEY)
            for clip in results:
                unique_id = f"pixabay_{clip['id']}"
                if unique_id not in used_clips:
                    database.mark_clip_used(video_project_id, "pixabay", unique_id)
                    return {"tier_used": "pixabay", **clip}
        except Exception as e:
            print(f"[visuals.py] Pixabay search failed: {e}")

    # Tier 3/4: AI-generate (hamesha unique hota hai, kabhi repeat nahi hoga)
    if config.RUNWAY_API_KEY:
        try:
            output_path = os.path.join(config.OUTPUT_DIR, f"ai_clip_{video_project_id}_{visual_tag[:20]}.mp4")
            clip = generate_ai_clip_runway(visual_tag, config.RUNWAY_API_KEY, output_path)
            unique_id = f"runway_{clip['id']}"
            database.mark_clip_used(video_project_id, "runway_ai", unique_id)
            return {"tier_used": "runway_ai", **clip}
        except Exception as e:
            print(f"[visuals.py] AI generation failed: {e}")

    raise RuntimeError(
        f"'{visual_tag}' ke liye koi unique clip nahi mil saki - "
        f"sab stock aur AI sources exhaust ho gaye ya API keys missing hain."
    )


if __name__ == "__main__":
    print("Visuals module ready. Tier order:", config.VISUALS_TIERS)
