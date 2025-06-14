# Standard library imports
import os
import sys
import asyncio

# Local imports
from core.trends.trends_api_client import get_trending_hashtags
from services.auth import authenticate_youtube
from services.fetch_news import fetch_news_article
from services.shorts_uploader import upload_youtube_shorts
from services.video_processor import create_overlay_video_output
from settings import news_settings, PathSettings, TrendingSettings
from utils.commons import normalize_hashtag


async def process_article(yt, category: str, article: dict, hashtag: str = None) -> None:
    """Process a single article asynchronously."""
    try:
        # Create the overlay video
        overlay_video_output = await create_overlay_video_output(category, article)
        # Upload to YouTube Shorts (semaphore control handled within the function)
        await upload_youtube_shorts(yt, category, overlay_video_output, article, hashtag)
    except Exception as e:
        print(f"Error processing article: {str(e)}")
        raise


async def process_categories(yt) -> None:
    """Process news for each category and upload to YouTube asynchronously."""
    from utils.processing.worker_pool import get_worker_pool
    try:
        # Get the shared worker pool
        video_pool = await get_worker_pool()

        async def process_single_category(category):
            try:
                print(f"\n\n\n📌 Processing category: {category}")
                # Fetch the news articles data
                articles = await fetch_news_article(category)

                # Submit each article processing task to the video pool
                for i, article in enumerate(articles):
                    task_id = f"{category}_{i}"
                    await video_pool.submit(
                        task_id,
                        process_article(yt, category, article)
                    )

                print(f"✅ Submitted all articles for category: {category}")
            except Exception as e:
                print(f"⚠️ Error processing category {category}: {str(e)}")

        # Process all categories concurrently (control happens in the pool)
        category_tasks = [process_single_category(category) for category in news_settings.categories]
        await asyncio.gather(*category_tasks)

        # Wait for all video processing and uploads to complete
        print("\n⏳ Waiting for all video processing and uploads to complete...")
        results = await video_pool.wait_all()

        # Count successful videos
        successful = sum(1 for r in results.values() if r is not None)
        print(f"\n✅ Completed {successful}/{len(results)} videos successfully")

    except Exception as e:
        print(f"❌ Fatal error in category processing: {str(e)}")
        raise


async def process_keywords(yt) -> None:
    """Process news for trending hashtags and manual queries asynchronously."""
    from utils.processing.worker_pool import get_worker_pool
    try:
        # Get trending hashtags and combine with manual queries
        trending_hashtags = await get_trending_hashtags()
        manual_hashtags = TrendingSettings.get_manual_hashtag_queries()
        hashtags = list(dict.fromkeys(manual_hashtags + trending_hashtags))

        if not hashtags:
            print("No hashtags found to process")
            return

        print(f"\n📈 Found {len(hashtags)} hashtags to process:")
        hashtag_sources = {tag: "manual" if tag in manual_hashtags else "trending"
                          for tag in hashtags}

        for idx, tag in enumerate(hashtags, 1):
            print(f"{idx}. {tag} ({hashtag_sources[tag]})")

        # Get the shared worker pool
        video_pool = await get_worker_pool()

        # Process all hashtags concurrently
        async def process_single_hashtag(hashtag):
            try:
                query = normalize_hashtag(hashtag) if hashtag_sources[hashtag] == "trending" else hashtag
                print(f"\n\n\n🔍 Processing hashtag: {hashtag}. Converted query: {query}")

                # Fetch and process articles
                articles = await fetch_news_article(query, is_keyword=True)

                # Submit each article processing task to the video pool
                for i, article in enumerate(articles):
                    task_id = f"{hashtag}_{i}"
                    await video_pool.submit(
                        task_id,
                        process_article(yt, query, article, hashtag)
                    )

                print(f"✅ Submitted all articles for hashtag: {hashtag}")
            except Exception as e:
                print(f"⚠️ Error processing hashtag {hashtag}: {str(e)}")

        # Create tasks for all hashtags to run concurrently
        hashtag_tasks = [process_single_hashtag(hashtag) for hashtag in hashtags]
        await asyncio.gather(*hashtag_tasks)

        # Wait for all video processing and uploads to complete
        print("\n⏳ Waiting for all video processing and uploads to complete...")
        results = await video_pool.wait_all()

        # Count successful videos
        successful = sum(1 for r in results.values() if r is not None)
        print(f"\n✅ Completed {successful}/{len(results)} videos successfully")

    except Exception as e:
        print(f"❌ Fatal error in hashtag processing: {str(e)}")
        raise


async def async_main() -> None:
    """Async main entry point for the script."""
    from core.news.news_api_client import close_session
    from services.video_processor import cleanup_executor
    from services.shorts_uploader import cleanup_upload_executor

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
            news_settings.country = country_arg
        except ValueError as e:
            print(f"Invalid country code: {country_arg}. {str(e)}")
            sys.exit(1)

        # Authenticate to YouTube
        print("🔐 Authenticating to YouTube...")
        yt = authenticate_youtube()

        # Run the specified process
        if process_type in ["categories", "all"]:
            print(f"\n🎯 Starting category processing for country: {news_settings.country}...")
            await process_categories(yt)

        if process_type in ["keywords", "all"]:
            print(f"\n🎯 Starting keyword processing for country: {news_settings.country}...")
            await process_keywords(yt)

        print("\n✨ All processing completed successfully!")

    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)
    finally:
        # Clean up resources
        await close_session()
        await cleanup_executor()
        await cleanup_upload_executor()


if __name__ == "__main__":
    asyncio.run(async_main())
