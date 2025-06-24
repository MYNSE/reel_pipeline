from stable_whisper import result_to_srt_vtt
import whisper
import subprocess

def transcribe_audio(input_file="griffin.mp4", output_prefix="input"):
    model = whisper.load_model("base")
    results = model.transcribe(input_file, word_timestamps=True, fp16=False) # Transcribe the audio with word timestamps
    result_to_srt_vtt(results, output_prefix)

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