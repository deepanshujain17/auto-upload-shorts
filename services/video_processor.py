from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import multiprocessing

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip

from settings import PathSettings, VideoSettings, news_settings
from utils.media.audio_composer import AudioComposer
from utils.media.video_composer import VideoComposer
from utils.web.browser_utils import render_card_to_image
from utils.web.html_utils import create_html_card
from utils.file_lock import FileLock

# Shared thread pool executor with proper initialization
_shared_executor: Optional[ThreadPoolExecutor] = None
_executor_lock = asyncio.Lock()

# Global semaphore to limit concurrent video processing
# This helps prevent memory issues with multiple moviepy instances
_video_semaphore: Optional[asyncio.Semaphore] = None

def get_video_semaphore() -> asyncio.Semaphore:
    """Get the global video processing semaphore."""
    global _video_semaphore
    if _video_semaphore is None:
        # Allow slightly more concurrent video processing tasks than CPUs
        # but not too many to prevent memory issues
        cpu_count = multiprocessing.cpu_count()
        max_concurrent = max(1, min(cpu_count + 2, 8))  # Between 1 and 8
        _video_semaphore = asyncio.Semaphore(max_concurrent)
    return _video_semaphore

def get_executor() -> ThreadPoolExecutor:
    """Get or create the shared thread pool executor."""
    global _shared_executor
    if _shared_executor is None:
        # Increase number of workers for better parallelism
        # Using CPU count or slightly higher for IO-bound portions
        cpu_count = multiprocessing.cpu_count()
        _shared_executor = ThreadPoolExecutor(max_workers=max(cpu_count * 2, 8))
    return _shared_executor

async def cleanup_executor():
    """Cleanup the shared executor."""
    global _shared_executor
    async with _executor_lock:
        if _shared_executor is not None:
            _shared_executor.shutdown(wait=True)
            _shared_executor = None

async def _generate_overlay_image(category: str, article: dict) -> str:
    """Generate the overlay image asynchronously using the shared executor."""
    try:
        # Get file paths
        html_output = PathSettings.get_html_output(category)
        overlay_image = PathSettings.get_overlay_image(category)

        # Acquire locks for both files
        await FileLock.acquire(html_output)
        await FileLock.acquire(overlay_image)

        try:
            loop = asyncio.get_running_loop()
            executor = get_executor()
            return await loop.run_in_executor(executor, _generate_overlay_image_sync, category, article)
        finally:
            # Release locks in reverse order
            await FileLock.release(overlay_image)
            await FileLock.release(html_output)
    except Exception as e:
        print(f"Error in _generate_overlay_image: {str(e)}")
        raise

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
    """Create an overlay video asynchronously using the shared executor."""
    try:
        # Get file paths that need locking
        output_video_path = PathSettings.get_final_video(category)
        await FileLock.acquire(output_video_path)

        try:
            loop = asyncio.get_running_loop()
            async with _executor_lock:
                executor = get_executor()
                return await loop.run_in_executor(executor, create_overlay_video_output_sync, category, article)
        finally:
            await FileLock.release(output_video_path)
    except Exception as e:
        print(f"Error in create_overlay_video_output: {str(e)}")
        raise


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

        # The async parts must be executed in the main thread using an event loop
        # Temporarily create a new event loop in this thread to run our async functions
        loop = asyncio.new_event_loop()
        try:
            # Generate article audio using our new async function
            print("🎙️ Generating audio from article...")
            speech_audio = loop.run_until_complete(
                AudioComposer.generate_article_audio(article)
            )
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

                # Configure & Create composite audio using our new async function
                combined_audio = loop.run_until_complete(
                    AudioComposer.create_composite_audio(
                        speech_audio, music_audio, duration
                    )
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
        finally:
            loop.close()

        print(f"✅ Overlay Video created successfully: {output_video_path}")
        return output_video_path

    except Exception as e:
        print(f"❌ Error creating video for {category}: {str(e)}")
        raise
