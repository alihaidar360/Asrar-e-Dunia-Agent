"""
modules/video_assembler.py
============================
Ye module poore video ka "assembly line" hai:
har scene ki clip + uska matching audio segment + Urdu subtitles + background
music, sab ko FFmpeg se combine karke final video banata hai.

FFmpeg 100% free, open-source, aur professional-grade hai (bade video platforms
khud isko backend mein use karte hain) - isliye ye sabse reliable core engine hai.
"""

import subprocess
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def trim_clip_to_duration(input_path: str, output_path: str, duration_seconds: float):
    """
    Ek clip ko exact duration tak trim/loop karta hai taake wo apne scene ke
    audio segment ke sath perfectly sync ho.
    """
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", input_path,   # agar clip chhoti ho to loop karo
        "-t", str(duration_seconds),
        "-c:v", "libx264", "-an",                  # audio yahan nahi (baad mein voiceover add hoga)
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def concatenate_clips(clip_paths: list, output_path: str):
    """Sab trimmed clips ko ek single video stream mein jodta hai."""
    list_file = os.path.join(config.OUTPUT_DIR, "concat_list.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for path in clip_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def add_voiceover_and_music(video_path: str, voice_path: str, music_path: str, output_path: str,
                             music_volume: float = 0.12):
    """
    Video (bina audio) + narration voice + halki background music -> final mix.
    music_volume kam rakha gaya hai taake voice clearly sunai de.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", voice_path,
        "-i", music_path,
        "-filter_complex",
        f"[2:a]volume={music_volume}[music];[1:a][music]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac",
        "-shortest",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def burn_urdu_subtitles(video_path: str, srt_path: str, output_path: str):
    """
    Urdu subtitles video par 'burn' karta hai (permanently visible) - retention
    barhane ke liye zaroori, kyunki bohat log muted/low-volume dekhte hain.
    """
    # RTL Urdu text ke liye subtitle font clearly Urdu-capable hona chahiye
    style = f"FontName=Urdu Font,FontSize=22,PrimaryColour=&H00FFFFFF,BorderStyle=3,Outline=1"
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='{style}'",
        "-c:a", "copy",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def build_srt_from_scene_blocks(scene_blocks: list, output_srt_path: str):
    """
    Scene-blocks (narration + timing) se ek standard .srt subtitle file banata hai.
    Har block ka 'start_time' aur 'duration' hona chahiye (assembly pipeline pehle
    ye calculate kar chuka hoga audio-duration ke basis par).
    """
    def format_timestamp(seconds: float) -> str:
        ms = int((seconds - int(seconds)) * 1000)
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    with open(output_srt_path, "w", encoding="utf-8") as f:
        for i, block in enumerate(scene_blocks, start=1):
            start = format_timestamp(block["start_time"])
            end = format_timestamp(block["start_time"] + block["duration"])
            f.write(f"{i}\n{start} --> {end}\n{block['narration_ur']}\n\n")

    return output_srt_path


def assemble_full_video(video_project_id: str, scene_blocks: list, clip_paths: list,
                         voice_path: str, music_path: str):
    """
    Master pipeline: sab steps ko sahi order mein chalata hai.
    Returns: final video ka path
    """
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    project_dir = os.path.join(config.OUTPUT_DIR, video_project_id)
    os.makedirs(project_dir, exist_ok=True)

    # Step 1: Har clip ko uske scene-block ki duration tak trim karo
    trimmed_paths = []
    for i, (block, clip_path) in enumerate(zip(scene_blocks, clip_paths)):
        trimmed = os.path.join(project_dir, f"trimmed_{i}.mp4")
        trim_clip_to_duration(clip_path, trimmed, block["duration"])
        trimmed_paths.append(trimmed)

    # Step 2: Sab clips ko jodo (silent video)
    silent_video = os.path.join(project_dir, "silent_video.mp4")
    concatenate_clips(trimmed_paths, silent_video)

    # Step 3: Voiceover + music mix karo
    with_audio = os.path.join(project_dir, "with_audio.mp4")
    add_voiceover_and_music(silent_video, voice_path, music_path, with_audio)

    # Step 4: Urdu subtitles banao aur burn karo
    srt_path = os.path.join(project_dir, "subtitles.srt")
    build_srt_from_scene_blocks(scene_blocks, srt_path)
    final_output = os.path.join(project_dir, "final_video.mp4")
    burn_urdu_subtitles(with_audio, srt_path, final_output)

    return final_output


if __name__ == "__main__":
    print("Video assembler module ready. Output dir:", config.OUTPUT_DIR)
