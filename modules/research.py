"""
modules/research.py
====================
Ye module YouTube par trending history topics dhoondta hai, aur database
se check karta hai ke kaunsa topic pehle se cover ho chuka hai (duplicate na ho).

Zaroori: YouTube Data API v3 ki free API key chahiye hogi (Google Cloud Console se,
free tier mein 10,000 units/day milte hain jo rozana ke research ke liye kaafi hai).
"""

import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

# Broad seed categories - agent inhe rotate karke research karega
SEED_CATEGORIES = [
    "ancient civilizations history",
    "world war history documentary",
    "islamic history events",
    "science history discoveries",
    "lost cities mystery",
    "ancient empires rise and fall",
    "unsolved historical mysteries",
    "medieval history battles",
]


def search_trending_topics(youtube_api_key: str, query: str, max_results: int = 10):
    """
    YouTube search API se ek query ke liye top/trending results laata hai.
    Views aur recency dono ka combined signal deta hai.
    """
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "maxResults": max_results,
        "key": youtube_api_key,
        "relevanceLanguage": "en",  # English mein trending dekh kar Urdu gap nikalte hain
    }
    try:
        resp = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "channel": item["snippet"]["channelTitle"],
                "video_id": item["id"]["videoId"],
            })
        return results
    except requests.RequestException as e:
        print(f"[research.py] YouTube API error: {e}")
        return []


def filter_uncovered_topics(candidate_topics: list):
    """Database check karta hai - jo topics already cover ho chuke unhe hata deta hai."""
    fresh_topics = []
    for topic in candidate_topics:
        if not database.is_topic_covered(topic["title"]):
            fresh_topics.append(topic)
    return fresh_topics


def get_next_research_batch(youtube_api_key: str, category_index: int = 0):
    """
    Ek category se fresh (uncovered) topics ki list laata hai.
    main.py/scheduler is function ko call karke agla topic decide karta hai.
    """
    category = SEED_CATEGORIES[category_index % len(SEED_CATEGORIES)]
    raw_results = search_trending_topics(youtube_api_key, category)
    fresh = filter_uncovered_topics(raw_results)
    return {
        "category_used": category,
        "candidates": fresh,
    }


if __name__ == "__main__":
    # Demo run (API key config.py se aayegi)
    import config
    if not config.CLAUDE_API_KEY:
        print("Note: Ye sirf structure test hai. Asal research ke liye YOUTUBE_API_KEY set karo.")
    print("Seed categories ready:", SEED_CATEGORIES)
