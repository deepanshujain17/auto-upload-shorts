from news.utils.news_api_client import get_trending_news, get_keyword_news


def generate_news_card(identifier: str, is_keyword: bool = False) -> dict:
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
            article = get_keyword_news(identifier)
            print(f"Trending Keyword Article | {identifier}:\n{article}")
            if not article:
                raise ValueError(f"No article found for keyword: {identifier}")
        else:
            article = get_trending_news(identifier)  # identifier is category in this case
            print(f"Trending Category Article | {identifier}:\n{article}")

        return article
    except Exception as e:
        raise

