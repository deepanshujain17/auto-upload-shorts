from news.utils.news_utils import get_trending_news, get_keyword_news
from news.utils.html_utils import create_html_card
from news.utils.browser_utils import render_card_to_image
from settings import PathSettings


def generate_news_card(identifier: str, is_keyword: bool = False) -> tuple[dict, str]:
    """
    Generate a news card image for the given category or keyword.
    Args:
        identifier (str): Either a news category or a keyword to search for
        is_keyword (bool): If True, treats identifier as a keyword for search. If False, treats it as a category.

    Returns:
        tuple[dict, str]: A tuple containing:
            - article: The news article data used for tag generation
            - str: Path to the generated overlay image
    Raises:
        Exception: If any step in the process fails
    """
    try:
        # 1. First fetch the news to generate the news cards
        print("📰 Fetching news and generating news cards...")
        if is_keyword:
            article = get_keyword_news(identifier)
            print(f"{identifier} article:\n{article}")
            if not article:
                raise ValueError(f"No article found for keyword: {identifier}")
        else:
            article = get_trending_news(identifier)  # identifier is category in this case

        # 2. Generate news card HTML
        html_output = PathSettings.get_html_output(identifier)
        print(f"🖥️ Generating HTML card for {identifier}...")
        create_html_card(article, html_output)

        # 3. Render the HTML to an image
        overlay_image = PathSettings.get_overlay_image(identifier)
        print(f"🖼️ Rendering HTML to image for {identifier}...")
        render_card_to_image(html_output, overlay_image)

        return article, overlay_image
    except Exception as e:
        print(f"❌ Error generating news card for {identifier}: {str(e)}")
        raise

