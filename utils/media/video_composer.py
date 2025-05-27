from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import CompositeAudioClip
from settings import VideoSettings

class VideoComposer:
    """Handles video composition and rendering."""

    @staticmethod
    def create_composite_video(bg_clip: ImageClip,
                               overlay_clip: ImageClip,
                               combined_audio: CompositeAudioClip,
                               duration: float) -> CompositeVideoClip:
        """Create composite video with background and overlay."""

        # Configure video clips
        bg_clip = bg_clip.with_duration(duration).with_fps(VideoSettings.FPS)
        overlay_clip = (overlay_clip
                        .with_duration(duration)
                        .resized(height=VideoSettings.IMAGE_HEIGHT)
                        .with_position(("center", bg_clip.h // 2 - VideoSettings.IMAGE_VERTICAL_OFFSET)))

        # Combine everything
        final = CompositeVideoClip([bg_clip, overlay_clip]).with_audio(combined_audio).with_duration(duration)

        return final