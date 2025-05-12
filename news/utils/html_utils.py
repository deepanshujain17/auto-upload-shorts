import datetime
from datetime import datetime, timezone, timedelta

from settings import HTMLSettings

# --- GENERATE HTML ---
def create_html_card(article, output_path="temp.html"):
    # Pre-calculate all article-related variables
    title = article.get("title", "No Title")
    description = article.get("description", "No Description")
    image_url = article.get("image", "")
    published_at = article.get("publishedAt")
    source = article.get('source', {}).get('name', 'Unknown')

    # Source of the article
    print(f"🌐 News Source: {source}")

    # Process image HTML
    image_html = f"<img src='{image_url}' alt='News image'>" if image_url else ""

    # Process publish date to IST
    published = "Unknown"
    if published_at:
        try:
            dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
            ist_time = dt.astimezone(timezone(timedelta(hours=5, minutes=30)))
            published = ist_time.strftime("%Y-%m-%d %H%M")
        except ValueError:
            pass

    html_template = """
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    width: {width}px;
                    border: 1px solid #ccc;
                    padding: 10px;
                    margin: 0 auto;
                    background-color: #f9f9f9;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: {border_radius}px;
                }}
                h2 {{
                    font-size: {title_size}px;
                    margin-top: {title_margin}px;
                }}
                p {{
                    font-size: {desc_size}px;
                }}
                .meta {{
                    font-size: {meta_size}px;
                    color: gray;
                }}
            </style>
        </head>
        <body>
            {image_html}
            <h2>{title}</h2>
            <p>{description}</p>
            <div class="meta">
                <p><b>Published:</b> {published}</p>
            </div>
        </body>
    </html>
    """

    html_content = html_template.format(
        width=HTMLSettings.CARD_WIDTH,
        border_radius=HTMLSettings.BORDER_RADIUS,
        title_size=HTMLSettings.TITLE_FONT_SIZE,
        title_margin=HTMLSettings.TITLE_MARGIN_TOP,
        desc_size=HTMLSettings.DESCRIPTION_FONT_SIZE,
        meta_size=HTMLSettings.META_FONT_SIZE,
        title=title,
        description=description,
        image_html=image_html,
        published=published
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

