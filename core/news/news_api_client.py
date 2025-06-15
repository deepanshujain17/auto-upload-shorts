import asyncio
import aiohttp
from typing import List, Dict, Any
import time

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
    Implements exponential backoff for rate limiting (HTTP 429).

    Raises:
        ValueError: If no articles are found for the given category
        aiohttp.ClientError: If there's a network error after all retries
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

    max_attempts = 3
    # Define a strict timeout to prevent hanging requests
    timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout

    for attempt in range(max_attempts):
        start_time = time.time()
        print(f"Starting attempt {attempt + 1}/{max_attempts} for category '{category}'")

        try:
            session = await get_session()

            # Log when we start making the API call
            print(f"Making API request to GNews for category '{category}'...")

            # Use timeout to prevent hanging requests
            async with session.get(news_settings.top_headlines_endpoint,
                                  params=params,
                                  timeout=timeout) as response:

                # Log the response status
                status = response.status
                print(f"Received response with status {status} for '{category}'")

                # Handle rate limiting with exponential backoff
                if status == 429:  # Too Many Requests
                    if attempt < max_attempts - 1:  # Not the last attempt
                        wait_time = min(2 ** attempt * 2, 10)  # Max 10 seconds wait
                        print(f"⏳ Rate limited for {category}. Waiting {wait_time} seconds before retry {attempt + 1}/{max_attempts}")
                        # Use a timer to verify the sleep is working
                        sleep_start = time.time()
                        await asyncio.sleep(wait_time)
                        sleep_end = time.time()
                        print(f"Sleep completed after {sleep_end - sleep_start:.2f} seconds for {category}")
                        # Skip to the next iteration
                        continue
                    else:
                        # This is the last attempt, so we give up
                        print(f"⚠️ Max retries reached for {category} due to rate limiting")
                        raise ValueError(f"Failed to fetch {category} after {max_attempts} attempts due to rate limiting")

                # For other status codes, raise an exception
                response.raise_for_status()

                # Process the successful response
                print(f"Parsing JSON response for '{category}'...")
                data = await response.json()
                print(f"JSON parsed successfully for '{category}'")

                articles = data.get("articles", [])
                if articles:
                    result = articles[:news_settings.max_articles]
                    print(f"✅ Successfully fetched article for {category}")
                    return result
                else:
                    raise ValueError(f"🔍 No articles found for category: {category}")

        except asyncio.TimeoutError:
            # Handle request timeout
            print(f"⏱️ Request timeout for {category} on attempt {attempt + 1}/{max_attempts}")
            if attempt == max_attempts - 1:  # Last attempt
                raise ValueError(f"Request timed out for {category} after {max_attempts} attempts")
            # Add a delay before retrying
            print(f"Waiting 2 seconds before retrying after timeout...")
            await asyncio.sleep(2)
            print(f"Timeout wait completed for {category}")

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
                        raise ValueError(f"Failed to fetch results for '{query}' after {max_attempts} attempts due to rate limiting")

                # For other status codes
                response.raise_for_status()

                # Process the successful response
                print(f"Parsing JSON response for '{query}'...")
                data = await response.json()
                print(f"JSON parsed successfully for '{query}'")

                found_articles = data.get("articles", [])
                if found_articles:
                    result = found_articles[:2]
                    # Save the successful query to history with country code
                    HashtagStorage.save_hashtag(f"{query}_{news_settings.country}")
                    print(f"✅ Successfully fetched article for {query}")
                    return result
                else:
                    raise ValueError(f"🔍 No articles found for query: {query}")

        except asyncio.TimeoutError:
            print(f"⏱️ Request timeout for query '{query}' on attempt {attempt + 1}/{max_attempts}")
            if attempt == max_attempts - 1:  # Last attempt
                raise ValueError(f"Request timed out for '{query}' after {max_attempts} attempts")
            # Add a short delay before retrying
            print(f"Waiting 2 seconds before retrying after timeout...")
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
                # For other status codes or last attempt, propagate the error
                print(f"Network error for query '{query}': {e.status}, message='{e.message}', url='{e.request_info.url}'")
                raise

        except aiohttp.ClientError as e:
            if attempt == max_attempts - 1:  # Last attempt
                print(f"Network error while fetching news for query '{query}': {str(e)}")
                raise
            wait_time = min(2 ** attempt * 2, 10)
            print(f"⚠️ Network error on attempt {attempt + 1}/{max_attempts} for query '{query}'. Waiting {wait_time} seconds before retry...")
            sleep_start = time.time()
            await asyncio.sleep(wait_time)
            sleep_end = time.time()
            print(f"Sleep completed after {sleep_end - sleep_start:.2f} seconds for '{query}'")

        except Exception as e:
            print(f"Unexpected error while fetching news for query '{query}': {str(e)}")
            import traceback
            traceback.print_exc()
            raise

        print(f"Completed attempt {attempt + 1}/{max_attempts} for '{query}' in {time.time() - start_time:.2f} seconds")

    # If we get here, all retries failed
    raise aiohttp.ClientError(f"Failed to fetch news for query '{query}' after {max_attempts} attempts")