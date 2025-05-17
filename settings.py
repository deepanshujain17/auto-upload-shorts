import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NewsSettings:
    # GNews API Configuration
    API_KEY = os.getenv("GNEWS_API_KEY")

    # News API Settings
    CATEGORIES = ["general", "sports", "world", "nation", "business", "technology", "entertainment", "science", "health"]
    CATEGORY_BGM = {
        "sports": "bgm_tararara",
        "entertainment": "bgm_chubina",
        "nation": "bgm_cheerful"
    }
    DEFAULT_CATEGORY = "nation"
    DEFAULT_CATEGORY_BGM = "bgm_cheerful"
    LANGUAGE = "en"
    COUNTRY = "in"
    MINUTES_AGO = 600 # Change this to get the latest news
    IN_FIELD = "title"
    QUERY = "India"
    MAX_ARTICLES = 1
    SORT_BY = "publishedAt" # Another option: "relevance"

    # API Endpoints
    SEARCH_ENDPOINT = "https://gnews.io/api/v4/search"
    TOP_HEADLINES_ENDPOINT = "https://gnews.io/api/v4/top-headlines"

class HTMLSettings:
    CARD_WIDTH = 720
    TITLE_FONT_SIZE = 28
    DESCRIPTION_FONT_SIZE = 18
    META_FONT_SIZE = 12
    TITLE_MARGIN_TOP = 15
    BORDER_RADIUS = 8
    FONT_FAMILY = "Arial, sans-serif" # For Hindi use: "Noto Sans Devanagari, Mangal, sans-serif";

class VideoSettings:
    IMAGE_HEIGHT = 800
    IMAGE_VERTICAL_OFFSET = 300
    VIDEO_CODEC = "libx264"
    AUDIO_CODEC = "aac"
    WINDOW_WIDTH = 740
    WINDOW_HEIGHT = 820
    BROWSER_WAIT_TIME = 2  # seconds

class YouTubeSettings:
    DEFAULT_CATEGORY = "22"  # People & Blogs
    DEFAULT_PRIVACY = "public"
    DEFAULT_TAGS = ["shorts", "news", "TrendingNow"]
    ARTICLE_MAX_TAGS = 3
    MAX_TAGS = 12  # Maximum number of tags allowed by YouTube


class PathSettings:
    # Directory paths
    OUTPUT_DIR = "output"
    ASSETS_VIDEO_DIR = "assets/videos"
    NEWS_TEMP_DIR = "news/temp"
    NEWS_CARDS_DIR = "news/news_cards"

    # File paths
    @staticmethod
    def get_html_output(category: str) -> str:
        return f"{PathSettings.NEWS_TEMP_DIR}/temp_{category}.html"

    @staticmethod
    def get_overlay_image(category: str) -> str:
        return f"{PathSettings.NEWS_CARDS_DIR}/card_{category}.png"

    @staticmethod
    def get_video_path(bgm_video: str) -> str:
        return f"{PathSettings.ASSETS_VIDEO_DIR}/{bgm_video}.mp4"

    @staticmethod
    def get_final_video(category: str) -> str:
        return f"{PathSettings.OUTPUT_DIR}/short_with_overlay_{category}.mp4"

class TrendingSettings:
    TRENDS_URL = "https://trends24.in/india"
    USER_AGENT = "Mozilla/5.0"
    DEFAULT_LIMIT = 50
    MAX_HASHTAGS = 10  # Maximum number of hashtags to return
