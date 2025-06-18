#!/usr/bin/env python3

import os,subprocess     # pip install openai-whisper yt-dlp moviepy
from datetime import timedelta
from moviepy import VideoFileClip, CompositeVideoClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip

import whisper  # pip install "numpy<=2.2"    # python3 caption_video.py griffin.mp4     
# C:/Users/Richard/AppData/Local/Programs/Python/Python312/python.exe c:/Programming/Dump/reel_pipeline/captions.py griffin.mp4

TEMP_FILE = "temp.mp3"          
OUTPUT_SRT = "output.srt"
OUTPUT_VID = "output.mp4"
FONT_PATH = "C:/Windows/Fonts/arial.ttf"

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

    # Overwrite any existing SRT file
    with open(OUTPUT_SRT, "w", encoding="utf-8") as f:
        for seg in segments:
            start = "0" + str(timedelta(seconds=int(seg["start"]))) + ",000"
            end = "0" + str(timedelta(seconds=int(seg["end"]))) + ",000"
            text = seg["text"].lstrip()
            f.write(f"{seg['id'] + 1}\n{start} --> {end}\n{text}\n\n")

    print("subtitles generated")


def attach_subtitles(video: VideoFileClip) -> None:
    subtitles = SubtitlesClip(
        OUTPUT_SRT,
        lambda txt: TextClip(txt, font=FONT_PATH, fontsize=24, color="white", bg_color="black"),
    )

    video_with_subtitles = CompositeVideoClip([
        video,
        subtitles.set_position(("center", 0.95), relative=True)
    ])

    video_with_subtitles.write_videofile(OUTPUT_VID, codec="libx264")
    print(f"captioned video saved as {OUTPUT_VID}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Add captions to an mp4 using Whisper")
    parser.add_argument("video_path", type=str, help="Path to the mp4 video")
    args = parser.parse_args()

    if not check_ffmpeg():
        print("ffmpeg is not installed, quitting.")
        return

    if not os.path.exists(args.video_path):
        print("video file not found, quitting.")
        return

    video = extract_audio(args.video_path)
    generate_subtitles()
    attach_subtitles(video)


if __name__ == "__main__":
    main()
