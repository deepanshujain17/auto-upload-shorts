from typing import Optional

from googleapiclient.discovery import Resource

from core.youtube.youtube_api import add_to_playlist, upload_video
from settings import YouTubeSettings
from utils.metadata.metadata_utils import (
    generate_video_description,
    generate_video_tags,
    generate_video_title
)


def upload_youtube_shorts(
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
