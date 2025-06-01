from core.news.news_api_client import get_category_news, get_keyword_news


def fetch_news_article(identifier: str, is_keyword: bool = False) -> list[dict]:
    """
    Fetch news article for the given category or keyword.
    Args:
        identifier (str): Either a news category or a keyword to search for
        is_keyword (bool): If True, treats identifier as a keyword for search. If False, treats it as a category.

    Returns:
        dict: The news article data used for tag generation
    Raises:
        Exception: If any step in the process fails
    """
    try:
        # Fetch the news
        print("📰 Fetching news...")
        if is_keyword:
            articles = get_keyword_news(identifier)
            print(f"Trending Keyword Article | {identifier}:\n{articles}")
            if not articles:
                raise ValueError(f"No article found for keyword: {identifier}")
        else:
            articles = get_category_news(identifier)  # identifier is category in this case
            print(f"Trending Category Article | {identifier}:\n{articles}")
            if not articles:
                raise ValueError(f"No article found for category: {identifier}")

        return articles
    except Exception as e:
        error_msg = f"Error fetching news article for {identifier}: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)

