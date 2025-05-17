import os

from utils.video_processor import create_overlay_video_output
from utils.auth import authenticate_youtube
from news.utils.commons import normalize_hashtag
from utils.upload import upload_youtube_shorts
from news.news_fetcher import generate_news_card
from news.utils.trending_utils import get_trending_hashtags
from settings import NewsSettings, PathSettings


def process_categories(yt):
    """Process news for each category and upload to YouTube."""
    try:
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


def process_keywords(yt):
    """Process news for trending hashtags and upload to YouTube."""
    try:
        # Get trending hashtags
        hashtags = get_trending_hashtags()
        if not hashtags:
            print("No trending hashtags found")
            return

        # Process each hashtag
        for hashtag in hashtags:
            try:
                print(f"\n🔍 Processing hashtag: {hashtag}")
                query = normalize_hashtag(hashtag)

                # Generate news card with is_keyword=True
                article, overlay_image = generate_news_card(query, is_keyword=True)

                # Create the overlay video
                overlay_video_output = create_overlay_video_output(query, overlay_image)

                # Upload the video to YouTube Shorts
                upload_youtube_shorts(yt, query, overlay_video_output, article)

                print(f"✅ Successfully processed hashtag {hashtag}")
            except Exception as e:
                print(f"⚠️ Failed to process hashtag {hashtag}: {str(e)}")
                continue
    except Exception as e:
        print(f"❌ Fatal error in hashtag processing: {str(e)}")


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs(PathSettings.OUTPUT_DIR, exist_ok=True)

    try:
        # Authenticate to YouTube once before the loop
        print("🔐 Authenticating to YouTube...")
        yt = authenticate_youtube()

        # Choose which process to run
        process_categories(yt)  # For category-based news
        process_keywords(yt)    # For trending hashtags
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")

