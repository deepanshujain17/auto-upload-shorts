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
from settings.language import apply_language
from utils.logging_utils import configure_logging, get_logger, with_context


async def process_article(yt, category: str, article: dict, hashtag: str = None) -> None:
    """Process a single article asynchronously."""
    logger = with_context(get_logger(__name__), category=category, hashtag=hashtag, article_url=article.get("url"))
    try:
        # Create the overlay video
        overlay_video_output = await create_overlay_video_output(category, article)
        # Upload to YouTube Shorts
        await upload_youtube_shorts(yt, category, overlay_video_output, article, hashtag)
    except Exception as e:
        logger.exception("❌ Error processing article")
        raise


async def process_categories(yt) -> None:
    """Process news for each category and upload to YouTube asynchronously."""
    logger = get_logger(__name__)
    try:
        # First, fetch all articles for all categories with a delay between each fetch
        logger.info("📰 Fetching articles for all categories...")
        all_category_articles = {}

        for category in news_settings.categories:
            try:
                logger.info(f"📌 Fetching for category: {category}")
                articles = await fetch_news_article(category)
                all_category_articles[category] = articles
                logger.info(f"✅ Fetched {len(articles)} articles for category: {category}")

                # Add a delay before fetching the next category
                if category != news_settings.categories[-1]:  # No need to wait after the last one
                    await asyncio.sleep(1)

            except Exception as e:
                logger.exception(f"⚠️ Error fetching articles for category {category}")
                # Continue with other categories even if one fails

        # Print summary of all fetched articles
        total_categories_articles_fetched = len(all_category_articles)
        total_articles_fetched = sum(len(articles) for articles in all_category_articles.values())
        logger.info(f"🔍 Total articles fetched: {total_articles_fetched} for {total_categories_articles_fetched} categories")

        # Now process categories with limited concurrency (max 3 categories in parallel)
        async def process_category_articles(category, articles):
            category_logger = with_context(logger, category=category, article_count=len(articles))
            try:
                category_logger.info(f"📌 Processing category: {category} with {len(articles)} articles")

                # Process articles concurrently (since max 2 articles per category)
                tasks = [process_article(yt, category, article) for article in articles]
                await asyncio.gather(*tasks, return_exceptions=True)

                category_logger.info(f"✅ Successfully processed category: {category}")
            except Exception as e:
                category_logger.exception(f"⚠️ Error processing category {category}")

        # Limit concurrent category processing to max 3 using semaphore
        semaphore = asyncio.Semaphore(3)

        async def process_category_with_semaphore(category, articles):
            async with semaphore:
                await process_category_articles(category, articles)
                # Add small delay between category batches to reduce server load
                await asyncio.sleep(1)

        # Create tasks for processing categories with limited concurrency
        category_tasks = [
            process_category_with_semaphore(category, articles)
            for category, articles in all_category_articles.items()
            if articles  # Skip categories with no articles
        ]

        if category_tasks:
            await asyncio.gather(*category_tasks, return_exceptions=True)
            logger.info("✅ Successfully processed all categories")
        else:
            logger.warning("⚠️ No articles found for any category")

    except Exception as e:
        logger.exception("❌ Fatal error in category processing")
        raise


