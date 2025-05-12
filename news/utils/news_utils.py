import requests
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from .commons import get_zulu_time_minus

from settings import (
    GNEWS_API_KEY,
    DEFAULT_CATEGORY,
    NEWS_LANGUAGE,
    NEWS_COUNTRY,
    MAX_ARTICLES,
    NEWS_MINUTES_AGO,
    NEWS_IN,
    NEWS_QUERY,
    GNEWS_TOP_HEADLINES_ENDPOINT,
    GNEWS_SEARCH_ENDPOINT
)

def get_news(categories=None):
    """
    Fetch news articles from GNews API for given categories
    """
    if categories is None:
        categories = [DEFAULT_CATEGORY]

    results = {}
    for category in categories:
        print(f"Fetching news for category: {category}")
        from_time = get_zulu_time_minus(NEWS_MINUTES_AGO)  # Fetch articles from the last X minutes

        params = {
            # "q": NEWS_QUERY,
            # "in": NEWS_IN,
            "from": from_time,
            "category": category,
            "lang": NEWS_LANGUAGE,
            "country": NEWS_COUNTRY,
            "max": MAX_ARTICLES,
            "apikey": GNEWS_API_KEY
        }

        try:
            response = requests.get(GNEWS_TOP_HEADLINES_ENDPOINT, params=params)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            if articles:
                results[category] = articles[0]
                print(f"Successfully fetched article for {category}")
            else:
                print(f"No articles found for {category}")
                results[category] = {"title": "No article found", "description": ""}
        except requests.exceptions.RequestException as e:
            print(f"Network error while fetching {category}: {str(e)}")
            results[category] = {"title": f"Error fetching {category}", "description": str(e)}
        except Exception as e:
            print(f"Unexpected error while fetching {category}: {str(e)}")
            results[category] = {"title": f"Error fetching {category}", "description": str(e)}

    return results


