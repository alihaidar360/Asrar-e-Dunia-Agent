"""
modules/voiceover.py
=====================
Script ke Urdu narration ko awaz (audio file) mein convert karta hai.

Tier 1: ElevenLabs   (best quality, free tier ~10K characters/month)
Tier 2: PlayHT       (achi quality, free tier limited)
Tier 3: Edge TTS      (Microsoft, 100% free, unlimited, no API key chahiye)

Edge TTS hamesha kaam karega isliye ye system "kabhi rukta nahi" - guaranteed
fallback hai jo permanently free hai.
"""

import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Edge TTS ki Urdu-capable voices
EDGE_TTS_URDU_VOICES = {
    "male": "ur-PK-AsadNeural",
    "female": "ur-PK-UzmaNeural",
}


def generate_voice_elevenlabs(text: str, api_key: str, output_path: str, voice_id: str = "default"):
    """Tier 1: ElevenLabs se natural, emotional Urdu voice generate karta hai."""
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=api_key)
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
    )
    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    return output_path


def generate_voice_playht(text: str, api_key: str, output_path: str):
    """Tier 2: PlayHT se voice generate karta hai (fallback)."""
    import pyht
    client = pyht.Client(api_key=api_key)
    # PlayHT SDK ka actual usage docs ke mutabiq adjust karna hoga
    audio_stream = client.tts(text=text, voice="urdu_default")
    with open(output_path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)
    return output_path


async def _edge_tts_async(text: str, output_path: str, voice: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def generate_voice_edge_tts(text: str, output_path: str, gender: str = "male"):
    """
    Tier 3: Edge TTS - hamesha available, free, unlimited.
    Ye system ka "safety net" hai - agar Tier 1/2 fail ho jayen, ye kabhi fail nahi hota.
    """
    voice = EDGE_TTS_URDU_VOICES.get(gender, EDGE_TTS_URDU_VOICES["male"])
    asyncio.run(_edge_tts_async(text, output_path, voice))
    return output_path


def generate_voiceover(text: str, output_path: str):
    """
    Master function: config.VOICEOVER_TIERS ke order mein tools try karta hai.
    """
    errors = []

    if "elevenlabs" in config.VOICEOVER_TIERS and config.ELEVENLABS_API_KEY:
        try:
            return {"tier_used": "elevenlabs",
                    "path": generate_voice_elevenlabs(text, config.ELEVENLABS_API_KEY, output_path)}
        except Exception as e:
            errors.append(f"ElevenLabs failed: {e}")

    if "playht" in config.VOICEOVER_TIERS and config.PLAYHT_API_KEY:
        try:
            return {"tier_used": "playht",
                    "path": generate_voice_playht(text, config.PLAYHT_API_KEY, output_path)}
        except Exception as e:
            errors.append(f"PlayHT failed: {e}")

    if "edge_tts" in config.VOICEOVER_TIERS:
        try:
            return {"tier_used": "edge_tts",
                    "path": generate_voice_edge_tts(text, output_path)}
        except Exception as e:
            errors.append(f"Edge TTS failed: {e}")

    raise RuntimeError("Sab voiceover tiers fail ho gaye:\n" + "\n".join(errors))


def get_audio_duration_seconds(audio_path: str) -> float:
    """FFprobe se audio file ki exact duration nikalta hai (video-timing sync ke liye)."""
    import subprocess
    import json as _json
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", audio_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    info = _json.loads(result.stdout)
    return float(info["format"]["duration"])


if __name__ == "__main__":
    print("Voiceover module ready. Tier order:", config.VOICEOVER_TIERS)
    print("Edge TTS Urdu voices available:", EDGE_TTS_URDU_VOICES)
