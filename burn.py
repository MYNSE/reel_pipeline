import subprocess

def burn_srt_into_video(video_path, srt_path, output_path):
    command = [
        "ffmpeg",
        "-y",  # Overwrite output
        "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='FontName=Arial,FontSize=24,Outline=1,Shadow=0'",
        "-c:a", "copy",  # keep original audio
        output_path]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def burn_ass_into_video(video_path, ass_path, output_path):
    command = ["ffmpeg", "-i", video_path, "-vf", f"ass={ass_path}", "-c:a", "copy", output_path]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)