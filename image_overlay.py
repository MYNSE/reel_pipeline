from moviepy import VideoFileClip, ImageClip, CompositeAudioClip, AudioFileClip, VideoClip
import numpy as np
import cv2

def get_clip_initial_size(static_clip: VideoClip):
    h, w = static_clip.get_frame(0).shape[:2]
    return w, h


class ImageOverlay:
    def __init__(self, bg_video: VideoClip, image_path: str):
        self._vid_w, self._vid_h = get_clip_initial_size(bg_video)
        print(f'{self._vid_w=}, {self._vid_h=}')

        self.prop_x, self.prop_y = 0.5, 0.5 # proportion of width/height that the CENTER of the image should be at
        self.clip = ImageClip(image_path).without_mask()
        self.w, self.h = get_clip_initial_size(self.clip)
        self.start = 0

        if self.w > self._vid_w:
            self = self.with_horizontal_size(1)
        if self.h > self._vid_h:
            self = self.with_vertical_size(1)

    def _with_scale(self, scale_factor_x, scale_factor_y=None):
        if not scale_factor_y:
            scale_factor_y = scale_factor_x
        self.w = int(self.w * scale_factor_x)
        self.h = int(self.h * scale_factor_y)
        self.clip = self.clip.resized((self.w, self.h))
        return self.with_position(self.prop_x, self.prop_y) # redo position since it's relative to screen etc.
    
    def with_prop_scale(self, prop_screen_x, prop_screen_y):
        sx = (self._vid_w * prop_screen_x) / self.w
        sy = (self._vid_h * prop_screen_y) / self.h
        return self._with_scale(sx, sy)

    def with_horizontal_size(self, proportion_of_screen):
        assert 0 <= proportion_of_screen <= 1, 'size must be a proportion 0-1'
        scale_factor =  (self._vid_w * proportion_of_screen) / self.w
        return self._with_scale(scale_factor)
    
    def with_vertical_size(self, proportion_of_screen):
        assert 0 <= proportion_of_screen <= 1, 'size must be a proportion 0-1'
        scale_factor =  self._vid_h * proportion_of_screen / self.h
        return self._with_scale(scale_factor)
    
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
        print(f"{(cx, cy)=}")
        self.clip = self.clip.with_position((cx, cy))
        self.prop_x, self.prop_y = prop_x, prop_y
        return self
    
    def with_start_end(self, start_time, end_time):
        self.clip = self.clip.with_start(start_time).with_end(end_time)
        return self
    
    def with_audio(self, path, duration=None, start=0):
        """
        Start is relative to clip start
        """
        audioclip = AudioFileClip(path)
        if duration:
            audioclip = audioclip.with_duration(duration)
        if start is not None:
            audioclip = audioclip.with_start(start + self.start)
        new_audio_clip = CompositeAudioClip([audioclip])
        self.clip.audio = new_audio_clip
        return self
    
    def _get_absolute_coords_size(self, prop_x, prop_y, size_w, size_h):
        center_w = size_w // 2
        center_h = size_h // 2
        screen_x = int(self._vid_w * prop_x)
        screen_y = int(self._vid_h * prop_y)
        cx, cy = screen_x - center_w, screen_y - center_h
        return cx, cy

    # Return clip with a transition (at this point idk how we gonna keep track of stuff) =======================================

    def return_clip_with_pop_in(self, pop_in_time=0.1, start_size=0.7):
        scale_t = lambda t: start_size + ((1 - start_size) / pop_in_time) * min(t, pop_in_time)
        get_size_t = lambda t: (int(scale_t(t) * self.w), int(scale_t(t) * self.h))
        self.clip = self.clip.transform(lambda get_frame, t: cv2.resize(get_frame(t), get_size_t(t)))
        self.clip = self.clip.with_position(lambda t: self._get_absolute_coords_size(self.prop_x, self.prop_y, *get_size_t(t)))
        return self.clip # no more modifications allowed
    
    def return_clip_with_fade_in(self, fade_in_time=0.1, start_opacity=0.5):
        opacity_t = lambda t: min(start_opacity + ((1 - start_opacity) / fade_in_time) * t, 1.0)
        mask = VideoClip(
            frame_function=lambda t: np.full((self._vid_h, self._vid_w), opacity_t(t), dtype=float),
            duration=self.clip.duration
        )
        self.clip.mask = mask
        return self.clip
    
    def with_start_end(self, start_time, end_time):
        self.start = start_time
        self.clip = self.clip.with_start(start_time).with_end(end_time)
        return self
    
    def return_clip(self):
        return self.clip
