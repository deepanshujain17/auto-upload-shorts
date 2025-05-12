import requests
import sys
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from .commons import get_zulu_time_minus
from settings import NewsSettings

def get_news(categories=None):
    """
    Fetch news articles from GNews API for given categories
    """
    if categories is None:
        categories = [NewsSettings.DEFAULT_CATEGORY]

    results = {}
    for category in categories:
        print(f"Fetching news for category: {category}")
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

