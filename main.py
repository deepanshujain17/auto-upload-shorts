import os

from utils.video_processor import create_overlay_video
from utils.auth import authenticate_youtube
from utils.upload import upload_video
from news.utils.news_utils import get_news
from news.utils.html_utils import create_html_card
from news.utils.browser_utils import render_card_to_image
from news.utils.tag_utils import generate_tags_with_frequency
from settings import YouTubeSettings, NewsSettings, PathSettings


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

def create_overlay_video_output(category, overlay_image):
    """
    Create an overlay video with the news card.
    Args:
        category (str): News category to process
        overlay_image (str): Path to the overlay image

    Returns:
        str: Path to the final video
    Raises:
        Exception: If video creation fails
    """
    try:
        bgm_video = NewsSettings.CATEGORY_BGM.get(category, NewsSettings.DEFAULT_CATEGORY_BGM)
        input_video = PathSettings.get_video_path(bgm_video)
        final_video = PathSettings.get_final_video(category)

        print(f"🎬 Creating overlay video for {category}...")
        output = create_overlay_video(input_video, overlay_image, final_video)
        return output
    except Exception as e:
        print(f"❌ Error creating overlay video for {category}: {str(e)}")
        raise

def upload_youtube_shorts(yt, category, overlay_video_output, article):
    """
    Upload the generated video to YouTube Shorts.
    Args:
        yt: YouTube API client
        category (str): News category to process
        overlay_video_output: Path to the final video
        article: The news article data used for tag generation
    Raises:
        Exception: If upload fails
    """
    try:
        # Generate dynamic tags from article content
        article_tags = [tag for tag, _ in generate_tags_with_frequency(article)]

        # Combine with default tags, ensure uniqueness, and limit total tags
        combined_tags = list(dict.fromkeys([category] + article_tags + YouTubeSettings.DEFAULT_TAGS))[:10]  # YouTube allows max 10 tags

        article_title = ' '.join(article.get("title", "No Title").split()[:8])
        title = f"Breaking News: {article_title}"

        article_description = article.get("description", "No Description")
        article_tags_str = " ".join([f"#{tag}" for tag in article_tags])
        description = f"{article_description} {article_tags_str} #{category} #news #update #trends #shorts"

        youtube_category = YouTubeSettings.DEFAULT_CATEGORY
        privacy = YouTubeSettings.DEFAULT_PRIVACY

        print(f"🚀 Uploading {category} video to YouTube Shorts...")
        upload_video(yt, overlay_video_output, title, description, combined_tags, youtube_category, privacy)
    except Exception as e:
        print(f"❌ Error uploading video for {category}: {str(e)}")
        raise

# --- MAIN ---
if __name__ == "__main__":
    # 📝 Set your input and metadata here
    os.makedirs(PathSettings.OUTPUT_DIR, exist_ok=True)

    try:
        # Authenticate to YouTube once before the loop
        print("🔐 Authenticating to YouTube...")
        yt = authenticate_youtube()

        # Process each category
        for category in NewsSettings.CATEGORIES:
            try:
                print(f"\n📌 Processing category: {category}")

                # 1. Generate the news card image and get article data
                article, overlay_image = generate_news_card(category)

                # 2. Create the overlay video
                overlay_video_output = create_overlay_video_output(category, overlay_image)

                # 3. Upload the video to YouTube Shorts
                upload_youtube_shorts(yt, category, overlay_video_output, article)

                print(f"✅ Successfully processed {category}")
            except Exception as e:
                print(f"⚠️ Failed to process category {category}. Moving to next category...")
                continue
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")

