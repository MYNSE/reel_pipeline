#!/usr/bin/env python3
import os, subprocess, whisper    # pip install openai-whisper moviepy        yt-dlp
from datetime import timedelta  
from moviepy import VideoFileClip
import random

# pip install "numpy<=2.2"    # python3 caption_video.py griffin.mp4     or below format for me
# C:/Users/Richard/AppData/Local/Programs/Python/Python312/python.exe C:/Programming/Dump/reel_pipeline/caption.py griffin.mp4

INPUT_VID = "griffin.mp4" 
TEMP_FILE = "temp.mp3"          
OUTPUT_SRT = "output.srt"
OUTPUT_VID = "output.mp4"
# FONT_PATH = "C:/Windows/Fonts/arial.ttf"

def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0 and 'ffmpeg' in result.stdout
    except FileNotFoundError:
        return False

def extract_audio(video_path: str) -> VideoFileClip:
    video = VideoFileClip(video_path)
    if video.audio is not None:
        video.audio.write_audiofile(TEMP_FILE, codec="mp3")
        return video
    else:
        print("video has no audio")
        exit()


def generate_subtitles() -> None:
    model = whisper.load_model("base")
    result = model.transcribe(audio=TEMP_FILE, fp16=False)
    segments = result["segments"]
    
    with open(OUTPUT_SRT, "w", encoding="utf-8") as f: # Overwrite any existing SRT file
        for seg in segments:
            start = "0" + str(timedelta(seconds=int(seg["start"]))) + ",000"
            end = "0" + str(timedelta(seconds=int(seg["end"]))) + ",000"
            text = seg["text"].lstrip()
            f.write(f"{seg['id'] + 1}\n{start} --> {end}\n{text}\n\n")
    print("subtitles generated")

OUTPUT_ASS = "output.ass"

def to_ass_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds - int(seconds)) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

def generate_ass() -> None:
    model = whisper.load_model("base")
    result = model.transcribe(audio=TEMP_FILE, fp16=False)
    segments = result["segments"]

    header = """[Script Info]
Title: Word-by-Word ASS
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,36,&H0000FF00,&H00666666,&H00000000,&H00000000,-1,0,1,1,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    with open(OUTPUT_ASS, "w", encoding="utf-8") as f:
        f.write(header)

        for seg in segments:
            start_time = seg["start"]
            end_time = seg["end"]
            duration = end_time - start_time

            start = to_ass_timestamp(start_time)
            end = to_ass_timestamp(end_time)

            # Words and timing
            words = seg["text"].strip().split()
            num_words = len(words)
            word_duration_cs = int((duration / max(1, num_words)) * 100)  # centiseconds

            # Build word-by-word highlight using \k
            karaoke_line = ''.join([f"{{\\k{word_duration_cs}}}{w} " for w in words])

            # One-time pop-in for the entire line (from 70% to 100% over 500ms)
            pop_in_prefix = r"{\fscx70\fscy70\t(0,500,\fscx100\fscy100)}"
            full_line = f"{pop_in_prefix}{karaoke_line.strip()}"

            f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{full_line}\n")

    print("ASS subtitles generated with karaoke highlighting and pop-in.")

def burn_srt_into_video(video_path, srt_path, output_path):
    if not os.path.exists(video_path) or not os.path.exists(srt_path):
        raise FileNotFoundError(f"Video or SRT file not found")

    command = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='FontName=Arial,FontSize=24,Outline=1,Shadow=0'",
        "-c:a", "copy",  # keep original audio
        output_path
    ]

    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if process.returncode != 0:
        print("Error:", process.stderr.decode())
        raise RuntimeError("FFmpeg failed to burn subtitles.")
    print("Subtitle overlay complete. Output saved to:", output_path)

def burn_ass_into_video(video_path, ass_path, output_path):
    if not os.path.exists(video_path) or not os.path.exists(ass_path):
        raise FileNotFoundError("Video or ASS file not found")

    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"ass={ass_path}",
        "-c:a", "copy",
        output_path
    ]

    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if process.returncode != 0:
        print("Error:", process.stderr.decode())
        raise RuntimeError("FFmpeg failed to burn ASS subtitles.")
    print("ASS subtitle overlay complete. Output saved to:", output_path)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Add captions to an mp4 using Whisper")
    parser.add_argument("video_path", type=str, help="Path to the mp4 video")
    args = parser.parse_args()

    video = extract_audio(args.video_path)
    #generate_subtitles()
    generate_ass()
    #burn_srt_into_video(video_path=INPUT_VID, srt_path=OUTPUT_SRT, output_path=OUTPUT_VID)  #only INPUT VID should be passed in from other functions called captions.py
    burn_ass_into_video(video_path=INPUT_VID, ass_path="output.ass", output_path=OUTPUT_VID)


if __name__ == "__main__":
    main()
