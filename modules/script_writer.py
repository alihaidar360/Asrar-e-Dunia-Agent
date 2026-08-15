"""
modules/script_writer.py
=========================
Ye module topic leta hai aur ek poora Urdu script generate karta hai, jo
"scene-blocks" mein divided hota hai. Har block ke sath ek "visual_tag" hota
hai jo batata hai us waqt video mein kya dikhna chahiye (clip-matching ke liye).

Tier fallback: Claude -> Gemini -> Local Llama (jo bhi available/working ho)
"""

import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

SYSTEM_PROMPT = """
Tum ek professional Urdu history scriptwriter ho. Tumhara kaam hai world-history
based, story-format YouTube script likhna, jo curiosity aur twists se bhara ho.

SAKHT QAWAID (kabhi na todna):
1. Kisi Nabi, Sahabi, ya kisi bhi mazhabi shakhsiyat ki shakl/tasveer ka zikr
   visual tags mein na karo (sirf symbolic imagery: maps, artifacts, landscapes).
2. Har fact do se zyada independent sources se verify shuda hona chahiye.
3. Comparative-religion topics par mukammal neutral, respectful tone rakho.
4. Script ko chote "scene blocks" mein todo, har block ~10-15 second ka.
5. Har 3-5 minute (yani har ~20-25 blocks) ke baad ek "twist" ya "cliffhanger" ho.

OUTPUT FORMAT: Sirf valid JSON array do, har item is shape mein:
{
  "block_id": 1,
  "narration_ur": "...",       // Urdu mein bola jane wala text
  "visual_tag": "...",         // English keywords, stock-footage search ke liye
  "is_twist_moment": false     // agar ye scene ek reveal/twist hai to true
}
"""


def _build_user_prompt(topic_title: str, target_minutes: int = 25):
    return f"""
Topic: {topic_title}
Target duration: {target_minutes} minutes (long-form documentary style)
Language: Urdu (Roman script nahi, asal Urdu script mein)
Format: Non-linear storytelling allowed, hook se shuru karo.

Upar diye rules follow karte hue poora script scene-blocks mein JSON format mein do.
"""


def generate_script_claude(topic_title: str, api_key: str, target_minutes: int = 25):
    """Tier 1: Claude API se script generate karta hai."""
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_prompt(topic_title, target_minutes)}],
    )
    text = response.content[0].text
    return json.loads(text)


def generate_script_gemini(topic_title: str, api_key: str, target_minutes: int = 25):
    """Tier 2: Google Gemini se script generate karta hai (fallback)."""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro", system_instruction=SYSTEM_PROMPT)
    response = model.generate_content(_build_user_prompt(topic_title, target_minutes))
    return json.loads(response.text)


def generate_script_local_llama(topic_title: str, target_minutes: int = 25):
    """Tier 3: Local Ollama/Llama model se script generate karta hai (hamesha available, unlimited)."""
    import ollama
    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(topic_title, target_minutes)},
        ],
    )
    return json.loads(response["message"]["content"])


def generate_script(topic_title: str, target_minutes: int = 25):
    """
    Master function: Tier order (config.SCRIPT_WRITER_TIERS) ke mutabiq
    tools try karta hai jab tak koi ek kaam na kar jaye.
    """
    errors = []

    if "claude" in config.SCRIPT_WRITER_TIERS and config.CLAUDE_API_KEY:
        try:
            return {"tier_used": "claude", "blocks": generate_script_claude(
                topic_title, config.CLAUDE_API_KEY, target_minutes)}
        except Exception as e:
            errors.append(f"Claude failed: {e}")

    if "gemini" in config.SCRIPT_WRITER_TIERS and config.GEMINI_API_KEY:
        try:
            return {"tier_used": "gemini", "blocks": generate_script_gemini(
                topic_title, config.GEMINI_API_KEY, target_minutes)}
        except Exception as e:
            errors.append(f"Gemini failed: {e}")

    if "local_llama" in config.SCRIPT_WRITER_TIERS:
        try:
            return {"tier_used": "local_llama", "blocks": generate_script_local_llama(
                topic_title, target_minutes)}
        except Exception as e:
            errors.append(f"Local Llama failed: {e}")

    raise RuntimeError(f"Sab script-writer tiers fail ho gaye:\n" + "\n".join(errors))


if __name__ == "__main__":
    print("Script writer module ready. System prompt rules loaded.")
    print("Tier order:", config.SCRIPT_WRITER_TIERS)
