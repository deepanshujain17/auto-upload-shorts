import requests
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from .commons import get_zulu_time_minus
from settings import NewsSettings

def get_news(category=None):
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
        "apikey": NewsSettings.API_KEY
    }

    try:
        response = requests.get(NewsSettings.TOP_HEADLINES_ENDPOINT, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        if articles:
            result = articles[0]
            print(f"Successfully fetched article for {category}")
            return result
        else:
            raise ValueError(f"No articles found for category: {category}")
    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching {category}: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error while fetching {category}: {str(e)}")
        raise
