from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import functools

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

def get_executor() -> ThreadPoolExecutor:
    """Get or create the shared thread pool executor."""
    global _shared_executor
    if _shared_executor is None:
        # Increase number of workers for better parallelism
        # Using CPU count or slightly higher for IO-bound portions
        import multiprocessing
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

async def _run_in_executor(func, *args, **kwargs):
    """Helper function to run a synchronous function in the executor."""
    loop = asyncio.get_running_loop()
    executor = get_executor()
    return await loop.run_in_executor(executor, functools.partial(func, *args, **kwargs))

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
            # Run HTML creation in executor
            await _run_in_executor(create_html_card, article, html_output)
            # Run image rendering in executor
            await _run_in_executor(render_card_to_image, html_output, overlay_image)

            print(f"✅ Overlay image created: {overlay_image}")
            return overlay_image
        finally:
            # Release locks in reverse order
            await FileLock.release(overlay_image)
            await FileLock.release(html_output)
    except Exception as e:
        print(f"Error in _generate_overlay_image: {str(e)}")
        raise

async def create_overlay_video_output(category: str, article: dict) -> str:
    """Create an overlay video asynchronously using the shared executor."""
    try:
        # Get file paths that need locking
        output_video_path = PathSettings.get_final_video(category)
        await FileLock.acquire(output_video_path)

        try:
            # Generate the overlay image
            overlay_image = await _generate_overlay_image(category, article)

            # Get background assets
            bg_image = PathSettings.get_image_path(
                news_settings.category_bg_image.get(category, news_settings.category_bg_image["default"])
            )
            bg_music = PathSettings.get_music_path(
                news_settings.category_bgm.get(category, news_settings.category_bgm["default"])
            )
            print(f"📸 Using background image: {bg_image}")
            print(f"🎵 Using background music: {bg_music}")

            # Validate input files
            for path in [bg_image, bg_music, overlay_image]:
                if not await _run_in_executor(Path(path).is_file):
                    raise FileNotFoundError(f"Required file not found: {path}")

            # Ensure output directory exists
            await _run_in_executor(lambda: Path(output_video_path).parent.mkdir(parents=True, exist_ok=True))

            # Generate article audio
            print("🎙️ Generating audio from article...")
            speech_audio = await AudioComposer.generate_article_audio(article)
            duration = speech_audio.duration

            # Load audio and image files in executor
            bg_audio_clip = await _run_in_executor(AudioFileClip, bg_music)
            try:
                # Configure & Create composite audio
                combined_audio = await AudioComposer.create_composite_audio(
                    speech_audio, bg_audio_clip, duration
                )
                print("✅ Audio generated and combined successfully")

                # Load image clips in executor
                bg_clip = await _run_in_executor(ImageClip, bg_image)
                overlay_clip = await _run_in_executor(ImageClip, overlay_image)

                try:
                    # Create composite video
                    composite_video = await _run_in_executor(
                        VideoComposer.create_composite_video,
                        bg_clip, overlay_clip, combined_audio, duration
                    )

                    # Write video file in executor (this is CPU intensive)
                    await _run_in_executor(
                        composite_video.write_videofile,
                        output_video_path,
                        fps=VideoSettings.FPS,
                        codec=VideoSettings.VIDEO_CODEC,
                        audio_codec=VideoSettings.AUDIO_CODEC,
                        logger=None
                    )
                finally:
                    # Clean up resources
                    await _run_in_executor(lambda: bg_clip.close() if hasattr(bg_clip, 'close') else None)
                    await _run_in_executor(lambda: overlay_clip.close() if hasattr(overlay_clip, 'close') else None)
                    if hasattr(composite_video, 'close'):
                        await _run_in_executor(composite_video.close)
            finally:
                # Safely close background audio clip if available
                if hasattr(bg_audio_clip, 'close') and bg_audio_clip is not None:
                    await _run_in_executor(bg_audio_clip.close)

            print(f"✅ Overlay Video created successfully: {output_video_path}")
            return output_video_path
        finally:
            await FileLock.release(output_video_path)
    except Exception as e:
        print(f"❌ Error creating video for {category}: {str(e)}")
        raise
