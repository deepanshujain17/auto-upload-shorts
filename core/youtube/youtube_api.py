from typing import List
import os
import time
from ssl import SSLError

from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError

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

    # Verify file exists and get accurate size
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    print(f"Starting upload of file: {file_path} (Size: {file_size} bytes)")

    # Retry logic for non-resumable upload
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            media = MediaFileUpload(file_path, resumable=False)
            response = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            ).execute()
            video_id = response.get('id')
            if video_id:
                print(f"✅ Video uploaded! Video ID: {video_id}")
                return video_id
            else:
                print(f"⚠️ Unexpected response format: {response}")
                raise ValueError(f"Unexpected response format from YouTube API: {response}")
        except (HttpError, SSLError) as e:
            if attempt < max_retries:
                backoff = 2 ** (attempt - 1)
                print(f"⚠️ Upload attempt {attempt} failed: {e}. Retrying in {backoff}s...")
                time.sleep(backoff)
                continue
            print(f"❌ All {max_retries} upload attempts failed: {e}")
            raise
        except Exception as e:
            if attempt < max_retries and 'EOF occurred in violation of protocol' in str(e):
                backoff = 2 ** (attempt - 1)
                print(f"⚠️ Upload attempt {attempt} encountered SSL EOF error: {e}. Retrying in {backoff}s...")
                time.sleep(backoff)
                continue
            print(f"❌ Upload failed on attempt {attempt}: {e}")
            raise


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
