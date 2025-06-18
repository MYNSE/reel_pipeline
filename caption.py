#!/usr/bin/env python3
import os, subprocess, whisper    # pip install openai-whisper moviepy        yt-dlp
from datetime import timedelta  
from moviepy import VideoFileClip

# pip install "numpy<=2.2"    # python3 caption_video.py griffin.mp4     or below format for me
# C:/Users/Richard/AppData/Local/Programs/Python/Python312/python.exe c:/Programming/Dump/reel_pipeline/captions.py griffin.mp4

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


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Add captions to an mp4 using Whisper")
    parser.add_argument("video_path", type=str, help="Path to the mp4 video")
    args = parser.parse_args()

    video = extract_audio(args.video_path)
    generate_subtitles()
    burn_srt_into_video(video_path=INPUT_VID, srt_path=OUTPUT_SRT, output_path=OUTPUT_VID)  #only INPUT VID should be passed in from other functions called captions.py

if __name__ == "__main__":
    main()
