import requests

from .commons import get_zulu_time_minus
from settings import NewsSettings


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

    Args:
        query (str): The keyword to search for

    Returns:
        dict: The first matching article if found

    Raises:
        ValueError: If no articles are found
        requests.exceptions.RequestException: If there's a network error
    """
    # Normalize the hashtag and use as search query
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

    try:
        response = requests.get(NewsSettings.SEARCH_ENDPOINT, params=params)
        response.raise_for_status()
        found_articles = response.json().get("articles", [])
        if found_articles:
            article = found_articles[0]
            article['hashtag'] = query  # Add the original hashtag to the article for reference
            print(f"✅ Successfully fetched article for {query}")
            return article
        else:
            raise ValueError(f"🔍 No articles found for query: {query}")
    except ValueError as ve:
        print(str(ve))
        raise
    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching news for {query}: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error while fetching news for {query}: {str(e)}")
        raise
