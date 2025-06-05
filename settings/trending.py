from .paths import PathSettings
from .news import news_settings

class TrendingSettings:
    TRENDS_URLS = {
        "in": "https://trends24.in/india",
        "us": "https://trends24.in/united-states"
    }
    USER_AGENT = "Mozilla/5.0"
    DEFAULT_LIMIT = 100
    MAX_HASHTAGS = 5  # Maximum number of hashtags to return

    @staticmethod
    def get_trends_url():
        country = news_settings.country.lower()
        return TrendingSettings.TRENDS_URLS.get(country, TrendingSettings.TRENDS_URLS["in"])

    @staticmethod
    def get_manual_hashtag_queries():
        country = news_settings.country.lower()
        manual_hashtags_path = f"{PathSettings.CONFIG_DIR}/manual_hashtags_{country}.txt"
        try:
            with open(manual_hashtags_path, 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"Warning: Manual hashtags file not found at {manual_hashtags_path}")
            return []
