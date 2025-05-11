from googleapiclient.http import MediaFileUpload

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
