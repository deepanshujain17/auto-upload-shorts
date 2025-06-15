import re
import aiohttp
from bs4 import BeautifulSoup

from settings import TrendingSettings


async def get_trending_hashtags(limit=TrendingSettings.DEFAULT_LIMIT):
    """
    Asynchronously fetch trending hashtags from trends24.in based on country settings
    Args:
        limit: Maximum number of hashtags to return (default: 50)
    Returns:
        list: List of unique trending hashtags that match the pattern (letters, digits, underscore, spaces, # only)
    """
    headers = {"User-Agent": TrendingSettings.USER_AGENT}
    trends_url = TrendingSettings.get_trends_url()
    print(f"Fetching trending hashtags from: {trends_url}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(trends_url, headers=headers) as response:
                response.raise_for_status()  # Raise exception for bad status codes
                html_content = await response.text()

        soup = BeautifulSoup(html_content, "html.parser")
        trends = soup.select("ol.trend-card__list li span.trend-name a.trend-link")
        unique_hashtags = set()

        pattern = re.compile(r'^[\w\s#]+$')  # letters, digits, underscore, spaces, # only

        for tag in trends[:limit]:
            tag_text = tag.get_text().strip()
            if pattern.match(tag_text):  # Only add if matches pattern
                unique_hashtags.add(tag_text)

        hashtag_list = list(unique_hashtags)
        print(f"Found {len(hashtag_list)} valid trending hashtags")
        return hashtag_list

    except aiohttp.ClientError as e:
        print(f"Error fetching trending hashtags: {str(e)}")
        return []
    except Exception as e:
        print(f"Unexpected error while fetching trending hashtags: {str(e)}")
        return []
