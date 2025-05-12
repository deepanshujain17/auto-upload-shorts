import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GNews API Configuration
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

# News API Settings
DEFAULT_CATEGORY = "nation"
NEWS_LANGUAGE = "hi"
NEWS_COUNTRY = "in"
NEWS_MINUTES_AGO = 240
# Extra params
NEWS_IN = "title"
NEWS_QUERY = "India"

MAX_ARTICLES = 1

# API Endpoints
GNEWS_SEARCH_ENDPOINT = "https://gnews.io/api/v4/search"
GNEWS_TOP_HEADLINES_ENDPOINT = "https://gnews.io/api/v4/top-headlines"
