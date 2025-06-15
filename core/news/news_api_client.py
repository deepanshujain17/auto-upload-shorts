import asyncio
import aiohttp
from typing import List, Dict, Any

from settings import news_settings
from utils.commons import get_zulu_time_minus
from core.news.hashtag_storage import HashtagStorage

# Shared session instance
_session: aiohttp.ClientSession = None

async def get_session() -> aiohttp.ClientSession:
    """Get or create the shared aiohttp ClientSession."""
    global _session
    if _session is None or _session.closed:
        # Create a ClientSession with SSL verification disabled to handle certificate issues
        ssl_context = False  # This disables SSL verification
        _session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
    return _session

async def close_session():
    """Close the shared session."""
    global _session
    if _session and not _session.closed:
        await _session.close()

async def get_category_news(category=None) -> List[Dict[str, Any]]:
    """
    Asynchronously fetch news articles from GNews API for given categories

    Raises:
        ValueError: If no articles are found for the given category
        aiohttp.ClientError: If there's a network error
    """
    print(f"📰 Fetching news for category: {category}")
    from_time = get_zulu_time_minus(news_settings.minutes_ago)

    params = {
        "from": from_time,
        "category": category,
        "lang": news_settings.language,
        "country": news_settings.country,
        "max": news_settings.max_articles,
        "apikey": news_settings.api_key,
        "sortby": news_settings.sort_by,
    }

    try:
        session = await get_session()
        async with session.get(news_settings.top_headlines_endpoint, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            articles = data.get("articles", [])
            if articles:
                result = articles[:news_settings.max_articles]
                print(f"✅ Successfully fetched article for {category}")
                return result
            else:
                raise ValueError(f"🔍 No articles found for category: {category}")
    except aiohttp.ClientError as e:
        print(f"Network error while fetching {category}: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error while fetching {category}: {str(e)}")
        raise


async def get_keyword_news(query: str) -> List[Dict[str, Any]]:
    """
    Asynchronously fetch news article from GNews API using a search query.
    Implements exponential backoff for rate limiting (HTTP 429).
    Checks if the query was already processed today to avoid duplicates.

    Args:
        query (str): The keyword to search for

    Returns:
        List[Dict[str, Any]]: The matching articles if found

    Raises:
        ValueError: If no articles are found or query was already processed today
        aiohttp.ClientError: If there's a network error after all retries
    """
    if HashtagStorage.is_hashtag_processed_today(f"{query}_{news_settings.country}"):
        raise ValueError(f"🔄 Query '{query}' was already processed today for country {news_settings.country}")

    from_time = get_zulu_time_minus(news_settings.minutes_ago)

    params = {
        "q": query,
        "from": from_time,
        "lang": news_settings.language,
        "country": news_settings.country,
        "max": news_settings.max_articles,
        "apikey": news_settings.api_key,
        "sortby": news_settings.sort_by,
    }

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            session = await get_session()
            async with session.get(news_settings.search_endpoint, params=params) as response:
                # Handle rate limiting with exponential backoff
                if response.status == 429:
                    wait_time = 2 ** attempt  # 1, 2, 4 seconds
                    print(f"⏳ Rate limited. Waiting {wait_time} seconds before retry {attempt + 1}/{max_attempts}")
                    await asyncio.sleep(wait_time)
                    continue

                response.raise_for_status()
                data = await response.json()
                found_articles = data.get("articles", [])
                if found_articles:
                    result = found_articles[:2]
                    # Save the successful query to history with country code
                    HashtagStorage.save_hashtag(f"{query}_{news_settings.country}")
                    print(f"✅ Successfully fetched article for {query}")
                    return result
                else:
                    raise ValueError(f"🔍 No articles found for query: {query}")

        except ValueError as ve:
            print(str(ve))
            raise
        except aiohttp.ClientError as e:
            if attempt == max_attempts - 1:  # Last attempt
                print(f"Network error while fetching news for {query}: {str(e)}")
                raise
            wait_time = 2 ** attempt
            print(f"⚠️ Network error on attempt {attempt + 1}/{max_attempts}. Waiting {wait_time} seconds before retry...")
            await asyncio.sleep(wait_time)
            continue
        except Exception as e:
            print(f"Unexpected error while fetching news for {query}: {str(e)}")
            raise

    # If we get here, all retries failed
    raise aiohttp.ClientError(f"Failed to fetch news after {max_attempts} attempts")
