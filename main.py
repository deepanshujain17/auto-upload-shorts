import pickle
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- CONFIG ---
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_PICKLE = "token.pkl"

# --- VIDEO PROCESSING ---
def create_overlay_video(video_path, image_path, output_path="output_with_overlay.mp4"):
    video = VideoFileClip(video_path)
    image = (
        ImageClip(image_path)
        .with_duration(video.duration)
        .resized(height=500)  # Resize image to desired height
        # .with_position(("center", "bottom"))  # position: bottom center
        # .with_position((0.1,0.5), relative=True) # position: 50% from left and 60% from top
        .with_position(("center", video.h // 2 + 100))
    )
    final = CompositeVideoClip([video, image])
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

# --- AUTHENTICATION ---
def authenticate_youtube():
    creds = None

    # 🔁 Reuse token if it exists
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as token:
            creds = pickle.load(token)

    # 🔐 If no (valid) token, do full OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # 💾 Save token for next time
        with open(TOKEN_PICKLE, "wb") as token:
            pickle.dump(creds, token)

    # ✅ Build YouTube client
    return build("youtube", "v3", credentials=creds)

# --- UPLOAD ---
def upload_video(youtube, file_path, title, description, tags, category_id, privacy_status):
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

# --- MAIN ---
if __name__ == "__main__":
    # 📝 Set your input and metadata here
    os.makedirs("output", exist_ok=True)

    input_video = "videos/video1.mp4"
    overlay_image = "images/image1.jpeg"
    final_video = "output/short_with_overlay.mp4"

    title = "My Short with Overlay"
    description = "Auto-uploaded via Python!"
    tags = ["shorts", "python"]
    category = "22"  # People & Blogs
    privacy = "public"

    print("🎬 Creating overlay video...")
    output = create_overlay_video(input_video, overlay_image, final_video)

    print("🔐 Authenticating to YouTube...")
    yt = authenticate_youtube()

    print("🚀 Uploading to YouTube Shorts...")
    upload_video(yt, output, title, description, tags, category, privacy)
