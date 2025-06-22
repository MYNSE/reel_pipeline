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


# def generate_subtitles() -> None:
#     model = whisper.load_model("base")
#     result = model.transcribe(audio=TEMP_FILE, fp16=False)
#     segments = result["segments"]
    
#     with open(OUTPUT_SRT, "w", encoding="utf-8") as f: # Overwrite any existing SRT file
#         for seg in segments:
#             start = "0" + str(timedelta(seconds=int(seg["start"]))) + ",000"
#             end = "0" + str(timedelta(seconds=int(seg["end"]))) + ",000"
#             text = seg["text"].lstrip()
#             f.write(f"{seg['id'] + 1}\n{start} --> {end}\n{text}\n\n")
#     print("subtitles generated")

def format_srt_timestamp(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    millis = int((td.total_seconds() - total_seconds) * 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_subtitles() -> None:
    model = whisper.load_model("base")
    result = model.transcribe(audio=TEMP_FILE, fp16=False)
    segments = result["segments"]

    with open(OUTPUT_SRT, "w", encoding="utf-8") as f:
        index = 1
        for seg in segments:
            words = seg["text"].strip().split()
            num_words = len(words)

            if num_words == 0:
                continue

            # Chunk into 2–3 words per subtitle line
            chunks = []
            i = 0
            while i < num_words:
                chunk_size = min(3, max(2, num_words - i)) if num_words - i > 3 else num_words - i
                chunks.append(words[i:i + chunk_size])
                i += chunk_size

            chunk_duration = (seg["end"] - seg["start"]) / len(chunks)
            for i, chunk in enumerate(chunks):
                chunk_start = seg["start"] + i * chunk_duration
                chunk_end = chunk_start + chunk_duration

                start_ts = format_srt_timestamp(chunk_start)
                end_ts = format_srt_timestamp(chunk_end)
                text = " ".join(chunk)

                f.write(f"{index}\n{start_ts} --> {end_ts}\n{text}\n\n")
                index += 1

    print("chunked subtitles generated")

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
            words = seg["text"].strip().split()
            num_words = len(words)
            if num_words == 0:
                continue

            # Create chunks of 2–3 words
            chunks = []
            i = 0
            while i < num_words:
                remaining = num_words - i
                chunk_size = 3 if remaining >= 3 else remaining
                if remaining == 4:  # to avoid a lone word at the end
                    chunk_size = 2
                chunks.append(words[i:i + chunk_size])
                i += chunk_size

            total_duration = seg["end"] - seg["start"]
            chunk_duration = total_duration / len(chunks)

            for j, chunk in enumerate(chunks):
                chunk_start = seg["start"] + j * chunk_duration
                chunk_end = chunk_start + chunk_duration

                start = to_ass_timestamp(chunk_start)
                end = to_ass_timestamp(chunk_end)

                word_duration_cs = int((chunk_duration / len(chunk)) * 100)  # centiseconds

                karaoke_line = ''.join([f"{{\\k{word_duration_cs}}}{word} " for word in chunk])
                pop_in_prefix = r"{\fscx70\fscy70\t(0,500,\fscx100\fscy100)}"
                full_line = f"{pop_in_prefix}{karaoke_line.strip()}"

                f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{full_line}\n")

    print("ASS subtitles generated with 2–3 word chunks, karaoke highlighting, and pop-in.")

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
    command = ["ffmpeg", "-i", video_path, "-vf", f"ass={ass_path}", "-c:a", "copy", output_path]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():
    # import argparse
    # parser = argparse.ArgumentParser(description="Add captions to an mp4 using Whisper")
    # parser.add_argument("video_path", type=str, help="Path to the mp4 video")
    # args = parser.parse_args()

    # video = extract_audio(args.video_path)
    #generate_subtitles()
    #generate_ass()
    #burn_srt_into_video(video_path=INPUT_VID, srt_path=OUTPUT_SRT, output_path=OUTPUT_VID)  #only INPUT VID should be passed in from other functions called captions.py
    burn_ass_into_video(video_path=INPUT_VID, ass_path="output.ass", output_path=OUTPUT_VID)


if __name__ == "__main__":
    main()
