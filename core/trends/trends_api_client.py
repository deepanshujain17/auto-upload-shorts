import re

import requests
from bs4 import BeautifulSoup

from settings import TrendingSettings


def get_trending_hashtags(limit=TrendingSettings.DEFAULT_LIMIT):
    """
    Fetch trending hashtags from trends24.in based on country settings
    Args:
        limit: Maximum number of hashtags to return (default: 50)
    Returns:
        list: List of unique trending hashtags that match the pattern (letters, digits, underscore, spaces, # only)
    """
    headers = {"User-Agent": TrendingSettings.USER_AGENT}
    trends_url = TrendingSettings.get_trends_url()

    try:
        res = requests.get(trends_url, headers=headers)
        res.raise_for_status()  # Raise exception for bad status codes
        soup = BeautifulSoup(res.text, "html.parser")

        trends = soup.select("ol.trend-card__list li span.trend-name a.trend-link")
        unique_hashtags = set()

        pattern = re.compile(r'^[\w\s#]+$')  # letters, digits, underscore, spaces, # only

        for tag in trends[:limit]:
            text = tag.text.strip()
            if text.startswith("#") and pattern.match(text):
                unique_hashtags.add(text)

        # Convert set back to list and apply max limit
        return list(unique_hashtags)[:TrendingSettings.MAX_HASHTAGS]

    except requests.RequestException as e:
        print(f"Error fetching trending hashtags: {e}")
        return []
