"""
Utility module for generating news card images using Pillow instead of browser rendering.
"""

# Standard library imports
import os
import sys
from io import BytesIO
from datetime import datetime, timezone, timedelta
import textwrap
import requests

# Third-party imports
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from settings import HTMLSettings, VideoSettings


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
    """Get the height of text with a given font using the new Pillow API."""
    try:
        bbox = font.getbbox(text)
        return bbox[3] - bbox[1]
    except Exception as e:
        print(f"Error getting font height: {e}")
        return 20  # Default height if there's an error


def get_system_font():
    """
    Get the system font that best matches the HTMLSettings.FONT_FAMILY (Arial, sans-serif).
    This function prioritizes exact matches for Arial on various platforms.
    """
    # Parse the font family from settings - targeting "Arial, sans-serif"
    font_family = HTMLSettings.FONT_FAMILY.lower()

    # Specifically look for Arial since that's the primary font in the HTML card
    if 'arial' in font_family:
        # macOS Arial locations
        if sys.platform == 'darwin':
            arial_candidates = [
                '/Library/Fonts/Arial.ttf',
                '/System/Library/Fonts/Supplemental/Arial.ttf',
                '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
            ]

            for font_path in arial_candidates:
                if os.path.exists(font_path):
                    print(f"Using Arial font: {font_path}")
                    return font_path

            # If Arial is not found on macOS, try Helvetica as it's visually similar
            helvetica_candidates = [
                '/System/Library/Fonts/Helvetica.ttc',
                '/System/Library/Fonts/Helvetica.dfont',
            ]

            for font_path in helvetica_candidates:
                if os.path.exists(font_path):
                    print(f"Using Helvetica as Arial substitute: {font_path}")
                    return font_path

        # Linux Arial locations
        elif sys.platform.startswith('linux'):
            linux_arial_candidates = [
                '/usr/share/fonts/truetype/msttcorefonts/Arial.ttf',
                '/usr/share/fonts/TTF/arial.ttf',
            ]

            for font_path in linux_arial_candidates:
                if os.path.exists(font_path):
                    print(f"Using Arial font: {font_path}")
                    return font_path

        # Windows Arial locations
        elif sys.platform == 'win32':
            win_arial_candidates = [
                'C:\\Windows\\Fonts\\arial.ttf',
                'C:\\Windows\\Fonts\\Arial.ttf',
            ]

            for font_path in win_arial_candidates:
                if os.path.exists(font_path):
                    print(f"Using Arial font: {font_path}")
                    return font_path

    # If 'arial' is not found or not in font_family, check for generic sans-serif
    if 'sans-serif' in font_family or 'sans' in font_family:
        # Common sans-serif fonts across platforms
        sans_serif_candidates = [
            # macOS
            '/System/Library/Fonts/Helvetica.ttc',
            '/System/Library/Fonts/SF-Pro-Display-Regular.otf',
            '/System/Library/Fonts/SF-Pro-Text-Regular.otf',
            # Linux
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            # Generic
            'DejaVuSans.ttf',
            'FreeSans.ttf',
        ]

        for font_path in sans_serif_candidates:
            if os.path.exists(font_path):
                print(f"Using sans-serif font: {font_path}")
                return font_path

    # Last resort: use any available system font
    print("Arial or sans-serif not found, checking for any available system font...")
    fallback_paths = [
        # macOS
        '/System/Library/Fonts/',
        '/Library/Fonts/',
        # Linux
        '/usr/share/fonts/truetype/',
        # Windows
        'C:\\Windows\\Fonts\\',
    ]

    for directory in fallback_paths:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if file.lower().endswith(('.ttf', '.ttc', '.otf')):
                    font_path = os.path.join(directory, file)
                    print(f"Using fallback font: {font_path}")
                    return font_path

    print("No suitable font found, will use default")
    return None


