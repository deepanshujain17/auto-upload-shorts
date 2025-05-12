import os
import dotenv

from utils.html_utils import create_html_card
from utils.news_utils import get_news
from utils.browser_utils import render_card_to_image

# --- CONFIG ---
dotenv.load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

if __name__ == "__main__":
    print("📡 Fetching news articles...")
    # categories = [
    #     "world", "nation", "business", "technology",
    #     "entertainment", "sports", "science", "health"
    # ]

    categories = ["nation", "sports"]
    articles_by_category = get_news(categories)

    for category, article in articles_by_category.items():
        print(f"\n🧾 Generating news card for category: {category}")

        html_output = f"temp/temp_{category}.html"
        image_output = f"news_cards/card_{category}.png"

        create_html_card(article, output_path=html_output)
        render_card_to_image(html_output, image_output)

        print(f"✅ News card for '{category}' saved as {image_output}")

