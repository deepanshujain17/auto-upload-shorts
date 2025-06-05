from pydantic import BaseModel, Field
from .config import get_env_var

class NewsSettings(BaseModel):
    api_key: str = Field(default=get_env_var("GNEWS_API_KEY"))
    categories: list[str] = ["general", "sports", "world", "nation", "business",
                            "technology", "entertainment", "science", "health"]
    category_bgm: dict = {"default": "bgm_find"}
    category_bg_image: dict = {"default": "bg_image"}
    language: str = "en"
    _country: str = "in"
    minutes_ago: int = 1440
    in_field: str = "title,description"
    max_articles: int = 3
    sort_by: str = "publishedAt"
    search_endpoint: str = "https://gnews.io/api/v4/search"
    top_headlines_endpoint: str = "https://gnews.io/api/v4/top-headlines"

    @property
    def country(self) -> str:
        return self._country

    @country.setter
    def country(self, value: str) -> None:
        if not isinstance(value, str) or len(value) != 2:
            raise ValueError("Country must be a 2-letter code")
        self._country = value.lower()

# Create a global instance
news_settings = NewsSettings()
