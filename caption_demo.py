from transcribe_and_burn import transcribe_audio, burn_ass_into_video  #pip install openai-whisper, stable-ts
from caption_effects import chunk_srt, convert_srt_to_ass
import os

def main():   # https://aegi.vmoe.info/docs/3.1/ASS_Tags/
    ''' 
    alignment value 
        +  +  +  +  +
        +  7  8  9  +
        +  4  5  6  +
        +  1  2  3  +
        +  +  +  +  +
    '''

    video_path = 'griffin.mp4'
    EXPECTED_FILES = ["input.srt", "output.srt",  ]   #"output.mp4" "output.ass"
    
    transcribe_audio(video_path, "input")     #video(mp3, mp4), output_prefix                    
    chunk_srt("input.srt", "output.srt", 3, 88, 100, 70)   #words max a line, start scale, end scale, transition time
    convert_srt_to_ass("output.srt", "output.ass", "Dosis", 30, 5) # font, font size, alignment    
    burn_ass_into_video(video_path, "output.ass", "output.mp4")  #video, burn ass, output path

    for file in EXPECTED_FILES:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Could not delete {file}: {e}")

if __name__ == "__main__":
    main()