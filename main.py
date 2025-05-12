import os

from utils.video_processor import create_overlay_video
from utils.auth import authenticate_youtube
from utils.upload import upload_video
from news.utils.news_utils import get_news
from news.utils.html_utils import create_html_card
from news.utils.browser_utils import render_card_to_image
from settings import YouTubeSettings

# --- MAIN ---
if __name__ == "__main__":
    # 📝 Set your input and metadata here
    os.makedirs("output", exist_ok=True)

    # Define categories to process
    categories = ["nation", "sports", "entertainment"]

    # Authenticate to YouTube once before the loop
    print("🔐 Authenticating to YouTube...")
    yt = authenticate_youtube()

    # Process each category
    for category in categories:
        print(f"\n📌 Processing category: {category}")

        # First fetch the news to generate the news cards
        print("📰 Fetching news and generating news cards...")
        article = get_news(category)
        # print(article)

        # Generate news card for the category
        html_output = f"news/temp/temp_{category}.html"
        print(f"🖥️ Generating HTML card for {category}...")
        create_html_card(article, html_output)

        # Render the HTML to an image
        overlay_image = f"news/news_cards/card_{category}.png"
        print(f"🖼️ Rendering HTML to image for {category}...")
        render_card_to_image(html_output, overlay_image)

        input_video = "assets/videos/video1.mp4"
        final_video = f"output/short_with_overlay_{category}.mp4"

        # TODO: Update title, description and tags to be more relevant, catchy and exciting eg. news of the hour or so
        title = f"Latest {category.title()} News Update"
        description = f"Auto-generated {category} news update #shorts"
        tags = ["shorts", "news", category, "update", "trending"]
        privacy = YouTubeSettings.DEFAULT_PRIVACY
        youtube_category = YouTubeSettings.DEFAULT_CATEGORY

        print(f"🎬 Creating overlay video for {category}...")
        output = create_overlay_video(input_video, overlay_image, final_video)

        print(f"🚀 Uploading {category} video to YouTube Shorts...")
        upload_video(yt, output, title, description, tags, youtube_category, privacy)
