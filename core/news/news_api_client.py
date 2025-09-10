import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
import time

from settings import news_settings
from utils.commons import get_zulu_time_minus

# Shared session instance
_session: Optional[aiohttp.ClientSession] = None

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


def _require_api_key(context: str) -> None:
    """Ensure a non-empty API key is configured before making requests.

    Args:
        context: A short label like 'category' or 'keyword' for error messages.

    Raises:
        ValueError: If the API key is missing.
    """
    if not getattr(news_settings, "api_key", None):
        lang = getattr(news_settings, "language", "en")
        expected_env = "GNEWS_HI_API_KEY" if lang == "hi" else "GNEWS_API_KEY"
        raise ValueError(
            f"Missing GNews API key for {context} requests. Set {expected_env} and ensure apply_language('{lang}') runs before API calls."
        )

async def get_category_news(category=None) -> List[Dict[str, Any]]:
    """
    Asynchronously fetch news articles from GNews API for given categories
    Implements exponential backoff for rate limiting (HTTP 429).

    Returns:
        List[Dict[str, Any]]: The matching articles if found or empty list if none found

    Raises:
        aiohttp.ClientError: If there's a network error after all retries
    """
    # Validate API key before making any requests
    _require_api_key("category")

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

    max_attempts = 4
    timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout

    for attempt in range(max_attempts):
        start_time = time.time()
        print(f"Starting attempt {attempt + 1}/{max_attempts} for category '{category}'")

        try:
            session = await get_session()

            # Log when we start making the API call
            print(f"Making API request to GNews for category '{category}'...")

            async with session.get(news_settings.top_headlines_endpoint,
                                   params=params,
                                   timeout=timeout) as response:

                # Log the response status
                status = response.status
                print(f"Received response with status {status} for '{category}'")

                # Handle rate limiting with exponential backoff
                if status == 429:  # Too Many Requests
                    if attempt < max_attempts:  # Not the last attempt
                        wait_time = min(2 ** attempt * 2, 10)  # Max 10 seconds wait
                        print(f"⏳ Rate limited for category '{category}'. Waiting {wait_time} seconds before retry {attempt + 1}/{max_attempts}")
                        sleep_start = time.time()
                        await asyncio.sleep(wait_time)
                        sleep_end = time.time()
                        print(f"Sleep completed after {sleep_end - sleep_start:.2f} seconds for '{category}'")
                        continue
                    else:
                        print(f"⚠️ Max retries reached for '{category}' due to rate limiting")
                        raise ValueError(f"Failed to fetch results for '{category}' after {max_attempts} attempts due to rate limiting")

                # For other status codes
                response.raise_for_status()

                # Process the successful response
                print(f"Parsing JSON response for '{category}'...")
                data = await response.json()
                print(f"JSON parsed successfully for '{category}'")

                found_articles = data.get("articles", [])
                if found_articles:
                    result = found_articles[:news_settings.max_articles]
                    print(f"✅ Successfully fetched {len(result)} article(s) for {category}")
                    return result
                else:
                    print(f"🔍 No articles found for category: {category}")
                    return []  # Return empty list instead of raising an exception

        except asyncio.TimeoutError:
            print(f"⏱️ Request timeout for category '{category}' on attempt {attempt + 1}/{max_attempts}")
            if attempt == max_attempts - 1:  # Last attempt
                raise ValueError(f"Request timed out for '{category}' after {max_attempts} attempts")
            # Add a short delay before retrying
            print("Waiting 2 seconds before retrying after timeout...")
            await asyncio.sleep(2)
            print(f"Timeout wait completed for '{category}'")

        except aiohttp.ClientResponseError as e:
            # This handles cases where raise_for_status() throws an exception
            if e.status == 429 and attempt < max_attempts - 1:  # Rate limited and not last attempt
                wait_time = min(2 ** attempt * 2, 10)
                print(f"⏳ Rate limited for {category} (ClientResponseError). Waiting {wait_time} seconds before retry {attempt + 1}/{max_attempts}")
                sleep_start = time.time()
                await asyncio.sleep(wait_time)
                sleep_end = time.time()
                print(f"Sleep completed after {sleep_end - sleep_start:.2f} seconds for {category}")
            else:
                # For other status codes or last attempt, propagate the error
                print(f"Network error for {category}: {e.status}, message='{e.message}', url='{e.request_info.url}'")
                raise

        except aiohttp.ClientError as e:
            if attempt == max_attempts - 1:  # Last attempt
                print(f"Network error while fetching {category}: {str(e)}")
                raise
            wait_time = min(2 ** attempt * 2, 10)
            print(f"⚠️ Network error on attempt {attempt + 1}/{max_attempts} for {category}. Waiting {wait_time} seconds before retry...")
            sleep_start = time.time()
            await asyncio.sleep(wait_time)
            sleep_end = time.time()
            print(f"Sleep completed after {sleep_end - sleep_start:.2f} seconds for {category}")

        except Exception as e:
            print(f"Unexpected error while fetching {category}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

        print(f"Completed attempt {attempt + 1}/{max_attempts} for '{category}' in {time.time() - start_time:.2f} seconds")

    # If we get here, all retries failed
    raise aiohttp.ClientError(f"Failed to fetch news for {category} after {max_attempts} attempts")


async def get_keyword_news(query: str) -> List[Dict[str, Any]]:
    """
    Asynchronously fetch news article from GNews API using a search query.
    Implements exponential backoff for rate limiting (HTTP 429).

    Args:
        query (str): The keyword to search for

    Returns:
        List[Dict[str, Any]]: The matching articles if found or empty list if none found

    Raises:
        aiohttp.ClientError: If there's a network error after all retries
    """
    # Validate API key before making any requests
    _require_api_key("keyword")

    from_time = get_zulu_time_minus(news_settings.minutes_ago)

    params = {
        "q": query,
        "from": from_time,
        "lang": news_settings.language,
        "country": news_settings.country,
        "max": 1,  # Only fetch the first article
        "apikey": news_settings.api_key,
        "sortby": news_settings.sort_by,
    }

    max_attempts = 4
    timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout

    for attempt in range(max_attempts):
        start_time = time.time()
        print(f"Starting attempt {attempt + 1}/{max_attempts} for query '{query}'")

        try:
            session = await get_session()

            # Log when we start making the API call
            print(f"Making API request to GNews for query '{query}'...")

            async with session.get(news_settings.search_endpoint,
                                   params=params,
                                   timeout=timeout) as response:

                # Log the response status
                status = response.status
                print(f"Received response with status {status} for '{query}'")

                # Handle rate limiting with exponential backoff
                if status == 429:
                    if attempt < max_attempts - 1:  # Not the last attempt
                        wait_time = min(2 ** attempt * 2, 10)  # Max 10 seconds wait
                        print(f"⏳ Rate limited for query '{query}'. Waiting {wait_time} seconds before retry {attempt + 1}/{max_attempts}")
                        sleep_start = time.time()
                        await asyncio.sleep(wait_time)
                        sleep_end = time.time()
                        print(f"Sleep completed after {sleep_end - sleep_start:.2f} seconds for '{query}'")
                        continue
                    else:
                        print(f"⚠️ Max retries reached for '{query}' due to rate limiting")
                        return []  # Return empty list instead of raising exception

                # For other status codes
                response.raise_for_status()

                # Process the successful response
                print(f"Parsing JSON response for '{query}'...")
                data = await response.json()
                print(f"JSON parsed successfully for '{query}'")

                found_articles = data.get("articles", [])
                if found_articles:
                    print(f"✅ Successfully fetched article for {query}")
                    return found_articles
                else:
                    print(f"🔍 No articles found for query: {query}")
                    return []  # Return empty list instead of raising an exception

        except asyncio.TimeoutError:
            print(f"⏱️ Request timeout for query '{query}' on attempt {attempt + 1}/{max_attempts}")
            if attempt == max_attempts - 1:  # Last attempt
                print(f"⚠️ Final timeout for query '{query}' after {max_attempts} attempts")
                return []  # Return empty list instead of raising exception
            # Add a short delay before retrying
            print("Waiting 2 seconds before retrying after timeout...")
            await asyncio.sleep(2)
            print(f"Timeout wait completed for '{query}'")

        except aiohttp.ClientResponseError as e:
            # This handles cases where raise_for_status() throws an exception
            if e.status == 429 and attempt < max_attempts - 1:  # Rate limited and not last attempt
                wait_time = min(2 ** attempt * 2, 10)
                print(f"⏳ Rate limited for query '{query}' (ClientResponseError). Waiting {wait_time} seconds before retry {attempt + 1}/{max_attempts}")
                sleep_start = time.time()
                await asyncio.sleep(wait_time)
                sleep_end = time.time()
                print(f"Sleep completed after {sleep_end - sleep_start:.2f} seconds for '{query}'")
            else:
                # For other status codes or last attempt, log and return empty list
                print(f"⚠️ Network error for query '{query}': {e.status}, message='{e.message}', url='{e.request_info.url}'")
                return []  # Return empty list instead of raising exception

        except aiohttp.ClientError as e:
            if attempt == max_attempts - 1:  # Last attempt
                print(f"⚠️ Network error while fetching news for query '{query}': {str(e)}")
                return []  # Return empty list instead of raising exception
            wait_time = min(2 ** attempt * 2, 10)
            print(f"⚠️ Network error on attempt {attempt + 1}/{max_attempts} for query '{query}'. Waiting {wait_time} seconds before retry...")
            sleep_start = time.time()
            await asyncio.sleep(wait_time)
            sleep_end = time.time()
            print(f"Sleep completed after {sleep_end - sleep_start:.2f} seconds for '{query}'")

        except Exception as e:
            print(f"⚠️ Unexpected error while fetching news for query '{query}': {str(e)}")
            import traceback
            traceback.print_exc()
            return []  # Return empty list instead of raising exception

        print(f"Completed attempt {attempt + 1}/{max_attempts} for '{query}' in {time.time() - start_time:.2f} seconds")

    # If we get here, all retries failed
    print(f"⚠️ Failed to fetch news for query '{query}' after {max_attempts} attempts")
    return []  # Return empty list instead of raising exception
