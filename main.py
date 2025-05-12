import os

from utils.video_processor import create_overlay_video
from utils.auth import authenticate_youtube
from utils.upload import upload_video
from news.utils.news_utils import get_news
from news.utils.html_utils import create_html_card
from news.utils.browser_utils import render_card_to_image
from settings import NewsSettings, YouTubeSettings

# --- MAIN ---
if __name__ == "__main__":
    # 📝 Set your input and metadata here
    os.makedirs("output", exist_ok=True)

    # First fetch the news to generate the news card
    print("📰 Fetching news and generating news card...")
    categories = [NewsSettings.DEFAULT_CATEGORY]
    articles_by_category = get_news(categories)
    print(articles_by_category)

    # Generate news card for the nation category
    category = categories[0]
    html_output = f"news/temp/temp_{category}.html"
    create_html_card(articles_by_category[category], html_output)
    overlay_image = f"news/news_cards/card_{category}.png"
    render_card_to_image(html_output, overlay_image)

    input_video = "assets/videos/video1.mp4"
    final_video = "output/short_with_overlay.mp4"

    title = "My Short with Overlay"
    description = "Auto-uploaded via Python!"
    tags = ["shorts", "python"]
    privacy = YouTubeSettings.DEFAULT_PRIVACY
    category = YouTubeSettings.DEFAULT_CATEGORY

    print("🎬 Creating overlay video...")
    output = create_overlay_video(input_video, overlay_image, final_video)

    print("🔐 Authenticating to YouTube...")
    yt = authenticate_youtube()

    print("🚀 Uploading to YouTube Shorts...")
    upload_video(yt, output, title, description, tags, category, privacy)
