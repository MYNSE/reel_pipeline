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


# def attach_subtitles(video: VideoFileClip) -> None:
#     subtitles = SubtitlesClip(
#         OUTPUT_SRT,
#         lambda txt: TextClip(txt, font=FONT_PATH, fontsize=24, color="white", bg_color="black"),
#     )

#     video_with_subtitles = CompositeVideoClip([
#         video,
#         subtitles.set_position(("center", 0.95), relative=True)
#     ])

#     video_with_subtitles.write_videofile(OUTPUT_VID, codec="libx264")
#     print(f"captioned video saved as {OUTPUT_VID}")

def burn_srt_into_video(video_path, srt_path, output_path):
    """
    Burn subtitles from an SRT file into a video using FFmpeg.
    
    Args:
        video_path (str): Path to the input video.
        srt_path (str): Path to the subtitle file (.srt).
        output_path (str): Path to save the final video.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"SRT file not found: {srt_path}")

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

    if not check_ffmpeg():
        print("ffmpeg is not installed, quitting.")
        return

    if not os.path.exists(args.video_path):
        print("video file not found, quitting.")
        return

    video = extract_audio(args.video_path)
    generate_subtitles()
    # attach_subtitles(video)
    burn_srt_into_video(
    video_path="griffin.mp4",
    srt_path="output.srt",
    output_path="captioned_griffin.mp4"
)


if __name__ == "__main__":
    main()
