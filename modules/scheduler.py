"""
modules/scheduler.py
======================
Ye decide karta hai AAJ agent ko kya karna hai:
- Long video banani/upload karni hai? (har 3 din)
- Shorts banane/upload karne hain? (har 2 din, 3 ki batch)

Logic database ke "upload_history" table ko dekh kar last upload ka time
nikalta hai aur config.SCHEDULE ke intervals se compare karta hai.
"""

import sys
import os
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import database


def days_since(iso_timestamp: str) -> float:
    last = datetime.datetime.fromisoformat(iso_timestamp)
    delta = datetime.datetime.now() - last
    return delta.total_seconds() / 86400


def should_make_long_video() -> bool:
    """Har 3 din mein 1 dafa True return karta hai."""
    last = database.get_last_upload("long_video")
    if last is None:
        return True  # Pehli dafa - shuru karo
    return days_since(last["uploaded_at"]) >= config.SCHEDULE["long_video_every_n_days"]


def should_make_shorts() -> bool:
    """Har 2 din mein 1 dafa True return karta hai."""
    last = database.get_last_upload("short")
    if last is None:
        return True
    return days_since(last["uploaded_at"]) >= config.SCHEDULE["shorts_every_n_days"]


def get_today_tasks() -> dict:
    """
    Master function - aaj ke liye agent ko konse tasks karne hain, wo
    dictionary ke roop mein return karta hai. main.py isko call karega.
    """
    tasks = {
        "make_long_video": should_make_long_video(),
        "make_shorts": should_make_shorts(),
    }
    return tasks


if __name__ == "__main__":
    database.init_db()
    print("Aaj ke tasks:", get_today_tasks())
