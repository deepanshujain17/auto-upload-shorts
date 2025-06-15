import re
from typing import Dict
from settings import AudioSettings

# TODO: content of the article is incomplete, update API or use article.url to scrape full / longer content
class TextProcessor:
    """Handles text processing and SSML formatting for audio generation."""

    @staticmethod
    def clean_content(text: str) -> str:
        """Remove trailing pattern like '... [1234 chars]' from text."""
        return re.sub(r'\.\.\.\s*\[\d+\s+chars\]$', '', text.strip())

    @staticmethod
    def escape_ssml_characters(text: str) -> str:
        """
        Escapes special characters for safe use in SSML.
        """
        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            "\"": "&quot;",
            "'": "&apos;"
        }
        for char, escape in replacements.items():
            text = text.replace(char, escape)
        return text

    @staticmethod
    def add_breaks_to_punctuation(text: str, break_time: int = 1000) -> str:
        """Add SSML breaks after punctuation marks."""

        # Match any group of punctuation characters (.,!?;:) one or more times
        def replacer(match):
            first_char = match.group(0)[0]  # Keep the first punctuation
            return f"{first_char} <break time=\"{break_time}ms\"/>"

        text = TextProcessor.escape_ssml_characters(text)
        # Replace using regex
        text_with_break = re.sub(r'[.!?:]+', replacer, text)

        # Add long break after complete text
        text_with_break = f"{text_with_break} <break time=\"4000ms\"/>"
        return text_with_break

    @classmethod
    def prepare_article_text(cls, article: Dict[str, str]) -> str:
        """Prepare article text with SSML formatting."""

        # Extract and validate article components
        title = article.get('title', '').strip()
        description = article.get('description', '').strip()
        content = article.get('content', '').strip()

        if not any([title, description, content]):
            raise ValueError("Article must contain at least one of: title, description, or content")

        # Combine text parts
        text_parts = []
        if title:
            text_parts.append(title) # Can use <emphasize> on title in ssml
        if description:
            text_parts.append(description)
        if content:
            text_parts.append(cls.clean_content(content))

        final_text = ". ".join(text_parts)
        final_text = cls.add_breaks_to_punctuation(final_text)
        print(f"Generated text for audio: {final_text}")

        ssml_text = f"""
        <speak>
            <prosody rate="{AudioSettings.PROSODY_RATE}" volume="{AudioSettings.PROSODY_VOLUME}">
                {final_text}
            </prosody>
        </speak>
        """

        return ssml_text
