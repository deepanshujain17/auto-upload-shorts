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
from utils.idempotency_store import make_upload_key, mark_uploaded, was_uploaded
from utils.logging_utils import get_logger, with_context
from settings import news_settings, PathSettings

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
    logger = with_context(
        get_logger(__name__),
        category=category,
        country=getattr(news_settings, "country", None),
        language=getattr(news_settings, "language", None),
        hashtag=hashtag,
        article_url=article.get("url"),
    )
    try:
        # These metadata generation functions are CPU-light and can run in the main thread
        article_tags, combined_tags = generate_video_tags(article, category, hashtag)
        with_context(logger, tag_count=len(combined_tags)).info("🏷️ Combined tags generated")

        title = generate_video_title(article, article_tags, hashtag)
        with_context(logger, title=title).info("📝 Title generated")

        description = generate_video_description(article, combined_tags)
        with_context(logger, description_len=len(description)).info("📄 Description generated")

        # Get YouTube category and privacy settings
        youtube_category = str(YouTubeSettings.CATEGORY_TO_YOUTUBE_CATEGORY_MAP.get(
            category.lower(),
            YouTubeSettings.DEFAULT_YOUTUBE_CATEGORY
        ))
        privacy = YouTubeSettings.DEFAULT_PRIVACY

        store_path = f"{PathSettings.OUTPUT_DIR}/history/uploaded.jsonl"
        key = make_upload_key(
            article=article,
            country=str(getattr(news_settings, "country", "")),
            language=str(getattr(news_settings, "language", "")),
        )
        if await was_uploaded(store_path=store_path, key=key):
            with_context(logger, store_path=store_path).warning("⏭️ Skipping upload (already uploaded)")
            return None

        with_context(logger, video_path=overlay_video_output).info(f"🚀 Uploading '{category}' video to YouTube Shorts...")

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
            await mark_uploaded(
                store_path=store_path,
                key=key,
                video_id=video_id,
                article=article,
                country=str(getattr(news_settings, "country", "")),
                language=str(getattr(news_settings, "language", "")),
                category=category,
                hashtag=hashtag,
            )
            with_context(logger, video_id=video_id, store_path=store_path).info(
                f"✅ Successfully uploaded video for {category} and added to playlist"
            )

        return video_id
    except Exception as e:
        logger.exception(f"❌ Error uploading YouTube Short for {category}")
        raise
