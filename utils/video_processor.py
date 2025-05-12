from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

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
        .resized(height=720)  # Resize image to desired height
        .with_position(("center", video.h // 2 - 350))
    )
    final = CompositeVideoClip([video, image])
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path
