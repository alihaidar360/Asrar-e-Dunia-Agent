"""
modules/shorts_generator.py
=============================
Long video (20-30 min) ban jane ke baad, isi se 3 Shorts auto-generate karta hai.
Shorts alag se research/script nahi maangte - ye long video ka "byproduct" hain.

Selection logic: script_writer.py jin blocks ko "is_twist_moment: true" mark
karta hai, unhi ke around se best 3 moments Shorts ke liye choose kiye jate hain.
"""

import subprocess
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def pick_top_moments(scene_blocks: list, count: int = 3):
    """
    Twist-moments ko priority deta hai. Agar kaafi twist-moments na hon,
    to video ke evenly-spaced hisso se fill karta hai (start/middle/end).
    """
    twist_blocks = [b for b in scene_blocks if b.get("is_twist_moment")]

    if len(twist_blocks) >= count:
        return twist_blocks[:count]

    # Fallback: video ko teen hisso mein baant kar ek-ek moment lo
    total = len(scene_blocks)
    picks = []
    for i in range(count):
        idx = min(total - 1, int(total * (i + 0.5) / count))
        picks.append(scene_blocks[idx])
    return picks


def extract_short_clip(source_video_path: str, start_time: float, duration: float, output_path: str):
    """
    Long video se ek segment nikal kar 9:16 (vertical) Shorts format mein
    crop/convert karta hai - Shorts ke liye vertical hona zaroori hai.
    """
    max_duration = min(duration, config.SHORT_VIDEO_MAX_SECONDS)

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time), "-i", source_video_path,
        "-t", str(max_duration),
        # Center-crop karke 9:16 vertical banata hai (1080x1920 standard Shorts size)
        "-vf", "crop=ih*9/16:ih,scale=1080:1920",
        "-c:v", "libx264", "-c:a", "aac",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def add_shorts_hook_text(video_path: str, hook_text_ur: str, output_path: str):
    """
    Shorts ke upar ek bold Urdu hook-text overlay karta hai (jaise 'Kya sach mein
    aisa hua tha?') - ye scroll karte waqt attention grab karta hai.
    """
    font_path = config.URDU_FONT_PATH
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf",
        f"drawtext=fontfile={font_path}:text='{hook_text_ur}':"
        f"fontcolor=white:fontsize=60:box=1:boxcolor=black@0.5:boxborderw=15:"
        f"x=(w-text_w)/2:y=100",
        "-c:a", "copy",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def generate_shorts_from_long_video(video_project_id: str, final_video_path: str,
                                     scene_blocks: list, output_dir: str):
    """
    Master function: long video se 3 Shorts banata hai aur unke paths return karta hai.
    """
    os.makedirs(output_dir, exist_ok=True)
    top_moments = pick_top_moments(scene_blocks, count=3)

    shorts_paths = []
    for i, block in enumerate(top_moments, start=1):
        raw_short = os.path.join(output_dir, f"{video_project_id}_short_{i}_raw.mp4")
        final_short = os.path.join(output_dir, f"{video_project_id}_short_{i}.mp4")

        extract_short_clip(
            final_video_path,
            start_time=block["start_time"],
            duration=block["duration"] + 15,  # thora context ke sath
            output_path=raw_short,
        )

        hook_text = block["narration_ur"][:40]  # scene ke pehle alfaz hook ke tor par
        add_shorts_hook_text(raw_short, hook_text, final_short)
        shorts_paths.append(final_short)

    return shorts_paths


if __name__ == "__main__":
    print("Shorts generator ready. Max short duration:", config.SHORT_VIDEO_MAX_SECONDS, "seconds")
