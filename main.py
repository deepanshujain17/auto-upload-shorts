import os
import sys

from utils.video_processor import create_overlay_video_output
from utils.auth import authenticate_youtube
from utils.shorts_uploader import upload_youtube_shorts
from news.utils.commons import normalize_hashtag
from news.news_fetcher import generate_news_card
from news.utils.trending_utils import get_trending_hashtags
from settings import NewsSettings, PathSettings


def process_categories(yt) -> None:
    """
    Process news for each category and upload to YouTube.

    Args:
        yt: Authenticated YouTube API client
    """
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
                print(f"⚠️ Error processing category {category}: {str(e)}")
                print("Moving to next category...")
                continue

    except Exception as e:
        print(f"❌ Fatal error in category processing: {str(e)}")
        raise


def process_keywords(yt) -> None:
    """
    Process news for trending hashtags and upload to YouTube.

    Args:
        yt: Authenticated YouTube API client
    """
    try:
        # Get trending hashtags
        hashtags = get_trending_hashtags()
        print(f"\n📈 Found {len(hashtags)} trending hashtags:")
        for idx, tag in enumerate(hashtags, 1):
            print(f"{idx}. {tag}")

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
                upload_youtube_shorts(yt, query, overlay_video_output, article, hashtag)

                print(f"✅ Successfully processed hashtag {hashtag}")

            except Exception as e:
                print(f"⚠️ Error processing hashtag {hashtag}: {str(e)}")
                print("Moving to next hashtag...")
                continue

    except Exception as e:
        print(f"❌ Fatal error in hashtag processing: {str(e)}")
        raise


def main() -> None:
    """Main entry point for the script."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(PathSettings.OUTPUT_DIR, exist_ok=True)

        # Parse and validate command line arguments
        process_type = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
        if process_type not in ["all", "categories", "keywords"]:
            print(f"Invalid process type: {process_type}")
            sys.exit(1)

        # Authenticate to YouTube
        print("🔐 Authenticating to YouTube...")
        yt = authenticate_youtube()

        # Run the specified process
        if process_type in ["categories", "all"]:
            print("\n🎯 Starting category processing...")
            process_categories(yt)

        if process_type in ["keywords", "all"]:
            print("\n🎯 Starting keyword processing...")
            process_keywords(yt)

        print("\n✨ All processing completed successfully!")

    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
