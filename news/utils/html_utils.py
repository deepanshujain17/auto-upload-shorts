import datetime
from datetime import datetime, timezone, timedelta
import os
from settings import HTMLSettings

# --- GENERATE HTML ---
def create_html_card(article, output_path="temp.html"):
    """
    Creates an HTML card from the given article data.

    Args:
        article (dict): Article data containing title, description, etc.
        output_path (str): Path where the HTML file will be saved

    Raises:
        ValueError: If article data is invalid
        IOError: If there's an error writing the file
    """
    try:
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
                # Parse as UTC-aware datetime
                dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

                # Convert to IST (UTC+5:30)
                ist = timezone(timedelta(hours=5, minutes=30))
                ist_time = dt.astimezone(ist)

                # Format as readable IST time
                published = ist_time.strftime("%Y-%m-%d %H:%M")
            except ValueError as e:
                print(f"Error parsing date: {str(e)}")

        html_template = """
        <html>
            <head>
                <style>
                    body {{
                        font-family: {font_family};
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
            font_family=HTMLSettings.FONT_FAMILY,
            title=title,
            description=description,
            image_html=image_html,
            published=published
        )

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write the HTML file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        except IOError as e:
            print(f"Error writing HTML file: {str(e)}")
            raise

    except KeyError as e:
        print(f"Missing required article data: {str(e)}")
        raise ValueError(f"Invalid article data: {str(e)}")
    except Exception as e:
        print(f"Unexpected error creating HTML card: {str(e)}")
        raise
