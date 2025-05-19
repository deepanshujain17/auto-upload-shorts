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
    MINUTES_AGO = 1440 # 24-hours Change this to get the latest news #IMP
    IN_FIELD = "title,description" # Not being used as of now
    MAX_ARTICLES = 1 # TODO: In Future, get more articles to generate more videos with the same GNEWS Hits limit
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
    DEFAULT_PRIVACY = "private"  # Options: "public", "private", "unlisted"
    ARTICLE_MAX_TAGS = 3
    MAX_TAGS = 9  # Maximum number of tags allowed by YouTube #IMP #TODO: Review

    # Default HashTags (for trending keywords)
    DEFAULT_HASHTAGS = ["TrendingNow", "CurrentAffairs", "TopStories"]
    EXTRA_DESCRIPTION_HASHTAGS = ["ViralNews", "shorts"]
    # Mapping of content categories to Relevant HashTags
    CATEGORY_HASHTAG_MAP = {
        "general": [
            "BreakingNews", "TrendingNow", "CurrentAffairs"
        ],
        "sports": [
            "SportsNews", "GameDay", "AthleteLife"
        ],
        "world": [
            "WorldNews", "GlobalUpdates", "CurrentAffairs"
        ],
        "nation": [
            "IndiaNews", "HeadlinesToday", "CivicBuzz"
        ],
        "business": [
            "MarketWatch", "BizNews", "EconomyToday"
        ],
        "technology": [
            "TechNews", "Innovation", "DigitalTrends"
        ],
        "entertainment": [
            "CelebBuzz", "TVandFilm", "PopCulture"
        ],
        "science": [
            "SciTalk", "SpaceAndBeyond", "Discovery"
        ],
        "health": [
            "HealthTips", "Wellness", "FitLife"
        ]
    }


    # Default YouTube category ID for videos
    DEFAULT_YOUTUBE_CATEGORY = 22        # People & Blogs
    # Mapping of content categories to YouTube category IDs
    CATEGORY_TO_YOUTUBE_CATEGORY_MAP = {
        "general": 22,           # People & Blogs
        "sports": 17,            # Sports
        "world": 25,             # News & Politics
        "nation": 25,            # News & Politics
        "business": 26,          # Howto & Style (finance-oriented content)
        "technology": 28,        # Science & Technology
        "entertainment": 24,     # Entertainment
        "science": 28,           # Science & Technology
        "health": 26             # Howto & Style (for wellness/fitness)
    }

    # YouTube Playlist Settings
    DEFAULT_PLAYLIST_ID = "PLxkrFcfC1HKTjWUEuNsGkx7596lkYHmnM"     # #NowTrending 🔥 – What Everyone’s Talking About
    # Mapping of content categories to the respective YouTube playlist IDs
    CATEGORY_PLAYLIST_MAP = {
        "general": "PLxkrFcfC1HKQtEf4Ief6JdVjej1vA9xbG",           # NewsFlash 🔥 Top Stories & Trends
        "sports": "PLxkrFcfC1HKTo4hVW1uxhesL9T6j99NSP",            # Game On! ⚽ Sports Highlights & Updates
        "world": "PLxkrFcfC1HKQ8WPQJUHA6B69C0ag8h5T1",             # Global Pulse 🌍 What’s Happening Around the World
        "nation": "PLxkrFcfC1HKQ9EAijefBRgiEtlwQOaNYU",            # India Now 🇮🇳 Headlines That Matter
        "business": "PLxkrFcfC1HKSnjFyVE2Je1KlrrjzPtUDJ",          # Market Moves 📈 Business & Economy Shorts
        "technology": "PLxkrFcfC1HKTkvOIQKV0yByHn3uRdmE3g",        # Tech Shorts 🚀 Gadgets, AI & Future Bytes
        "entertainment": "PLxkrFcfC1HKQRZA4hBZbW9T0AY-7TprxX",     # PopBeat 🎬 Movies, Celebs & Culture
        "science": "PLxkrFcfC1HKRwOXokC0nh2gmnE4Vgwls5",           # Mind Blown 🔬 Fascinating Science & Discoveries
        "health": "PLxkrFcfC1HKREoe7AA5sSsvhuae5-K2se",            # Health Shot 💪 Wellness, Fitness & Medical News
    }

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
    DEFAULT_LIMIT = 100
    MAX_HASHTAGS = 10  # Maximum number of hashtags to return #IMP

