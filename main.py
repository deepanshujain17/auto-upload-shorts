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
        # Upload to YouTube Shorts
        await upload_youtube_shorts(yt, category, overlay_video_output, article, hashtag)
    except Exception as e:
        print(f"Error processing article: {str(e)}")
        raise


async def process_categories(yt) -> None:
    """Process news for each category and upload to YouTube asynchronously."""
    try:
        # Create a semaphore to limit concurrent API requests
        # This prevents making too many requests at once
        api_semaphore = asyncio.Semaphore(2)  # Allow only 2 concurrent API calls

        async def fetch_articles_for_category(category):
            """Fetch articles for a single category with rate limiting"""
            try:
                print(f"\n📌 Fetching news for category: {category}")
                # Use semaphore to limit concurrent API calls
                async with api_semaphore:
                    # Fetch the news articles data with rate limiting
                    articles = await fetch_news_article(category)
                    # Add a small delay between API calls to avoid rate limiting
                    await asyncio.sleep(1)
                    return category, articles
            except Exception as e:
                print(f"⚠️ Error fetching news for category {category}: {str(e)}")
                return category, None

        # Step 1: Fetch articles for all categories with rate limiting
        # Create tasks for fetching articles, which will respect the semaphore
        fetch_tasks = [fetch_articles_for_category(category) for category in news_settings.categories]

        # Execute fetch tasks one by one, with a delay between them to respect rate limits
        # but allow them to run concurrently up to the semaphore limit
        fetch_results = await asyncio.gather(*fetch_tasks)

        # Step 2: Process articles concurrently for all categories where fetching succeeded
        processing_tasks = []

        for category, articles in fetch_results:
            if articles:
                print(f"\n📊 Processing articles for category: {category}")
                # For each article in this category, create a processing task
                for article in articles:
                    processing_tasks.append(process_article(yt, category, article))

        # Run all processing tasks in parallel - no rate limiting needed here
        if processing_tasks:
            await asyncio.gather(*processing_tasks)

        print(f"✅ Successfully processed all categories")

    except Exception as e:
        print(f"❌ Fatal error in category processing: {str(e)}")
        raise


async def process_keywords(yt) -> None:
    """Process news for trending hashtags and manual queries asynchronously."""
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

        # Process all hashtags concurrently
        async def process_single_hashtag(hashtag):
            try:
                query = normalize_hashtag(hashtag) if hashtag_sources[hashtag] == "trending" else hashtag
                print(f"\n\n\n🔍 Processing hashtag: {hashtag}. Converted query: {query}")

                # Fetch and process articles
                articles = await fetch_news_article(query, is_keyword=True)

                # Process articles concurrently
                tasks = [process_article(yt, query, article, hashtag) for article in articles]
                await asyncio.gather(*tasks)

                print(f"✅ Successfully processed hashtag: {hashtag}")
            except Exception as e:
                print(f"⚠️ Error processing hashtag {hashtag}: {str(e)}")

        # Create tasks for all hashtags to run concurrently
        hashtag_tasks = [process_single_hashtag(hashtag) for hashtag in hashtags]
        await asyncio.gather(*hashtag_tasks)

    except Exception as e:
        print(f"�� Fatal error in hashtag processing: {str(e)}")
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
