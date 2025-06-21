from stable_whisper import result_to_srt_vtt
import whisper

model = whisper.load_model("base")
results = model.transcribe("griffin.mp4", word_timestamps=True, fp16=False) # Transcribe the audio with word timestamps
#results = model.transcribe("temp.mp3", word_timestamps=True, fp16=False) # works on mp3
result_to_srt_vtt(results, "temp")