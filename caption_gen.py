from get_srt import transcribe_audio
from modify_srt import chunk_srt 
from convert import convert_srt_to_ass
from burn import burn_ass_into_video
import os

def main():
    video_path = 'griffin.mp4'
    EXPECTED_FILES = ["input.srt", "output.srt", "output.ass" ]   #"output.mp4" 
    
    transcribe_audio(video_path, "input")     #video(mp3, mp4), output_prefix
    chunk_srt("input.srt", "output.srt", 3, 80, 100, 0.1)   #words max a line, start scale, end scale, transition time
    convert_srt_to_ass("output.srt", "output.ass")
    burn_ass_into_video(video_path, "output.ass", "output.mp4")  #video, burn ass, output path

    for file in EXPECTED_FILES:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Could not delete {file}: {e}")

if __name__ == "__main__":
    main()