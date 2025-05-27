from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from pathlib import Path

from settings import VideoSettings, NewsSettings, PathSettings
from utils.media_utils.audio_composer import AudioComposer
from utils.media_utils.video_composer import VideoComposer


def create_overlay_video_output(category: str, article: dict, overlay_image: str) -> str:
    """Create a complete video with news overlay and audio.

    Args:
        category (str): News category to process
        article (dict): News article data
        overlay_image (str): Path to the overlay image

    Returns:
        str: Path to the final video

    Raises:
        ValueError: If category is invalid or required assets are missing
        FileNotFoundError: If required files are missing
    """
    try:
        print(f"Generating overlay video from article of category: {category}")
        # Get output path
        final_video = PathSettings.get_final_video(category)

        # Get background assets
        bg_image = PathSettings.get_image_path(
            NewsSettings.CATEGORY_BG_IMAGE.get(category, NewsSettings.CATEGORY_BG_IMAGE["default"])
        )
        bg_music = PathSettings.get_music_path(
            NewsSettings.CATEGORY_BGM.get(category, NewsSettings.CATEGORY_BGM["default"])
        )
        print(f"📸 Using background: {bg_image}")
        print(f"🎵 Using music: {bg_music}")

        # Generate article audio
        print("🎙️ Generating audio from article...")
        speech_audio = AudioComposer.generate_article_audio(article)
        duration = speech_audio.duration

        # Validate input files
        for path in [bg_image, bg_music, overlay_image]:
            if not Path(path).is_file():
                raise FileNotFoundError(f"Required file not found: {path}")

        # Ensure output directory exists
        Path(final_video).parent.mkdir(parents=True, exist_ok=True)

        # Create video with all components in one step
        with AudioFileClip(bg_music) as music_audio, \
             ImageClip(bg_image) as bg_clip, \
             ImageClip(overlay_image) as overlay_clip:

            # Configure & Create composite audio
            combined_audio = AudioComposer.create_composite_audio(
                speech_audio, music_audio, duration
            )
            print("🎶 ✅ Audio generated and combined successfully")

            final = VideoComposer.create_composite_video(
                bg_clip, overlay_clip, combined_audio, duration
            )

            final.write_videofile(
                final_video,
                fps=VideoSettings.FPS,
                codec=VideoSettings.VIDEO_CODEC,
                audio_codec=VideoSettings.AUDIO_CODEC,
                logger=None
            )

        print(f"✅ Overlay Video created successfully: {final_video}")
        return final_video

    except Exception as e:
        print(f"❌ Error creating video for {category}: {str(e)}")
        raise

