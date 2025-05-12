import requests
import os
from dotenv import load_dotenv

from .commons import get_zulu_time_minus

# Load environment variables
load_dotenv()

# API Configuration
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")  # Ensure to set this in your .env file

def get_news(categories=None):
    """
    Fetch news articles from GNews API for given categories
    """
    if categories is None:
        categories = ["nation"]  # Default category

    search_endpoint_base_url = "https://gnews.io/api/v4/search" # Base URL for keyword search endpoint
    top_headlines_base_url = "https://gnews.io/api/v4/top-headlines"
    results = {}

    for category in categories:
        print(f"Fetching news for category: {category}")
        from_time = get_zulu_time_minus(240)  # Fetch articles from the last X minutes

        params = {
            # "q": "India",
            # "in": "title",
            # "from": from_time,
            "category": category,
            "lang": "en",
            "country": "in",
            "max": 1,
            "apikey": GNEWS_API_KEY,
        }
        try:
            response = requests.get(top_headlines_base_url, params=params)
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
