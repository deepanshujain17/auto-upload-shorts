"""
Utility module for generating news card images using Pillow.
"""

# Standard library imports
import os
from io import BytesIO
from datetime import datetime, timezone, timedelta
import textwrap
import requests

# Third-party imports
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from settings import HTMLSettings


def download_image(url):
    """Download an image from URL and return as a PIL Image object."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return None


def get_font_height(font, text):
    """Get the height of text with a given font."""
    try:
        bbox = font.getbbox(text)
        return bbox[3] - bbox[1]
    except Exception:
        return 20  # Default height if there's an error


def generate_news_card(article, output_path):
    """Generate a news card image with Pillow."""
    try:
        # Get article data
        title = article.get("title", "No Title")
        description = article.get("description", "No Description")
        image_url = article.get("image", "")
        published_at = article.get("publishedAt")
        source = article.get('source', {}).get('name', 'Unknown')

        # Process publish date to IST
        published = "Unknown"
        if published_at:
            try:
                dt = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                ist = timezone(timedelta(hours=5, minutes=30))
                published = dt.astimezone(ist).strftime("%Y-%m-%d %H:%M")
            except ValueError:
                pass

        # Setup card dimensions and styling
        card_width = HTMLSettings.CARD_WIDTH
        card_height = HTMLSettings.CARD_HEIGHT  # Initial height, will be adjusted
        content_padding = 30

        # Create initial canvas
        card = Image.new('RGB', (card_width, card_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(card)


        # Try to load fonts with sizes from settings
        try:
            # Extract first font from font family string (e.g., "Arial, sans-serif" -> "Arial")
            font_name = HTMLSettings.FONT_FAMILY.split(',')[0].strip()

            # Find standard and bold variants by common naming patterns
            bold_font_candidates = [
                font_name + "-Bold",  # Arial-Bold
                font_name + " Bold",  # Arial Bold
                font_name + "Bold",   # ArialBold
                font_name,            # Fallback to regular
            ]

            # Try to load regular font
            title_font = ImageFont.truetype(font_name, HTMLSettings.TITLE_FONT_SIZE)
            desc_font = ImageFont.truetype(font_name, HTMLSettings.DESCRIPTION_FONT_SIZE)
            meta_font = ImageFont.truetype(font_name, HTMLSettings.META_FONT_SIZE)

            # Try to find bold variant for titles and bold text
            title_bold_font = meta_bold_font = None
            for bold_candidate in bold_font_candidates:
                try:
                    title_bold_font = ImageFont.truetype(bold_candidate, HTMLSettings.TITLE_FONT_SIZE)
                    meta_bold_font = ImageFont.truetype(bold_candidate, HTMLSettings.META_FONT_SIZE)
                    break  # Found a bold font
                except:
                    continue

            # If couldn't find bold variant, fall back to regular
            if not title_bold_font:
                title_bold_font = title_font
            if not meta_bold_font:
                meta_bold_font = meta_font

        except:
            # Continue with default fonts if loading fails
            title_font = title_bold_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
            meta_font = meta_bold_font = ImageFont.load_default()

        current_y = 0

        # Add image if available
        if image_url:
            news_image = download_image(image_url)
            if news_image:
                aspect_ratio = news_image.width / news_image.height
                new_height = int(card_width / aspect_ratio)
                news_image = news_image.resize((card_width, new_height))
                card.paste(news_image, (0, current_y))
                current_y += new_height

        # Add title with spacing
        current_y += HTMLSettings.TITLE_MARGIN_TOP
        title_wrap_width = int((card_width - 2 * content_padding) / (HTMLSettings.TITLE_FONT_SIZE * 0.5))
        title_lines = textwrap.wrap(title, width=title_wrap_width)
        for line in title_lines:
            # Use bold font for title text
            draw.text((content_padding, current_y), line, font=title_bold_font, fill=(0, 0, 0))
            current_y += get_font_height(title_bold_font, line)
        current_y += 30  # Space after title

        # Add description with spacing
        desc_wrap_width = int((card_width - 8 * content_padding) / (HTMLSettings.DESCRIPTION_FONT_SIZE * 0.4))
        desc_lines = textwrap.wrap(description, width=desc_wrap_width)
        line_spacing = int(HTMLSettings.DESCRIPTION_FONT_SIZE * 0.3)
        for line in desc_lines:
            draw.text((content_padding, current_y), line, font=desc_font, fill=(0, 0, 0))
            current_y += int(get_font_height(desc_font, line) + line_spacing)
        current_y -= line_spacing  # Remove extra spacing from last line
        current_y += 40  # Space after description

        # Add metadata (source and published date)
        source_text, published_text = "Source: ", "Published: "
        source_width = meta_bold_font.getlength(source_text)
        source_pos = content_padding + source_width

        # Draw source
        draw.text((content_padding, current_y), source_text, font=meta_bold_font, fill=(128, 128, 128))
        draw.text((source_pos, current_y), source, font=meta_font, fill=(128, 128, 128))

        # Draw separator and published date
        separator = "           |         "
        sep_pos = source_pos + meta_font.getlength(source)
        draw.text((sep_pos, current_y), separator, font=meta_font, fill=(128, 128, 128))

        published_pos = sep_pos + meta_font.getlength(separator)
        draw.text((published_pos, current_y), published_text, font=meta_bold_font, fill=(128, 128, 128))

        pub_value_pos = published_pos + meta_bold_font.getlength(published_text)
        draw.text((pub_value_pos, current_y), published, font=meta_font, fill=(128, 128, 128))

        # Calculate final height
        current_y += get_font_height(meta_font, "Source:") + content_padding * 2
        final_height = current_y

        # Create the final card with exact dimensions needed
        final_card = Image.new('RGB', (card_width, final_height), color=(255, 255, 255))
        final_card.paste(card.crop((0, 0, card_width, final_height)), (0, 0))

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Add shadow and rounded corners
        shadow_blur = 12
        shadow_offset_y = 4
        radius = HTMLSettings.BORDER_RADIUS

        # Create final output with shadow and rounded corners
        try:
            # Create shadow image
            shadow = Image.new('RGBA', (card_width, final_height), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_draw.rounded_rectangle(
                [(0, 0), (card_width, final_height)],
                radius=radius, fill=(0, 0, 0, 25)
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))

            # Create card with rounded corners
            card_with_content = final_card.convert('RGBA')
            mask = Image.new('L', (card_width, final_height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                [(0, 0), (card_width-1, final_height-1)], # Change these for shadow effect outer layer
                radius=radius, fill=255
            )
            card_with_content.putalpha(mask)

            # Combine shadow and card
            output = Image.new('RGB', (card_width, final_height), (255, 255, 255))
            output.paste(shadow, (0, shadow_offset_y), shadow)
            output.paste(card_with_content, (0, 0), card_with_content)

        except (AttributeError, ImportError):
            # Fallback for older Pillow versions
            output = final_card

        # Save the image
        output.save(output_path, format="PNG")

    except Exception as e:
        print(f"Error generating card image: {str(e)}")
        import traceback
        traceback.print_exc()
