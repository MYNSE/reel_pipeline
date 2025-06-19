from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, VideoClip
import numpy as np
import cv2

# === Input files ===
video_path = "tmp/video.mp4"
overlay_image_path = "tmp/screen.png"

# === Load video and image ===
video_clip = VideoFileClip(video_path).with_duration(1)
overlay_image = ImageClip(overlay_image_path, duration=video_clip.duration)
img_h, img_w = overlay_image.get_frame(0).shape[:2]
print(f"{(img_h, img_w)=}")
vid_h, vid_w = video_clip.get_frame(0).shape[:2]
new_height = int(img_h * (vid_w / img_w))
print(vid_w, new_height)

# === Zoom and fade effect ===
fade_duration = 0.5

overlay_image = overlay_image.resized((vid_w, new_height)).with_position('center', 'center').without_mask()
scale_t = lambda t: 0.7 + 3 * min(t, 0.1)
overlay_image = overlay_image.transform(lambda get_frame, t: cv2.resize(get_frame(t), (int(scale_t(t) * vid_w), int(scale_t(t) * new_height))))

opacity_t = lambda t: min(max(0.5, t/fade_duration), 1.0)
mask = VideoClip(
    frame_function=lambda t: np.full((vid_h, vid_w), opacity_t(t), dtype=float),
    duration=2
)

overlay_image.mask = mask

# overlay_image = overlay_image.resized((vid_w, new_height)).with_position('center', 'center')

# NO NEED to do this, you can just use .resized()
# overlay_image = overlay_image.image_transform(lambda frame: cv2.resize(frame, (vid_w, new_height))).with_position('center', 'center')
# overlay_image.mask = overlay_image.mask.resized((vid_w, new_height))
print(f"{overlay_image.size=}")
print(f"{overlay_image.get_frame(0).shape=}")
# cv2.imwrite('output_img.png', overlay_image.get_frame(0))

# === Combine video and overlay ===
final_clip = CompositeVideoClip([video_clip, overlay_image])

# === Export result ===
final_clip.write_videofile("tmp/output_video.mp4", codec="libx264")