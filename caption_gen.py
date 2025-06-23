from get_srt import transcribe_audio  #pip install openai-whisper, stable-ts
from modify_srt import chunk_srt 
from convert import convert_srt_to_ass
from burn import burn_ass_into_video
import os

def main():   # https://aegi.vmoe.info/docs/3.1/ASS_Tags/
    video_path = 'griffin.mp4'
    EXPECTED_FILES = ["input.srt", "output.srt",  ]   #"output.mp4" "output.ass"
    
    transcribe_audio(video_path, "input")     #video(mp3, mp4), output_prefix                    
    chunk_srt("input.srt", "output.srt", 3, 88, 100, 70)   #words max a line, start scale, end scale, transition time
    convert_srt_to_ass("output.srt", "output.ass", "Dosis", 30, 5) # font, font size, alignment    
    ''' 
    alignment value 
        +  +  +  +  +
        +  7  8  9  +
        +  4  5  6  +
        +  1  2  3  +
        +  +  +  +  +
    '''
    burn_ass_into_video(video_path, "output.ass", "output.mp4")  #video, burn ass, output path

    for file in EXPECTED_FILES:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Could not delete {file}: {e}")

if __name__ == "__main__":
    main()