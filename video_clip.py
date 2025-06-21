from moviepy import VideoFileClip, VideoClip


def get_clip_initial_size(clip: VideoClip):
    h, w = clip.get_frame(0).shape[:2]
    return w, h


class BGClip:
    def __init__(self, path):
        self.clip = VideoFileClip(path)
        self.w, self.h = get_clip_initial_size(self.clip)

    def trim_time(self, start_time, end_time):
        self.clip = self.clip.subclipped(start_time, end_time)
        return self

    def center_crop(self, screen_size, offset_x=0, offset_y=0):
        assert -1 <= offset_x <= 1 and -1 <= offset_y <= 1, "offsets must be proportions (-1,1)"
        center_x, center_y = self.w // 2, self.h // 2
        sx, sy = (x // 2 for x in screen_size)
        center_x += int(offset_x * self.w)
        center_y += int(offset_y * self.h)
        self.clip = self.clip.cropped(center_x - sx, center_y - sy, center_x + sx, center_y + sy)
        return self
    
    def return_clip(self):
        return self.clip
