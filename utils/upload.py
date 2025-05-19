from typing import List, Optional

from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import Resource

from news.utils.tag_utils import generate_tags_with_frequency
from settings import YouTubeSettings


def upload_video(
    youtube: Resource,
    file_path: str,
    title: str,
    description: str,
    tags: List[str],
    category_id: str,
    privacy_status: str
) -> str:
    """
    Upload a video to YouTube

    Args:
        youtube: Authenticated YouTube API client
        file_path: Path to the video file
        title: Video title
        description: Video description
        tags: List of video tags
        category_id: YouTube category ID
        privacy_status: Privacy status ('private', 'unlisted', or 'public')

    Returns:
        str: Uploaded video ID
    """
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {"privacyStatus": privacy_status}
    }

    media = MediaFileUpload(file_path, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None

    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    print(f"✅ Video uploaded! Video ID: {response['id']}")
    return response["id"]


def add_to_playlist(youtube: Resource, video_id: str, category: str) -> None:
    """
    Add a video to a YouTube playlist

    Args:
        youtube: Authenticated YouTube API client
        video_id: ID of the video to add
        category: Content category to which the video belongs
    """
    try:
        # Get the playlist ID from the category mapping
        playlist_id = YouTubeSettings.CATEGORY_PLAYLIST_MAP.get(
            category.lower(),
            YouTubeSettings.DEFAULT_PLAYLIST_ID
        )

        if not playlist_id:
            print(f"⚠️ Playlist ID not found for category: {category}")
            return

        add_to_playlist_request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        add_to_playlist_request.execute()
        print(f"📁 Video added to playlist: {playlist_id}")

    except Exception as e:
        print(f"⚠️ Failed to add video to playlist: {str(e)}")


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
        # Handle category tags based on whether this is a trending query or category
        if hashtag:
            category_tags = category.split() + YouTubeSettings.DEFAULT_HASHTAGS
        else:
            category_tags = YouTubeSettings.CATEGORY_HASHTAG_MAP.get(category.lower(), [])

        # Generate dynamic tags from article content
        article_tags = [
            tag for tag, _ in generate_tags_with_frequency(
                article,
                max_tags=YouTubeSettings.ARTICLE_MAX_TAGS
            )
        ]

        # Combine tags ensuring uniqueness and proper limits
        hashtag_tags = [hashtag.lstrip("#")] if hashtag else []
        combined_tags = list(dict.fromkeys(
            hashtag_tags +
            article_tags +
            category_tags
        ))[:YouTubeSettings.MAX_TAGS]

        print(f"Combined tags: {combined_tags}")

        # Prepare video title
        article_title = ' '.join(article.get("title", "No Title").split()[:12])
        # If hashtag, append hashtag in title else use first article tag
        title_hashtag_str = f"{hashtag}" if hashtag else f"#{article_tags[0]}"
        title = f"Breaking News: {article_title} {title_hashtag_str}"

        # Prepare video description
        article_description = article.get("description", "No Description")
        category_tags_str = " ".join([f"#{tag}" for tag in category_tags])
        article_tags_str = " ".join([f"#{tag}" for tag in article_tags])

        description = (
            f"{article_description} {hashtag} {article_tags_str} {category_tags_str}"
            if hashtag else
            f"{article_description} {article_tags_str} {category_tags_str}"
        )

        # Get YouTube category and privacy settings
        youtube_category = str(YouTubeSettings.CATEGORY_TO_YOUTUBE_CATEGORY_MAP.get(
            category.lower(),
            YouTubeSettings.DEFAULT_YOUTUBE_CATEGORY
        ))
        privacy = YouTubeSettings.DEFAULT_PRIVACY

        print(f"🚀 Uploading {category} video to YouTube Shorts...")
        video_id = upload_video(
            yt,
            overlay_video_output,
            title,
            description,
            combined_tags,
            youtube_category,
            privacy
        )

        # Add video to the respective category playlist
        add_to_playlist(yt, video_id, category)

    except Exception as e:
        print(f"❌ Error uploading video for {category}: {str(e)}")
        raise

