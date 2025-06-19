from typing import Optional, List, Dict, Any
import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor

from googleapiclient.discovery import Resource

from core.youtube.youtube_api import add_to_playlist, upload_video
from settings import YouTubeSettings
from utils.metadata.metadata_utils import (
    generate_video_description,
    generate_video_tags,
    generate_video_title
)

# Shared thread pool executor
_upload_executor: Optional[ThreadPoolExecutor] = None
_upload_executor_lock = asyncio.Lock()

def get_upload_executor() -> ThreadPoolExecutor:
    """Get or create the shared thread pool executor for uploads."""
    global _upload_executor
    if _upload_executor is None:
        # YouTube API operations are network-bound but can be quite heavy
        # Use a smaller pool to avoid overwhelming the API
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        _upload_executor = ThreadPoolExecutor(max_workers=max(cpu_count * 2, 8))
    return _upload_executor

async def cleanup_upload_executor():
    """Cleanup the shared executor."""
    global _upload_executor
    async with _upload_executor_lock:
        if _upload_executor is not None:
            _upload_executor.shutdown(wait=True)
            _upload_executor = None

async def _run_in_upload_executor(func, *args, **kwargs):
    """Helper function to run a synchronous function in the upload executor."""
    loop = asyncio.get_running_loop()
    executor = get_upload_executor()
    return await loop.run_in_executor(executor, functools.partial(func, *args, **kwargs))

async def upload_youtube_shorts(
    yt: Resource,
    category: str,
    overlay_video_output: str,
    article: dict,
    hashtag: Optional[str] = None
) -> None:
    """
    Upload the generated video to YouTube Shorts asynchronously.

    Args:
        yt: YouTube API client
        category: News category to process
        overlay_video_output: Path to the final video
        article: The news article data used for tag generation
        hashtag: Optional hashtag to include in the video metadata

    Raises:
        Exception: If upload fails
    """
    try:
        # These metadata generation functions are CPU-light and can run in the main thread
        article_tags, combined_tags = generate_video_tags(article, category, hashtag)
        print(f"Combined tags: {combined_tags}")

        title = generate_video_title(article, article_tags, hashtag)
        print(f"Title: {title}")

        description = generate_video_description(article, combined_tags)
        print(f"Description: {description}")

        # Get YouTube category and privacy settings
        youtube_category = str(YouTubeSettings.CATEGORY_TO_YOUTUBE_CATEGORY_MAP.get(
            category.lower(),
            YouTubeSettings.DEFAULT_YOUTUBE_CATEGORY
        ))
        privacy = YouTubeSettings.DEFAULT_PRIVACY

        # TODO: Check in cache with title, if it exists already skip upload.
        print(f"🚀 Uploading '{category}' video to YouTube Shorts...")

        # Run the upload operation in the executor (network-bound but potentially slow)
        video_id = await _run_in_upload_executor(
            upload_video,
            yt,
            overlay_video_output,
            title,
            description,
            combined_tags[:YouTubeSettings.MAX_TAGS],
            youtube_category,
            privacy
        )

        # Also run the playlist addition in the executor
        if video_id:
            await _run_in_upload_executor(add_to_playlist, yt, video_id, category)
            print(f"✅ Successfully uploaded video for {category} and added to playlist")

        return video_id
    except Exception as e:
        print(f"❌ Error uploading YouTube Short for {category}: {str(e)}")
        raise
