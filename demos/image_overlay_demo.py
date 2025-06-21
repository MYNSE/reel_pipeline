import sys
import os
from typing import List

# Add parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from image_overlay import ImageOverlay
from video_clip import BGClip
from moviepy import VideoFileClip, CompositeVideoClip

if __name__ == "__main__":
    # === Input files ===
    video_path = "resources/video.mp4"
    overlay_image_paths = ["resources/01.jpg", "resources/02.jpg", "resources/03.png", "resources/03(1).png", "resources/04.jpg"]
    overlay_image_times = [(0, 2), (3, 5), (6, 6.8), (7, 8.8), (9, 12)]
    boom_path = "resources/boom.mp3"
    rat_path = "resources/sad rat.mp3"

    # === Load video and image ===
    # video_clip = VideoFileClip(video_path).with_duration(1)
    video_clip = BGClip(video_path).center_crop((720, 1280), 0.1, -0.1).trim_time(5, 18).return_clip()
    overlays: List[ImageOverlay] = []
    for p, t in zip(overlay_image_paths, overlay_image_times):
        overlay = ImageOverlay(video_clip, p).with_position(0.5, 0.3).with_start_end(*t)
        overlays.append(overlay)
    overlays[0] = overlays[0].with_horizontal_size(0.6).return_clip_with_fade_in(1, 0)
    overlays[1] = overlays[1].with_horizontal_size(0.6).return_clip_with_pop_in(0.2, 0.7)
    overlays[2] = overlays[2].with_prop_scale(1.0, 0.4).with_audio(boom_path, 1.5, start=0.03).return_clip_with_fade_in(0.1, 0.7)
    overlays[3] = overlays[3].with_horizontal_size(1).with_audio(boom_path, 1.5, start=0.03).return_clip_with_pop_in(0.2, 0.7)
    overlays[4] = overlays[4].with_audio(rat_path, 4).return_clip_with_fade_in(1, 0)
    # overlay = ImageOverlay(video_clip, overlay_image_path).with_position(0.5, 0.3).with_horizontal_size(0.8).with_start_end(0.5, 0.8).with_audio(boom_path, 1, start=0.03).return_clip_with_pop_in(pop_in_time=0.05, start_size=0.8)
    final_clip = CompositeVideoClip([video_clip] + overlays)
    # === Export result ===
    if not os.path.exists('../tmp'):
        os.makedirs('../tmp')
    final_clip.write_videofile("../tmp/output_video.mp4", codec="libx264")