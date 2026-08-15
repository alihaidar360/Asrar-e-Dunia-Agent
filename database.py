"""
database.py
============
Agent ki "memory" - SQLite database jo teen zaroori cheezein track karta hai:

1. used_clips        -> har video ke andar konsi clip use ho chuki hai (no-repeat rule)
2. covered_topics     -> ab tak konse history topics cover ho chuke (duplicate topic na banay)
3. upload_history      -> kab kya upload hua (scheduler isse decide karta hai aage kya karna hai)

SQLite isliye use ki gayi hai kyunki ye 100% free hai, koi server nahi chahiye,
aur ek single file (.db) mein sab kuch save ho jata hai.
"""

import sqlite3
import os
import datetime
import config


def _connect():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Pehli dafa chalane par tables create karta hai. Baar baar chalana safe hai."""
    conn = _connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS covered_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_title TEXT NOT NULL,
            video_id TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS used_clips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_project_id TEXT NOT NULL,
            clip_source TEXT NOT NULL,
            clip_identifier TEXT NOT NULL,
            used_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS upload_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,   -- 'long_video' ya 'short'
            title TEXT,
            youtube_video_id TEXT,
            uploaded_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# TOPIC TRACKING  (taake wohi topic dobara na bane)
# ---------------------------------------------------------------------------
def is_topic_covered(topic_title: str) -> bool:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) as c FROM covered_topics WHERE LOWER(topic_title) = LOWER(?)",
        (topic_title,),
    )
    count = cur.fetchone()["c"]
    conn.close()
    return count > 0


def mark_topic_covered(topic_title: str, video_id: str = ""):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO covered_topics (topic_title, video_id, created_at) VALUES (?, ?, ?)",
        (topic_title, video_id, datetime.datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# CLIP TRACKING  (taake ek video ke andar koi clip repeat na ho)
# ---------------------------------------------------------------------------
def is_clip_used_in_project(video_project_id: str, clip_identifier: str) -> bool:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """SELECT COUNT(*) as c FROM used_clips
           WHERE video_project_id = ? AND clip_identifier = ?""",
        (video_project_id, clip_identifier),
    )
    count = cur.fetchone()["c"]
    conn.close()
    return count > 0


def mark_clip_used(video_project_id: str, clip_source: str, clip_identifier: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO used_clips (video_project_id, clip_source, clip_identifier, used_at)
           VALUES (?, ?, ?, ?)""",
        (video_project_id, clip_source, clip_identifier, datetime.datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_used_clips_for_project(video_project_id: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT clip_identifier FROM used_clips WHERE video_project_id = ?",
        (video_project_id,),
    )
    rows = [r["clip_identifier"] for r in cur.fetchall()]
    conn.close()
    return set(rows)


# ---------------------------------------------------------------------------
# UPLOAD HISTORY  (scheduler isko dekh kar decide karta hai aage kya karna hai)
# ---------------------------------------------------------------------------
def log_upload(content_type: str, title: str, youtube_video_id: str = ""):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO upload_history (content_type, title, youtube_video_id, uploaded_at)
           VALUES (?, ?, ?, ?)""",
        (content_type, title, youtube_video_id, datetime.datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_last_upload(content_type: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """SELECT * FROM upload_history WHERE content_type = ?
           ORDER BY uploaded_at DESC LIMIT 1""",
        (content_type,),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


if __name__ == "__main__":
    init_db()
    print("Database ready:", config.DATABASE_PATH)