async def process_keywords(yt) -> None:
    """Process news for trending hashtags and manual queries asynchronously."""
    logger = get_logger(__name__)
    try:
        # Get trending hashtags and combine with manual queries
        trending_hashtags = await get_trending_hashtags(TrendingSettings.MAX_HASHTAGS)
        manual_hashtags = TrendingSettings.get_manual_hashtag_queries()
        hashtags = list(dict.fromkeys(manual_hashtags + trending_hashtags))

        if not hashtags:
            logger.warning("⚠️ No hashtags found to process")
            return

        logger.info(f"📈 Found {len(hashtags)} hashtags to process:")
        hashtag_sources = {tag: "manual" if tag in manual_hashtags else "trending"
                          for tag in hashtags}

        for idx, tag in enumerate(hashtags, 1):
            logger.info(f"{idx}. {tag} ({hashtag_sources[tag]})")

        # Fetch all articles for all hashtags synchronously first
        all_hashtag_articles = {}
        for hashtag in hashtags:
            query = normalize_hashtag(hashtag) if hashtag_sources[hashtag] == "trending" else hashtag
            logger.info(f"🔍 Fetching articles for hashtag: {hashtag}. Converted query: {query}")
            articles = await fetch_news_article(query, is_keyword=True)
            if articles:
                all_hashtag_articles[hashtag] = (query, articles)
            logger.info(f"📰 Found {len(articles)} articles for hashtag: {hashtag}")

        # Print summary of all fetched articles
        total_hashtags_articles_fetched = len(all_hashtag_articles)
        total_articles_fetched = sum(len(articles) for query, articles in all_hashtag_articles.values())
        logger.info(f"🔍 Total articles fetched: {total_articles_fetched} for {total_hashtags_articles_fetched} hashtags")

        # Now process hashtags with limited concurrency (max 3 hashtags in parallel)
        async def process_hashtag_articles(hashtag, query_articles_tuple):
            hashtag_logger = with_context(logger, hashtag=hashtag)
            try:
                query, articles = query_articles_tuple
                hashtag_logger = with_context(hashtag_logger, query=query, article_count=len(articles))
                hashtag_logger.info(f"🔍 Processing hashtag: {hashtag} with {len(articles)} articles")

                # Process articles concurrently within each hashtag
                tasks = [process_article(yt, query, article, hashtag) for article in articles]
                await asyncio.gather(*tasks, return_exceptions=True)

                hashtag_logger.info(f"✅ Successfully processed hashtag: {hashtag}")
            except Exception as e:
                hashtag_logger.exception(f"⚠️ Error processing hashtag {hashtag}")

        # Limit concurrent hashtag processing to max 3 using semaphore
        semaphore = asyncio.Semaphore(3)

        async def process_hashtag_with_semaphore(hashtag, query_articles):
            async with semaphore:
                await process_hashtag_articles(hashtag, query_articles)
                # Add small delay between hashtag batches to reduce server load
                await asyncio.sleep(1)

        # Create tasks for processing hashtags with limited concurrency
        hashtag_tasks = [
            process_hashtag_with_semaphore(hashtag, query_articles)
            for hashtag, query_articles in all_hashtag_articles.items()
            if query_articles[1]  # Skip hashtags with no articles
        ]

        if hashtag_tasks:
            await asyncio.gather(*hashtag_tasks, return_exceptions=True)
            logger.info("✅ Successfully processed all hashtags")
        else:
            logger.warning("⚠️ No articles found for any hashtag")

    except Exception as e:
        logger.exception("❌ Fatal error in hashtag processing")
        raise


async def async_main() -> None:
    """Async main entry point for the script."""
    from core.news.news_api_client import close_session
    from services.video_processor import cleanup_executor
    from services.shorts_uploader import cleanup_upload_executor

    try:
        configure_logging()
        logger = get_logger(__name__)
        # Create output directory if it doesn't exist
        os.makedirs(PathSettings.OUTPUT_DIR, exist_ok=True)
        logger.info("🧾 Idempotency: enabled (store: output/history/uploaded.jsonl)")

        # Parse and validate command line arguments
        process_type = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
        country_arg = sys.argv[2].lower() if len(sys.argv) > 2 else "in"

        # Apply language: from CLI arg if present, else default to 'en'
        if len(sys.argv) > 3:
            lang_arg = sys.argv[3].lower()
            try:
                apply_language(lang_arg)
                logger.info(f"🗣️ Applied language: {news_settings.language}")
            except ValueError as e:
                logger.error(str(e))
                sys.exit(1)
        else:
            try:
                apply_language("en")
                logger.info(f"🗣️ Applied default language: {news_settings.language}")
            except ValueError as e:
                logger.error(str(e))
                sys.exit(1)

        if process_type not in ["all", "categories", "keywords"]:
            logger.error(f"Invalid process type: {process_type}")
            sys.exit(1)

        try:
            news_settings.country = country_arg
        except ValueError as e:
            logger.error(f"Invalid country code: {country_arg}. {str(e)}")
            sys.exit(1)

        logger.info(f"🌐 Using country: {news_settings.country}, language: {getattr(news_settings, 'language', 'default')}")

        # Authenticate to YouTube
        logger.info("🔐 Authenticating to YouTube...")
        yt = authenticate_youtube()

        # Run the specified process
        if process_type in ["categories", "all"]:
            logger.info(f"🎯 Starting category processing for country: {news_settings.country}...")
            await process_categories(yt)

        if process_type in ["keywords", "all"]:
            logger.info(f"🎯 Starting keyword processing for country: {news_settings.country}...")
            await process_keywords(yt)

        logger.info("✨ All processing completed successfully!")

    except KeyboardInterrupt:
        logging = get_logger(__name__)
        logging.warning("⚠️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging = get_logger(__name__)
        logging.exception("❌ Fatal error")
        sys.exit(1)
    finally:
        # Clean up resources
        await close_session()
        await cleanup_executor()
        await cleanup_upload_executor()


if __name__ == "__main__":
    asyncio.run(async_main())
