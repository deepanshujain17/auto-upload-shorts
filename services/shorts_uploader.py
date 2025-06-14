from typing import Optional
import asyncio
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

# Semaphore to limit concurrent YouTube uploads
# This helps prevent YouTube API rate limiting and quota issues
_upload_semaphore: Optional[asyncio.Semaphore] = None

def get_upload_executor() -> ThreadPoolExecutor:
    """Get or create the shared thread pool executor for uploads."""
    global _upload_executor
    if _upload_executor is None:
        _upload_executor = ThreadPoolExecutor(max_workers=3)
    return _upload_executor

def get_upload_semaphore() -> asyncio.Semaphore:
    """Get the semaphore that limits concurrent YouTube uploads."""
    global _upload_semaphore
    if _upload_semaphore is None:
        # Limit to 3 concurrent uploads to prevent YouTube API rate limiting
        _upload_semaphore = asyncio.Semaphore(3)
    return _upload_semaphore

async def cleanup_upload_executor():
    """Cleanup the shared executor."""
    global _upload_executor
    async with _upload_executor_lock:
        if _upload_executor is not None:
            _upload_executor.shutdown(wait=True)
            _upload_executor = None

async def upload_youtube_shorts(
    yt: Resource,
    category: str,
    overlay_video_output: str,
    article: dict,
    hashtag: Optional[str] = None
) -> None:
    """Upload a video to YouTube Shorts with semaphore control."""
    # Acquire the upload semaphore to limit concurrent uploads
    upload_semaphore = get_upload_semaphore()
    async with upload_semaphore:
        print(f"🚦 Acquired upload semaphore for {category} video")
        loop = asyncio.get_running_loop()
        executor = get_upload_executor()
        try:
            return await loop.run_in_executor(
                executor,
                _upload_youtube_shorts_sync,
                yt, category, overlay_video_output, article, hashtag
            )
        finally:
            print(f"🚦 Released upload semaphore for {category} video")

def _upload_youtube_shorts_sync(
    yt: Resource,
    category: str,
    overlay_video_output: str,
    article: dict,
    hashtag: Optional[str] = None
) -> None:
    """
    Upload the generated video to YouTube Shorts.

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
        # Generate tags, title and description
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
        print(f"🚀 Uploading {category} video to YouTube Shorts...")
        video_id = upload_video(
            yt,
            overlay_video_output,
            title,
            description,
            combined_tags[:YouTubeSettings.MAX_TAGS],
            youtube_category,
            privacy
        )

        # Add video to the respective category playlist
        add_to_playlist(yt, video_id, category)

    except Exception as e:
        print(f"❌ Error uploading video for {category}: {str(e)}")
        raise
