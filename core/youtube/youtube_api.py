from typing import List

from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import Resource

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

    import os
    from googleapiclient.errors import HttpError

    # Verify file exists and get accurate size
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    print(f"Starting upload of file: {file_path} (Size: {file_size} bytes)")

    # Maximum retry attempts for upload
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Create fresh MediaFileUpload object for each attempt
            media = MediaFileUpload(file_path, resumable=True, chunksize=1024*1024)
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

            response = None
            last_progress = 0

            while response is None:
                status, response = request.next_chunk()
                if status:
                    current_progress = int(status.progress() * 100)
                    # Only print progress when it increases by 10%
                    if current_progress - last_progress >= 10:
                        print(f"Upload progress: {current_progress}%")
                        last_progress = current_progress

            print(f"✅ Video uploaded! Video ID: {response['id']}")
            return response["id"]

        except HttpError as e:
            retry_count += 1
            if retry_count < max_retries:
                print(f"⚠️ Upload failed (attempt {retry_count}/{max_retries}): {str(e)}")
                print(f"Retrying upload...")
                # Sleep before retry to avoid rate limits
                import time
                time.sleep(5)
            else:
                print(f"❌ Upload failed after {max_retries} attempts: {str(e)}")
                raise e
        except Exception as e:
            print(f"❌ Unexpected error during upload: {str(e)}")
            raise e


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
