import os, subprocess, whisper    # pip install openai-whisper moviepy        yt-dlp
from moviepy import VideoFileClip

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

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Add captions to an mp4 using Whisper")
    parser.add_argument("video_path", type=str, help="Path to the mp4 video")
    args = parser.parse_args()
    video = extract_audio(args.video_path)

if __name__ == "__main__":
    main()
