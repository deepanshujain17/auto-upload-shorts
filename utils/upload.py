from googleapiclient.http import MediaFileUpload
from news.utils.tag_utils import generate_tags_with_frequency
from settings import YouTubeSettings

def upload_video(youtube, file_path, title, description, tags, category_id, privacy_status):
    """
    Upload a video to YouTube

    Args:
        youtube: Authenticated YouTube API client
        file_path (str): Path to the video file
        title (str): Video title
        description (str): Video description
        tags (list): List of video tags
        category_id (str): YouTube category ID
        privacy_status (str): Privacy status ('private', 'unlisted', or 'public')

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

def add_to_playlist(youtube, video_id, category):
    """
    Add a video to a YouTube playlist

    Args:
        youtube: Authenticated YouTube API client
        video_id (str): ID of the video to add
        category (str): Content category to which the video belongs
    """
    try:
        # Get the playlist ID from the category mapping. If not category (keyword search), use the default playlist ID.
        playlist_id = YouTubeSettings.CATEGORY_PLAYLIST_MAP.get(category.lower(), YouTubeSettings.DEFAULT_PLAYLIST_ID)
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

def upload_youtube_shorts(yt, category, overlay_video_output, article):
    """
    Upload the generated video to YouTube Shorts.
    Args:
        yt: YouTube API client
        category (str): News category to process
        overlay_video_output: Path to the final video
        article: The news article data used for tag generation
    Raises:
        Exception: If upload fails
    """
    try:
        # Useful when category is not a single word (query)
        category_tags = category.split()
        # Generate dynamic tags from article content
        article_tags = [tag for tag, _ in generate_tags_with_frequency(article,
                                                                       max_tags=YouTubeSettings.ARTICLE_MAX_TAGS)]

        # Combine with default tags, ensure uniqueness, and limit total tags to MAX_TAGS
        combined_tags = list(dict.fromkeys(
            category_tags +
            article_tags +
            YouTubeSettings.DEFAULT_TAGS))[:YouTubeSettings.MAX_TAGS]

        article_title = ' '.join(article.get("title", "No Title").split()[:8])
        title = f"Breaking News: {article_title}"

        article_description = article.get("description", "No Description")
        category_tags_str = " ".join([f"#{tag}" for tag in category_tags])
        article_tags_str = " ".join([f"#{tag}" for tag in article_tags])
        description = f"{article_description} {category_tags_str} {article_tags_str} #{category} #news #update #trends #shorts"

        # Get YouTube category ID from mapping, fallback to default if not found
        youtube_category = str(YouTubeSettings.CATEGORY_TO_YOUTUBE_CATEGORY_MAP.get(category.lower(), YouTubeSettings.DEFAULT_YOUTUBE_CATEGORY))
        privacy = YouTubeSettings.DEFAULT_PRIVACY

        print(f"🚀 Uploading {category} video to YouTube Shorts...")
        video_id = upload_video(yt, overlay_video_output, title, description, combined_tags, youtube_category, privacy)

        # Add video to the respective category playlist
        add_to_playlist(yt, video_id, category)

    except Exception as e:
        print(f"❌ Error uploading video for {category}: {str(e)}")
        raise

