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
    MINUTES_AGO = 240 # Change this to get the latest news
    IN_FIELD = "title"
    QUERY = "India"
    MAX_ARTICLES = 1

    # API Endpoints
    SEARCH_ENDPOINT = "https://gnews.io/api/v4/search"
    TOP_HEADLINES_ENDPOINT = "https://gnews.io/api/v4/top-headlines"

class HTMLSettings:
    CARD_WIDTH = 800
    TITLE_FONT_SIZE = 28
    DESCRIPTION_FONT_SIZE = 18
    META_FONT_SIZE = 12
    TITLE_MARGIN_TOP = 15
    BORDER_RADIUS = 8
    FONT_FAMILY = "Arial, sans-serif" # For Hindi use: "Noto Sans Devanagari, Mangal, sans-serif";

class VideoSettings:
    IMAGE_HEIGHT = 720
    IMAGE_VERTICAL_OFFSET = 300
    VIDEO_CODEC = "libx264"
    AUDIO_CODEC = "aac"
    WINDOW_WIDTH = 790
    WINDOW_HEIGHT = 800
    BROWSER_WAIT_TIME = 2  # seconds

class YouTubeSettings:
    DEFAULT_CATEGORY = "22"  # People & Blogs
    DEFAULT_PRIVACY = "public"
    DEFAULT_TAGS = ["shorts", "news", "TrendingNow"]


