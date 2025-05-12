from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from settings import VideoSettings

def create_overlay_video(video_path, image_path, output_path="output_with_overlay.mp4"):
    """
    Create a video with an image overlay.

    Args:
        video_path (str): Path to the input video file
        image_path (str): Path to the overlay image file
        output_path (str): Path where the output video will be saved

    Returns:
        str: Path to the output video file
    """
    video = VideoFileClip(video_path)
    image = (
        ImageClip(image_path)
        .with_duration(video.duration)
        .resized(height=VideoSettings.IMAGE_HEIGHT)
        .with_position(("center", video.h // 2 - VideoSettings.IMAGE_VERTICAL_OFFSET))
    )
    final = CompositeVideoClip([video, image])
    final.write_videofile(output_path, codec=VideoSettings.VIDEO_CODEC, audio_codec=VideoSettings.AUDIO_CODEC)
    return output_path
