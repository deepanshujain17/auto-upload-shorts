import os
from utils.video_processor import create_overlay_video
from utils.auth import authenticate_youtube
from utils.upload import upload_video

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
    privacy = "private"

    if not os.path.exists(final_video):
        print("🎬 Creating overlay video...")
        output = create_overlay_video(input_video, overlay_image, final_video)
    else:
        print("✅ Overlay video already exists, skipping creation.")
        output = final_video

    print("🔐 Authenticating to YouTube...")
    yt = authenticate_youtube()

    print("🚀 Uploading to YouTube Shorts...")
    upload_video(yt, output, title, description, tags, category, privacy)
