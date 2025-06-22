from stable_whisper import result_to_srt_vtt
import whisper

def transcribe_audio(input_file="griffin.mp4", output_prefix="input"):
    model = whisper.load_model("base")
    results = model.transcribe(input_file, word_timestamps=True, fp16=False) # Transcribe the audio with word timestamps
    result_to_srt_vtt(results, output_prefix)