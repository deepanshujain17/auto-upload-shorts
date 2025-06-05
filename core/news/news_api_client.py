import time
import requests

from settings import news_settings
from utils.commons import get_zulu_time_minus
from core.news.hashtag_storage import HashtagStorage


def get_category_news(category=None) -> list[dict]:
    """
    Fetch news articles from GNews API for given categories

    Raises:
        ValueError: If no articles are found for the given category
        requests.exceptions.RequestException: If there's a network error
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
        response = requests.get(news_settings.top_headlines_endpoint, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        if articles:
            result = articles[:news_settings.max_articles]
            print(f"✅ Successfully fetched article for {category}")
            return result
        else:
            raise ValueError(f"🔍 No articles found for category: {category}")
    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching {category}: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error while fetching {category}: {str(e)}")
        raise


def get_keyword_news(query: str) -> list[dict]:
    """
    Fetch news article from GNews API using a search query.
    Implements exponential backoff for rate limiting (HTTP 429).
    Checks if the query was already processed today to avoid duplicates.

    Args:
        query (str): The keyword to search for

    Returns:
        dict: The first matching article if found

    Raises:
        ValueError: If no articles are found or query was already processed today
        requests.exceptions.RequestException: If there's a network error after all retries
    """
    # Check if this hashtag was already processed today
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
            response = requests.get(news_settings.search_endpoint, params=params)

            # Handle rate limiting with exponential backoff
            if response.status_code == 429:
                wait_time = 2 ** attempt  # 1, 2, 4 seconds
                print(f"⏳ Rate limited. Waiting {wait_time} seconds before retry {attempt + 1}/{max_attempts}")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            found_articles = response.json().get("articles", [])
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
        except requests.exceptions.RequestException as e:
            if attempt == max_attempts - 1:  # Last attempt
                print(f"Network error while fetching news for {query}: {str(e)}")
                raise
            wait_time = 2 ** attempt
            print(f"⚠️ Network error on attempt {attempt + 1}/{max_attempts}. Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
            continue
        except Exception as e:
            print(f"Unexpected error while fetching news for {query}: {str(e)}")
            raise

    # If we get here, all retries failed
    raise requests.exceptions.RequestException(f"Failed to fetch news after {max_attempts} attempts")
