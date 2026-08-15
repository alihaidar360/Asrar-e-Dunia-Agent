"""
modules/uploader.py
=====================
YouTube Data API v3 se video/Short upload karta hai, aur SEO-friendly
title/description/tags automatically generate karta hai.

Setup zaroori: Google Cloud Console se OAuth credentials (youtube_client_secret.json)
- pehli dafa chalane par browser khulega login/permission ke liye, uske baad
  token save ho jata hai aur agent khud-b-khud upload karta rahega.
"""

import sys
import os
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import database

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_PATH = os.path.join(config.DATA_DIR, "youtube_token.pickle")

# Channel ki fixed SEO keywords (description/tags template mein hamesha shamil)
CORE_KEYWORDS = [
    "world history urdu", "tareekh", "history in urdu", "urdu history channel",
    "qadeem tehzeebein", "history documentary urdu", "asrar e dunia",
]


def get_authenticated_service():
    """
    Google OAuth flow - pehli dafa manual login chahiye hoga, uske baad
    token.pickle se automatically authenticate hoga.
    """
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.YOUTUBE_CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def build_seo_description(topic_title: str, is_short: bool = False):
    """Har video ke liye consistent, SEO-optimized description banata hai."""
    intro = (
        f"{topic_title} - Asrar-e-Dunia par دنیا کی تاریخ کے وہ واقعات جو شاید "
        f"آپ نے پہلے نہیں سنے۔ تحقیق شدہ، دلچسپ، اور مکمل اردو میں۔"
    )
    body = (
        "\n\n🌍 اس چینل پر آپ کو ملے گا:\n"
        "- دنیا کی قدیم و جدید تاریخ کے بڑے واقعات\n"
        "- بادشاہتوں، جنگوں اور تہذیبوں کی کہانیاں\n"
        "- حیرت انگیز اور کم معلوم حقائق\n\n"
        "سبسکرائب کریں تاکہ کوئی قسط مس نہ ہو۔\n\n"
        f"#{'Shorts ' if is_short else ''}#AsrarEDunia #WorldHistory #UrduHistory"
    )
    return intro + body


def build_seo_tags(topic_title: str):
    words = [w.strip() for w in topic_title.split() if len(w.strip()) > 2]
    return list(dict.fromkeys(CORE_KEYWORDS + words))[:15]  # duplicates hata kar max 15 tags


def upload_video(video_path: str, thumbnail_path: str, topic_title: str,
                  is_short: bool = False, category_id: str = "27"):  # 27 = Education
    """
    Master function: video upload karta hai, SEO metadata attach karta hai,
    thumbnail set karta hai, aur database mein log karta hai.
    """
    from googleapiclient.http import MediaFileUpload

    youtube = get_authenticated_service()

    title = topic_title if not is_short else f"{topic_title} #Shorts"
    description = build_seo_description(topic_title, is_short)
    tags = build_seo_tags(topic_title)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "ur",
            "defaultAudioLanguage": "ur",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    video_id = response["id"]

    # Thumbnail set karo
    if thumbnail_path and os.path.exists(thumbnail_path):
        youtube.thumbnails().set(
            videoId=video_id, media_body=MediaFileUpload(thumbnail_path)
        ).execute()

    # Database mein log karo (scheduler ke liye zaroori)
    content_type = "short" if is_short else "long_video"
    database.log_upload(content_type, title, video_id)
    database.mark_topic_covered(topic_title, video_id)

    return {"video_id": video_id, "title": title, "url": f"https://youtube.com/watch?v={video_id}"}


if __name__ == "__main__":
    print("Uploader module ready.")
    print("Core SEO keywords:", CORE_KEYWORDS)
