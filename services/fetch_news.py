from core.news.news_api_client import get_category_news, get_keyword_news


async def fetch_news_article(identifier: str, is_keyword: bool = False) -> list[dict]:
    """
    Asynchronously fetch news article for the given category or keyword.
    Args:
        identifier (str): Either a news category or a keyword to search for
        is_keyword (bool): If True, treats identifier as a keyword for search. If False, treats it as a category.

    Returns:
        dict: The news article data used for tag generation
    Raises:
        Exception: If any step in the process fails
    """
    try:
        print("📰 Fetching news...")
        if is_keyword:
            articles = await get_keyword_news(identifier)
            print(f"Trending Keyword Article | {identifier}:\n{articles}")
            if not articles:
                print(f"🔍 No articles found for query: {identifier}")
                return []  # Return empty list instead of raising an exception
        else:
            articles = await get_category_news(identifier) # identifier is category in this case
            print(f"Trending Category Article | {identifier}:\n{articles}")
            if not articles:
                print(f"🔍 No articles found for category: {identifier}")
                return []  # Return empty list instead of raising an exception

        return articles
    except Exception as e:
        print(f"Error fetching news for identifier '{identifier}' (is_keyword={is_keyword}): {str(e)}")
        # Still raise other exceptions that aren't related to no articles found
        raise
