from .paths import PathSettings

class TrendingSettings:
    TRENDS_URL = "https://trends24.in/india"
    USER_AGENT = "Mozilla/5.0"
    DEFAULT_LIMIT = 100
    MAX_HASHTAGS = 5  # Maximum number of hashtags to return

    @staticmethod
    def get_manual_hashtag_queries():
        manual_hashtags_path = f"{PathSettings.CONFIG_DIR}/manual_hashtags.txt"
        try:
            with open(manual_hashtags_path, 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"Warning: Manual hashtags file not found at {manual_hashtags_path}")
            return []
