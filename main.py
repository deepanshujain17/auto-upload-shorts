# Standard library imports
import os
import sys

# Local imports
from core.trends.trends_api_client import get_trending_hashtags
from services.auth import authenticate_youtube
from services.fetch_news import fetch_news_article
from services.shorts_uploader import upload_youtube_shorts
from services.video_processor import create_overlay_video_output
from settings import NewsSettings, PathSettings, TrendingSettings
from utils.commons import normalize_hashtag


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
                print(f"\n\n\n📌 Processing category: {category}")

                # 1. Fetch the news articles data
                articles = fetch_news_article(category)

                for article in articles:
                    # 2. Create the overlay video (includes HTML and image generation)
                    overlay_video_output = create_overlay_video_output(category, article)

                    # 3. Upload the video to YouTube Shorts
                    upload_youtube_shorts(yt, category, overlay_video_output, article)

                print(f"✅ Successfully processed category: {category}")

            except Exception as e:
                print(f"⚠️ Error processing category {category}: {str(e)}")
                print("Moving to next category...")
                continue

    except Exception as e:
        print(f"❌ Fatal error in category processing: {str(e)}")
        raise


def process_keywords(yt) -> None:
    """
    Process news for trending hashtags and manual queries, then upload to YouTube.

    Args:
        yt: Authenticated YouTube API client
    """
    try:
        # Get trending hashtags and combine with manual queries
        trending_hashtags = get_trending_hashtags()
        manual_hashtags = TrendingSettings.get_manual_hashtag_queries()
        hashtags = list(set(trending_hashtags + manual_hashtags))  # Remove duplicates

        print(f"\n📈 Found {len(hashtags)} hashtags to process:")
        for idx, tag in enumerate(hashtags, 1):
            source = "(manual)" if tag in manual_hashtags else "(trending)"
            print(f"{idx}. {tag} {source}")

        if not hashtags:
            print("No hashtags found to process")
            return

        # Process each hashtag
        for hashtag in hashtags:
            try:
                print(f"\n\n\n🔍 Processing hashtag: {hashtag}")
                query = normalize_hashtag(hashtag)

                # 1. Generate news card with is_keyword=True
                articles = fetch_news_article(query, is_keyword=True)

                for article in articles:
                    # 2. Create the overlay video (includes HTML and image generation)
                    overlay_video_output = create_overlay_video_output(query, article)

                    # 3. Upload the video to YouTube Shorts
                    upload_youtube_shorts(yt, query, overlay_video_output, article, hashtag)

                print(f"✅ Successfully processed hashtag: {hashtag}")

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
        country_arg = sys.argv[2].lower() if len(sys.argv) > 2 else "in"

        if process_type not in ["all", "categories", "keywords"]:
            print(f"Invalid process type: {process_type}")
            sys.exit(1)

        try:
            NewsSettings.country = country_arg  # This will use the Pydantic model's setter with validation
        except ValueError as e:
            print(f"Invalid country code: {country_arg}. {str(e)}")
            sys.exit(1)

        # Authenticate to YouTube
        print("🔐 Authenticating to YouTube...")
        yt = authenticate_youtube()

        # Run the specified process
        if process_type in ["categories", "all"]:
            print(f"\n🎯 Starting category processing for country: {NewsSettings.country}...")
            process_categories(yt)

        if process_type in ["keywords", "all"]:
            print(f"\n🎯 Starting keyword processing for country: {NewsSettings.country}...")
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
