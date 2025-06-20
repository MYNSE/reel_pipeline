import sys
import os

# Add parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from image_overlay import ImageOverlay
from moviepy import VideoFileClip, CompositeVideoClip

if __name__ == "__main__":
    # === Input files ===
    video_path = "resources/video.mp4"
    overlay_image_path = "resources/screen.png"

    # === Load video and image ===
    video_clip = VideoFileClip(video_path).with_duration(1)
    overlay = ImageOverlay(video_clip, overlay_image_path).with_position(0.5, 0.3).with_horizontal_size(0.8).with_start_end(0.5, 0.8).return_clip_with_pop_in(pop_in_time=0.05, start_size=0.8)
    final_clip = CompositeVideoClip([video_clip, overlay])
    # === Export result ===
    if not os.path.exists('../tmp'):
        os.makedirs('../tmp')
    final_clip.write_videofile("../tmp/output_video.mp4", codec="libx264")