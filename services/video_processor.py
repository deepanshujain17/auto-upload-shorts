from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip

from settings import PathSettings, VideoSettings, news_settings
from utils.media.audio_composer import AudioComposer
from utils.media.video_composer import VideoComposer
from utils.web.browser_utils import render_card_to_image
from utils.web.html_utils import create_html_card


async def _generate_overlay_image(category: str, article: dict) -> str:
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, _generate_overlay_image_sync, category, article)


def _generate_overlay_image_sync(category: str, article: dict) -> str:
    """Generate the news card overlay image.

    Args:
        category (str): News category to process
        article (dict): News article data

    Returns:
        str: Path to the generated overlay image

    Raises:
        Exception: If there's an error in generating the overlay image
    """
    try:
        print(f"\nGenerating overlay video from article of category: {category}")

        # Generate news card HTML
        html_output = PathSettings.get_html_output(category)
        print(f"🖥️ Generating HTML card for {category}...")
        create_html_card(article, html_output)

        # Generate overlay image from HTML
        overlay_image = PathSettings.get_overlay_image(category)
        print(f"🖼️ Rendering HTML to image for {category}...")
        render_card_to_image(html_output, overlay_image)

        print(f"✅ Overlay image created: {overlay_image}")
        return overlay_image

    except Exception as e:
        print(f"❌ Error generating overlay image for {category}: {str(e)}")
        raise


async def create_overlay_video_output(category: str, article: dict) -> str:
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, create_overlay_video_output_sync, category, article)


def create_overlay_video_output_sync(category: str, article: dict) -> str:
    """Create a complete video with news overlay and audio.

    Args:
        category (str): News category to process
        article (dict): News article data

    Returns:
        str: Path to the final video

    Raises:
        FileNotFoundError: If required files are missing
    """
    try:
        # Generate the overlay image
        overlay_image = _generate_overlay_image_sync(category, article)

        # Get output path
        output_video_path = PathSettings.get_final_video(category)

        # Get background assets
        bg_image = PathSettings.get_image_path(
            news_settings.category_bg_image.get(category, news_settings.category_bg_image["default"])
        )
        bg_music = PathSettings.get_music_path(
            news_settings.category_bgm.get(category, news_settings.category_bgm["default"])
        )
        print(f"📸 Using background image: {bg_image}")
        print(f"🎵 Using background music: {bg_music}")

        # Generate article audio
        print("🎙️ Generating audio from article...")
        speech_audio = AudioComposer.generate_article_audio(article)
        duration = speech_audio.duration

        # Validate input files
        for path in [bg_image, bg_music, overlay_image]:
            if not Path(path).is_file():
                raise FileNotFoundError(f"Required file not found: {path}")

        # Ensure output directory exists
        Path(output_video_path).parent.mkdir(parents=True, exist_ok=True)

        # Create video with all components in one step
        with AudioFileClip(bg_music) as music_audio, \
             ImageClip(bg_image) as bg_clip, \
             ImageClip(overlay_image) as overlay_clip:

            # Configure & Create composite audio
            combined_audio = AudioComposer.create_composite_audio(
                speech_audio, music_audio, duration
            )
            print("✅ Audio generated and combined successfully")

            composite_video = VideoComposer.create_composite_video(
                bg_clip, overlay_clip, combined_audio, duration
            )

            composite_video.write_videofile(
                output_video_path,
                fps=VideoSettings.FPS,
                codec=VideoSettings.VIDEO_CODEC,
                audio_codec=VideoSettings.AUDIO_CODEC,
                logger=None
            )

        print(f"✅ Overlay Video created successfully: {output_video_path}")
        return output_video_path

    except Exception as e:
        print(f"❌ Error creating video for {category}: {str(e)}")
        raise
