import os

from utils.video_processor import create_overlay_video_output
from utils.auth import authenticate_youtube
from utils.upload import upload_youtube_shorts
from news.news_fetcher import generate_news_card
from settings import NewsSettings, PathSettings


if __name__ == "__main__":
    # 📝 Set your input and metadata here
    os.makedirs(PathSettings.OUTPUT_DIR, exist_ok=True)

    try:
        # Authenticate to YouTube once before the loop
        print("🔐 Authenticating to YouTube...")
        yt = authenticate_youtube()

        # Process each category
        for category in NewsSettings.CATEGORIES:
            try:
                print(f"\n📌 Processing category: {category}")

                # 1. Generate the news card image and get article data
                article, overlay_image = generate_news_card(category)

                # 2. Create the overlay video
                overlay_video_output = create_overlay_video_output(category, overlay_image)

                # 3. Upload the video to YouTube Shorts
                upload_youtube_shorts(yt, category, overlay_video_output, article)

                print(f"✅ Successfully processed {category}")
            except Exception as e:
                print(f"⚠️ Failed to process category {category}. Moving to next category...")
                continue
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")

