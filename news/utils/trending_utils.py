import requests
import re
from bs4 import BeautifulSoup
from settings import TrendingSettings


def get_trending_hashtags(limit=TrendingSettings.DEFAULT_LIMIT):
    """
    Fetch trending hashtags from trends24.in for India
    Args:
        limit: Maximum number of hashtags to return (default: 50)
    Returns:
        list: List of trending hashtags that match the pattern (letters, digits, underscore, spaces, # only)
    """
    headers = {"User-Agent": TrendingSettings.USER_AGENT}

    try:
        res = requests.get(TrendingSettings.TRENDS_URL, headers=headers)
        res.raise_for_status()  # Raise exception for bad status codes
        soup = BeautifulSoup(res.text, "html.parser")

        trends = soup.select("ol.trend-card__list li span.trend-name a.trend-link")
        hashtags = []

        pattern = re.compile(r'^[\w\s#]+$')  # letters, digits, underscore, spaces, # only

        for tag in trends[:limit]:
            text = tag.text.strip()
            if text.startswith("#") and pattern.match(text):
                hashtags.append(text)

        return hashtags[:TrendingSettings.MAX_HASHTAGS]

    except requests.RequestException as e:
        print(f"Error fetching trending hashtags: {e}")
        return []
