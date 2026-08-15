"""
main.py
========
Ye poore "Asrar-e-Dunia" agent ka ENTRY POINT hai.

Ye file chalane se agent:
1. Scheduler se check karta hai aaj kya karna hai (Long video? Shorts?)
2. Agar zaroorat ho -> Research -> Script -> Voice -> Visuals -> Assembly -> Upload
3. Agar long video ban chuki ho -> usi se Shorts nikal kar upload karta hai

Chalane ka tareeqa:
    python3 main.py

Roz automatically chalane ke liye (cron job):
    0 9 * * * cd /path/to/asrar_e_dunia_agent && python3 main.py >> logs.txt 2>&1
"""

import os
import sys
import uuid
import datetime
import traceback

import config
import database
from modules import research, script_writer, voiceover, visuals, video_assembler
from modules import shorts_generator, thumbnail, uploader, scheduler


def log(message: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_long_video_pipeline():
    """
    A-to-Z pipeline: research se le kar YouTube upload tak, ek complete
    long-form (20-30 min) history video banata hai.
    """
    project_id = f"video_{uuid.uuid4().hex[:10]}"
    log(f"=== Long Video Pipeline Shuru: {project_id} ===")

    # STEP 1: RESEARCH - naya, uncovered topic dhoondo
    log("Step 1/7: Topic research ho raha hai...")
    youtube_api_key = os.getenv("YOUTUBE_DATA_API_KEY", "")
    batch = research.get_next_research_batch(youtube_api_key)
    if not batch["candidates"]:
        log("Koi naya topic nahi mila is batch mein. Skip kar rahe hain.")
        return None
    topic_title = batch["candidates"][0]["title"]
    log(f"Topic chuna gaya: {topic_title}")

    # STEP 2: SCRIPT - scene-blocks ke sath Urdu script generate karo
    log("Step 2/7: Script likha ja raha hai...")
    script_result = script_writer.generate_script(topic_title)
    scene_blocks = script_result["blocks"]
    log(f"Script mila ({script_result['tier_used']} tier se) - {len(scene_blocks)} scenes")

    # STEP 3: VOICEOVER - poori narration ko awaz mein convert karo
    log("Step 3/7: Voiceover generate ho raha hai...")
    full_narration = " ".join(b["narration_ur"] for b in scene_blocks)
    voice_path = os.path.join(config.OUTPUT_DIR, f"{project_id}_voice.mp3")
    voice_result = voiceover.generate_voiceover(full_narration, voice_path)
    log(f"Voiceover taiyar ({voice_result['tier_used']} tier se)")

    # Har scene-block ki timing calculate karo (audio duration ke hisab se proportion)
    total_duration = voiceover.get_audio_duration_seconds(voice_result["path"])
    total_chars = sum(len(b["narration_ur"]) for b in scene_blocks)
    running_time = 0.0
    for block in scene_blocks:
        block["duration"] = (len(block["narration_ur"]) / total_chars) * total_duration
        block["start_time"] = running_time
        running_time += block["duration"]

    # STEP 4: VISUALS - har scene ke liye ek UNIQUE clip dhoondo
    log("Step 4/7: Visuals/clips dhoonde ja rahe hain (no-repeat rule ke sath)...")
    clip_paths = []
    for i, block in enumerate(scene_blocks):
        clip_info = visuals.find_unique_clip_for_scene(project_id, block["visual_tag"])
        clip_paths.append(clip_info.get("url") or clip_info.get("path"))
        log(f"  Scene {i+1}/{len(scene_blocks)}: '{block['visual_tag']}' -> {clip_info['tier_used']}")

    # STEP 5: ASSEMBLY - sab kuch combine karke final video banao
    log("Step 5/7: Video assemble ho raha hai (FFmpeg)...")
    music_path = os.path.join(config.MUSIC_DIR, "default_background.mp3")
    final_video_path = video_assembler.assemble_full_video(
        project_id, scene_blocks, clip_paths, voice_result["path"], music_path
    )
    log(f"Final video ready: {final_video_path}")

    # STEP 6: THUMBNAIL
    log("Step 6/7: Thumbnail bana raha hai...")
    hook_text = scene_blocks[0]["narration_ur"][:35]
    thumb_result = thumbnail.generate_thumbnail(project_id, hook_text)
    log(f"Thumbnail ready ({thumb_result['tier_used']} tier se)")

    # STEP 7: UPLOAD
    log("Step 7/7: YouTube par upload ho raha hai...")
    upload_result = uploader.upload_video(final_video_path, thumb_result["path"], topic_title)
    log(f"Upload complete: {upload_result['url']}")

    return {
        "project_id": project_id,
        "final_video_path": final_video_path,
        "scene_blocks": scene_blocks,
        "topic_title": topic_title,
        "upload_result": upload_result,
    }


def run_shorts_pipeline(long_video_result: dict = None):
    """
    Agar recent long video available ho to usi se 3 Shorts nikal kar upload
    karta hai. Agar available na ho, is cycle ko skip karta hai (Shorts hamesha
    kisi na kisi long video ka byproduct hain).
    """
    log("=== Shorts Pipeline Shuru ===")

    if long_video_result is None:
        log("Koi fresh long video available nahi - Shorts is cycle mein skip.")
        return None

    shorts_dir = os.path.join(config.OUTPUT_DIR, "shorts")
    shorts_paths = shorts_generator.generate_shorts_from_long_video(
        long_video_result["project_id"],
        long_video_result["final_video_path"],
        long_video_result["scene_blocks"],
        shorts_dir,
    )

    for i, short_path in enumerate(shorts_paths, start=1):
        thumb = thumbnail.generate_thumbnail(
            f"{long_video_result['project_id']}_short_{i}",
            long_video_result["scene_blocks"][0]["narration_ur"][:30],
        )
        result = uploader.upload_video(
            short_path, thumb["path"], long_video_result["topic_title"], is_short=True
        )
        log(f"Short {i}/3 uploaded: {result['url']}")

    return shorts_paths


def main():
    database.init_db()
    log(f"Asrar-e-Dunia Agent chalu ho raha hai...")

    tasks = scheduler.get_today_tasks()
    log(f"Aaj ke tasks: {tasks}")

    long_video_result = None

    if tasks["make_long_video"]:
        try:
            long_video_result = run_long_video_pipeline()
        except Exception as e:
            log(f"ERROR long video pipeline mein: {e}")
            traceback.print_exc()

    if tasks["make_shorts"]:
        try:
            run_shorts_pipeline(long_video_result)
        except Exception as e:
            log(f"ERROR shorts pipeline mein: {e}")
            traceback.print_exc()

    if not tasks["make_long_video"] and not tasks["make_shorts"]:
        log("Aaj kuch bhi due nahi hai - schedule ke mutabiq abhi wait karo.")

    log("Agent ka run complete hua.")


if __name__ == "__main__":
    main()
