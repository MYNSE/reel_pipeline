from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, VideoClip
import numpy as np
import cv2

def get_clip_initial_size(static_clip: VideoClip):
    h, w = static_clip.get_frame(0).shape[:2]
    return w, h


class ImageOverlay:
    def __init__(self, bg_video: VideoClip, image_path: str):
        self._vid_w, self._vid_h = get_clip_initial_size(bg_video)
        print(f'{self._vid_w=}, {self._vid_h=}')

        self.prop_x, self.prop_y = None, None # proportion of width/height that the CENTER of the image should be at
        self.clip = ImageClip(image_path).without_mask()
        self.w, self.h = get_clip_initial_size(self.clip)

    def with_scale(self, scale_factor):
        self.w = int(self.w * scale_factor)
        self.h = int(self.h * scale_factor)
        self.clip = self.clip.resized((self.w, self.h))
        return self.with_position(self.prop_x, self.prop_y) # redo position since it's relative to screen etc.

    def with_horizontal_size(self, proportion_of_screen):
        assert 0 <= proportion_of_screen <= 1, 'size must be a proportion 0-1'
        scale_factor =  (self._vid_w * proportion_of_screen) / self.w
        return self.with_scale(scale_factor)
    
    def with_vertical_size(self, proportion_of_screen):
        assert 0 <= proportion_of_screen <= 1, 'size must be a proportion 0-1'
        scale_factor =  self._vid_h * proportion_of_screen / self.h
        return self.with_scale(scale_factor)
    
    def _get_absolute_coords(self, prop_x, prop_y):
        assert 0 <= prop_x <= 1 and 0 <= prop_y <= 1, 'xy proportions must be 0-1'
        center_w = self.w // 2
        center_h = self.h // 2
        screen_x = int(self._vid_w * prop_x)
        screen_y = int(self._vid_h * prop_y)
        cx, cy = screen_x - center_w, screen_y - center_h
        return cx, cy

    def with_position(self, prop_x, prop_y):
        """
        Get coords such that this imageclip will be at the center of the video.
        """
        cx, cy = self._get_absolute_coords(prop_x, prop_y)
        self.clip = self.clip.with_position((cx, cy))
        self.prop_x, self.prop_y = prop_x, prop_y
        return self
    
    def with_start_end(self, start_time, end_time):
        self.clip = self.clip.with_start(start_time).with_end(end_time)
        return self


if __name__ == "__main__":
    # === Input files ===
    video_path = "tmp/video.mp4"
    overlay_image_path = "tmp/screen.png"

    # === Load video and image ===
    video_clip = VideoFileClip(video_path).with_duration(1)
    overlay = ImageOverlay(video_clip, overlay_image_path).with_position(0.5, 0.5).with_horizontal_size(1).with_start_end(0, 1)
    final_clip = CompositeVideoClip([video_clip, overlay.clip])
    # === Export result ===
    final_clip.write_videofile("tmp/output_video.mp4", codec="libx264")