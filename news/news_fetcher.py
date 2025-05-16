from news.utils.news_utils import get_news
from news.utils.html_utils import create_html_card
from news.utils.browser_utils import render_card_to_image
from settings import PathSettings


def generate_news_card(category: str) -> tuple[dict, str]:
    """
    Generate a news card image for the given category.
    Args:
        category (str): News category to process

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
        article = get_news(category)

        # 2. Generate news card HTML for the category
        html_output = PathSettings.get_html_output(category)
        print(f"🖥️ Generating HTML card for {category}...")
        create_html_card(article, html_output)

        # 3. Render the HTML to an image
        overlay_image = PathSettings.get_overlay_image(category)
        print(f"🖼️ Rendering HTML to image for {category}...")
        render_card_to_image(html_output, overlay_image)

        return article, overlay_image
    except Exception as e:
        print(f"❌ Error generating news card for {category}: {str(e)}")
        raise

