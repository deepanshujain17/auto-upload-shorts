import requests
import time
import os
from datetime import datetime
from pathlib import Path
from .commons import get_zulu_time_minus
from settings import NewsSettings

def _get_hashtag_file_path():
    """Returns the path to trending hashtags file"""
    output_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "output/history"
    return output_dir / "trending_hashtags.txt"

def _read_hashtag_history():
    """Read the hashtag history file and return a set of (hashtag, date) tuples"""
    file_path = _get_hashtag_file_path()
    history = set()
    if file_path.exists():
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    history.add((parts[0], parts[1]))
    return history

def _save_hashtag(hashtag):
    """Save a hashtag with current date to the history file"""
    file_path = _get_hashtag_file_path()
    current_date = datetime.now().strftime('%Y-%m-%d')
    with open(file_path, 'a') as f:
        f.write(f"{hashtag},{current_date}\n")

def get_trending_news(category=None):
    """
    Fetch news articles from GNews API for given categories

    Raises:
        ValueError: If no articles are found for the given category
        requests.exceptions.RequestException: If there's a network error
    """
    if category is None:
        category = NewsSettings.DEFAULT_CATEGORY

    print(f"📰 Fetching news for category: {category}")
    from_time = get_zulu_time_minus(NewsSettings.MINUTES_AGO)  # Fetch articles from the last X minutes

    params = {
        # "q": NewsSettings.QUERY,
        # "in": NewsSettings.IN_FIELD,
        "from": from_time,
        "category": category,
        "lang": NewsSettings.LANGUAGE,
        "country": NewsSettings.COUNTRY,
        "max": NewsSettings.MAX_ARTICLES,
        "apikey": NewsSettings.API_KEY,
        "sortby": NewsSettings.SORT_BY,
    }

    try:
        response = requests.get(NewsSettings.TOP_HEADLINES_ENDPOINT, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        if articles:
            result = articles[0]
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

def get_keyword_news(query: str) -> dict:
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
    current_date = datetime.now().strftime('%Y-%m-%d')
    history = _read_hashtag_history()
    if (query, current_date) in history:
        raise ValueError(f"🔄 Query '{query}' was already processed today")

    from_time = get_zulu_time_minus(NewsSettings.MINUTES_AGO)

    params = {
        "q": query,
        "from": from_time,
        "lang": NewsSettings.LANGUAGE,
        "country": NewsSettings.COUNTRY,
        "max": NewsSettings.MAX_ARTICLES,
        "apikey": NewsSettings.API_KEY,
        "sortby": NewsSettings.SORT_BY,
    }

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = requests.get(NewsSettings.SEARCH_ENDPOINT, params=params)

            # Handle rate limiting with exponential backoff
            if response.status_code == 429:
                wait_time = 2 ** attempt  # 1, 2, 4 seconds
                print(f"⏳ Rate limited. Waiting {wait_time} seconds before retry {attempt + 1}/{max_attempts}")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            found_articles = response.json().get("articles", [])
            if found_articles:
                article = found_articles[0]
                article['hashtag'] = query  # Add the original hashtag to the article for reference
                # Save the successful query to history
                _save_hashtag(query)
                print(f"✅ Successfully fetched article for {query}")
                return article
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
