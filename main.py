import os

from utils.video_processor import create_overlay_video
from utils.auth import authenticate_youtube
from utils.upload import upload_video
from news.utils.news_utils import get_news
from news.utils.html_utils import create_html_card
from news.utils.browser_utils import render_card_to_image

# --- MAIN ---
if __name__ == "__main__":
    # 📝 Set your input and metadata here
    os.makedirs("output", exist_ok=True)

    # First fetch the news to generate the news card
    print("📰 Fetching news and generating news card...")
    categories = ["nation"]
    # articles_by_category = get_news(categories)
    articles_by_category = {'nation': {'title': 'सीजफायर के लिए अमेरिका ने दी थी व्यापार ना करने की धमकी? ट्रंप के कथित दावों पर क्या बोला भारत', 'description': 'ट्रंप ने सोमवार को दावा किया था कि अमेरिका ने भारत और पाकिस्तान के बीच सुलह कराने के लिए व्यापार ना करने की धमकी दी थी। ट्रंप ने कहा कि अमेरिका ने परमाणु युद्ध रुकवा दी है।, India News in Hindi - Hindustan', 'content': 'ट्रंप ने सोमवार को दावा किया था कि अमेरिका ने भारत और पाकिस्तान के बीच सुलह कराने के लिए व्यापार ना करने की धमकी दी थी। ट्रंप ने कहा कि अमेरिका ने परमाणु युद्ध रुकवा दी है।\nभारत ने सोमवार को अमेरिकी राष्ट्रपति डोनाल्ड ट्रंप का बड़ा दावा खारिज कर दिया... [2271 chars]', 'url': 'https://www.livehindustan.com/national/india-rebuts-trump-claims-says-no-reference-to-trade-in-india-pakistan-ceasfire-talks-201747069156918.html', 'image': 'https://www.livehindustan.com/lh-img/smart/img/2025/05/12/1600x900/ANI-20250214092-0_1740021107713_1747069768082.jpg', 'publishedAt': '2025-05-12T17:10:24Z', 'source': {'name': 'Hindustan', 'url': 'https://www.livehindustan.com'}}}
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
    category = "22"  # People & Blogs
    privacy = "private"

    print("🎬 Creating overlay video...")
    output = create_overlay_video(input_video, overlay_image, final_video)

    print("🔐 Authenticating to YouTube...")
    yt = authenticate_youtube()

    print("🚀 Uploading to YouTube Shorts...")
    upload_video(yt, output, title, description, tags, category, privacy)