def generate_news_card(article, output_path):
    """
    Generates a news card image directly using Pillow that matches the styling
    of the original HTML-rendered card.

    Args:
        article (dict): Article data containing title, description, etc.
        output_path (str): Path where the image file will be saved

    Returns:
        None
    """
    try:
        # Get article data
        title = article.get("title", "No Title")
        description = article.get("description", "No Description")
        image_url = article.get("image", "")
        published_at = article.get("publishedAt")
        source = article.get('source', {}).get('name', 'Unknown')

        # Process publish date to IST - same as in HTML card
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

        # Get dimensions from settings
        card_width = HTMLSettings.CARD_WIDTH
        card_height = HTMLSettings.CARD_HEIGHT  # Starting height, will be adjusted based on content

        # Define padding for content - used for margins inside the card
        content_padding = 30  # Standard padding for card content (matches CSS padding from HTML card)

        # Create the canvas with the fixed dimensions
        card = Image.new('RGB', (card_width, card_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(card)

        # Load fonts with appropriate sizes from HTMLSettings
        system_font = get_system_font()
        system_font_bold = system_font  # Default to regular font if bold not found

        # Try to find the bold version of the font for title (h2) and metadata keywords
        if system_font and sys.platform == 'darwin':  # macOS
            if 'Arial.ttf' in system_font:
                # Try to find Arial Bold
                bold_path = system_font.replace('Arial.ttf', 'Arial Bold.ttf')
                if os.path.exists(bold_path):
                    system_font_bold = bold_path
            elif 'Helvetica.ttc' in system_font:
                # Helvetica bold is typically in the same .ttc file
                system_font_bold = system_font

        try:
            if system_font:
                # Use exact font sizes from the HTML styling
                # For title, use bold font to match h2 tag appearance
                if system_font_bold and os.path.exists(system_font_bold):
                    title_font = ImageFont.truetype(system_font_bold, HTMLSettings.TITLE_FONT_SIZE)  # 28px, bold like h2
                else:
                    title_font = ImageFont.truetype(system_font, HTMLSettings.TITLE_FONT_SIZE)  # 28px

                desc_font = ImageFont.truetype(system_font, HTMLSettings.DESCRIPTION_FONT_SIZE)  # 18px
                meta_font = ImageFont.truetype(system_font, HTMLSettings.META_FONT_SIZE)  # 12px

                # Bold font for the "Source" and "Published" keywords
                if system_font_bold and os.path.exists(system_font_bold):
                    meta_bold_font = ImageFont.truetype(system_font_bold, HTMLSettings.META_FONT_SIZE)
                else:
                    meta_bold_font = meta_font  # Fallback if bold font not available
            else:
                # Use default font as fallback
                title_font = ImageFont.load_default()
                desc_font = ImageFont.load_default()
                meta_font = ImageFont.load_default()
                meta_bold_font = meta_font
        except Exception as e:
            print(f"Font loading error: {str(e)}. Using default font.")
            title_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
            meta_font = ImageFont.load_default()
            meta_bold_font = meta_font

        current_y = 0

        # Add image if available - same as in HTML card
        if image_url:
            news_image = download_image(image_url)
            if news_image:
                # Resize image to fit card width
                aspect_ratio = news_image.width / news_image.height
                new_height = int(card_width / aspect_ratio)
                news_image = news_image.resize((card_width, new_height))

                # Paste image at the top
                card.paste(news_image, (0, current_y))
                current_y += new_height

        # Start the content section - with properly styled title
        # Apply margin-top: 30px after image (increased from 15px for better spacing)
        current_y += HTMLSettings.TITLE_MARGIN_TOP * 2  # 30px margin top

        # Draw title - with proper text wrapping and styling
        # Use wider text wrapping to better utilize the full card width
        title_wrap_width = int((card_width - 2 * content_padding) / (HTMLSettings.TITLE_FONT_SIZE * 0.5))  # Dynamic calculation based on font size
        title_lines = textwrap.wrap(title, width=title_wrap_width)
        for line in title_lines:
            draw.text((content_padding, current_y), line, font=title_font, fill=(0, 0, 0))
            current_y += get_font_height(title_font, line)

        # Add margin-bottom: 20px after title (increased from 8px for better spacing)
        current_y += 20  # Increased margin-bottom of title

        # Draw description - with proper text wrapping and styling to match HTML paragraph
        # Use wider text wrapping to better utilize the full card width
        desc_wrap_width = int((card_width - 2 * content_padding) / (HTMLSettings.DESCRIPTION_FONT_SIZE * 0.4))  # Dynamic calculation based on font size
        desc_lines = textwrap.wrap(description, width=desc_wrap_width)

        # Use regular font (non-bold) for description, matching HTML paragraph styling
        # Also ensure line height is appropriate for paragraph text (slightly more than font height)
        line_spacing = int(HTMLSettings.DESCRIPTION_FONT_SIZE * 0.3)  # Convert to integer
        for line in desc_lines:
            draw.text((content_padding, current_y), line, font=desc_font, fill=(0, 0, 0))
            current_y += int(get_font_height(desc_font, line) + line_spacing)  # Ensure integer

        # Adjust the extra line spacing from the last line
        current_y -= line_spacing

        # Add margin after description (20px increased from 8px)
        current_y += 20

        # Draw metadata with "Source" and "Published" in bold
        source_text = "Source: "
        published_text = "Published: "

        # Calculate text widths for proper positioning
        source_width = meta_bold_font.getlength(source_text)
        source_value_pos = content_padding + source_width

        # Draw "Source" in bold
        draw.text((content_padding, current_y), source_text, font=meta_bold_font, fill=(128, 128, 128))

        # Draw the source value in normal font
        draw.text((source_value_pos, current_y), source, font=meta_font, fill=(128, 128, 128))

        # Calculate position for the separator and "Published" text
        separator_text = " | "
        source_value_width = meta_font.getlength(source)
        separator_pos = source_value_pos + source_value_width

        # Draw separator
        draw.text((separator_pos, current_y), separator_text, font=meta_font, fill=(128, 128, 128))

        # Calculate position for "Published" text
        published_pos = separator_pos + meta_font.getlength(separator_text)

        # Draw "Published" in bold
        draw.text((published_pos, current_y), published_text, font=meta_bold_font, fill=(128, 128, 128))

        # Draw the published date in normal font
        published_value_pos = published_pos + meta_bold_font.getlength(published_text)
        draw.text((published_value_pos, current_y), published, font=meta_font, fill=(128, 128, 128))

        # Move position down after metadata
        current_y += get_font_height(meta_font, "Source:") + content_padding

        # Add padding at bottom - matches the padding in HTML card
        current_y += content_padding

        # Resize canvas to actual content height
        final_card_height = current_y

        # Make sure final_card_height is always a valid integer
        if final_card_height is None or not isinstance(final_card_height, int):
            # Fallback to a minimum height if we somehow got None
            final_card_height = 600

        # Create the final card with the exact content height
        final_card = Image.new('RGB', (card_width, final_card_height), color=(255, 255, 255))
        final_card.paste(card.crop((0, 0, card_width, final_card_height)), (0, 0))

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Add shadow effect that matches the HTML card's box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1)
        shadow_blur = 12  # Match the 12px blur from HTML
        shadow_offset_y = 4  # Match the 4px y-offset from HTML
        shadow_offset_x = 0  # Match the 0px x-offset from HTML

        # Add padding around image for the shadow to be fully visible
        # But keep the actual card width at exactly 1480px
        padding = shadow_blur * 2
        shadow_width = card_width  # Keep the shadow same width as card
        shadow_height = final_card_height

        # The final image will contain the card plus space for the shadow
        padded_width = card_width + padding * 2
        padded_height = final_card_height + padding * 2

        # Create a transparent background for the entire image
        final_bg = Image.new('RGB', (card_width, final_card_height), (255, 255, 255))

        # Create a solid color image for the shadow (with rounded corners if possible)
        try:
            # Create a shadow with rounded corners
            shadow_img = Image.new('RGBA', (shadow_width, shadow_height), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_img)

            # Draw the shadow with rounded corners
            radius = HTMLSettings.BORDER_RADIUS
            shadow_draw.rounded_rectangle(
                [(0, 0), (shadow_width, shadow_height)],
                radius=radius,
                fill=(0, 0, 0, 25)  # Light shadow (25/255 opacity)
            )

            # Apply blur to shadow
            shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(shadow_blur))

            # Create the final card with rounded corners
            card_rounded = Image.new('RGBA', (card_width, final_card_height), (0, 0, 0, 0))
            card_draw = ImageDraw.Draw(card_rounded)

            # Draw white rounded rectangle as the card background
            card_draw.rounded_rectangle(
                [(0, 0), (card_width-1, final_card_height-1)],
                radius=radius,
                fill=(255, 255, 255, 255)
            )

            # Apply the card content using the rounded card as a mask
            card_with_content = final_card.convert('RGBA')

            # Create a mask for the rounded corners
            mask = Image.new('L', (card_width, final_card_height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                [(0, 0), (card_width-1, final_card_height-1)],
                radius=radius,
                fill=255
            )

            # Apply mask to card content
            card_with_content.putalpha(mask)

            # Create the final image with exact dimensions
            final_output = Image.new('RGB', (card_width, final_card_height), (255, 255, 255))

            # Paste shadow first (it will be underneath)
            final_output.paste(shadow_img, (shadow_offset_x, shadow_offset_y), shadow_img)

            # Then paste the card content on top
            final_output.paste(card_with_content, (0, 0), card_with_content)

        except (AttributeError, ImportError):
            # Fallback for older Pillow versions without rounded_rectangle
            final_output = final_card

        # Save the final image with exact 1480px width
        final_output.save(output_path, format="PNG")
        print(f"News card image generated and saved to {output_path}, width={card_width}px")

    except Exception as e:
        print(f"Error generating card image: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
