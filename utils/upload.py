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
        # Generate dynamic tags from article content
        article_tags = [tag for tag, _ in generate_tags_with_frequency(article)]

        # Combine with default tags, ensure uniqueness, and limit total tags
        combined_tags = list(dict.fromkeys([category] + article_tags + YouTubeSettings.DEFAULT_TAGS))[:10]  # YouTube allows max 10 tags

        article_title = ' '.join(article.get("title", "No Title").split()[:8])
        title = f"Breaking News: {article_title}"

        article_description = article.get("description", "No Description")
        article_tags_str = " ".join([f"#{tag}" for tag in article_tags])
        description = f"{article_description} {article_tags_str} #{category} #news #update #trends #shorts"

        youtube_category = YouTubeSettings.DEFAULT_CATEGORY
        privacy = YouTubeSettings.DEFAULT_PRIVACY

        print(f"🚀 Uploading {category} video to YouTube Shorts...")
        upload_video(yt, overlay_video_output, title, description, combined_tags, youtube_category, privacy)
    except Exception as e:
        print(f"❌ Error uploading video for {category}: {str(e)}")
        raise

