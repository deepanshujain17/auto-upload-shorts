from settings import HTMLSettings

# --- GENERATE HTML ---
def create_html_card(article, output_path="temp.html"):
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

    image_html = f"<img src='{article.get('image', '')}' alt='News image'>" if article.get("image") else ""

    # Source of the article
    print(f"News Source: {article.get('source', {}).get('name', 'Unknown')}")

    # Split content into lines and combine first two lines if available
    content = article.get("content", "").split(". ")
    content_lines = [line.strip() + "." for line in content[:1] if line.strip()]
    combined_content = " ".join(content_lines) if content_lines else ""

    html_content = html_template.format(
        width=HTMLSettings.CARD_WIDTH,
        border_radius=HTMLSettings.BORDER_RADIUS,
        title_size=HTMLSettings.TITLE_FONT_SIZE,
        title_margin=HTMLSettings.TITLE_MARGIN_TOP,
        desc_size=HTMLSettings.DESCRIPTION_FONT_SIZE,
        meta_size=HTMLSettings.META_FONT_SIZE,
        title=article.get("title", "No Title"),
        description=article.get("description", "No Description"),
        image_html=image_html,
        # content=combined_content,
        published=article.get("publishedAt", "Unknown")
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


