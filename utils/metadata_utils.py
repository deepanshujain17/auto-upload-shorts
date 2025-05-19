from typing import List, Optional, Tuple

from news.utils.tag_utils import generate_tags_with_frequency
from settings import YouTubeSettings


def generate_video_tags(
    article: dict,
    category: str,
    hashtag: Optional[str] = None
) -> Tuple[List[str], List[str]]:
    """
    Generate tags for the YouTube video. Returns tags without '#' prefix.

    Args:
        article: The news article data
        category: News category
        hashtag: Optional hashtag to include

    Returns:
        Tuple containing:
            - List of article-specific tags
            - Combined list of tags
    """
    # Handle category tags based on whether this is a trending query or category
    if hashtag:
        # Default hashtags plus breakdown of hashtag keyword
        category_tags = YouTubeSettings.DEFAULT_HASHTAGS + category.split()
    else:
        category_tags = YouTubeSettings.CATEGORY_HASHTAG_MAP.get(category.lower(), [])

    # Generate dynamic tags from article content
    article_tags = [
        tag for tag, _ in generate_tags_with_frequency(
            article,
            max_tags=YouTubeSettings.ARTICLE_MAX_TAGS
        )
    ]

    # Combine tags ensuring uniqueness and proper limits
    hashtag_tags = [hashtag.lstrip("#")] if hashtag else []

    # Remove duplicates while preserving order
    combined_tags = list(dict.fromkeys(
        hashtag_tags +
        article_tags +
        category_tags
    ))

    return article_tags, combined_tags


def generate_video_title(
    article: dict,
    article_tags: List[str],
    hashtag: Optional[str] = None
) -> str:
    """
    Generate title for the YouTube video.

    Args:
        article: The news article data
        article_tags: List of article tags
        hashtag: Optional hashtag to include

    Returns:
        Formatted video title
    """
    article_title = article.get("title", "No Title")
    # If hashtag, use that else (category case) use first article tag
    title_hashtag_str = f"{hashtag}" if hashtag else f"#{article_tags[0]}"

    # Create base title with prefix
    base_title = "Breaking News: "
    # Calculate remaining characters for article title considering hashtag
    max_article_length = 100 - len(base_title) - len(title_hashtag_str) - 1  # -1 for space before hashtag
    truncated_article_title = ' '.join(article_title.split())
    if len(truncated_article_title) > max_article_length:
        truncated_article_title = truncated_article_title[:max_article_length].rsplit(' ', 1)[0]

    return f"{base_title}{truncated_article_title} {title_hashtag_str}"


def generate_video_description(
    article: dict,
    combined_tags: List[str]
) -> str:
    """
    Generate description for the YouTube video.

    Args:
        article: The news article data
        combined_tags: List of combined tags

    Returns:
        Formatted video description
    """
    article_description = article.get("description", "No Description")
    combined_tags_str = " ".join([f"#{tag}" for tag in combined_tags])
    extra_tags_str = " ".join([f"#{tag}" for tag in YouTubeSettings.EXTRA_DESCRIPTION_HASHTAGS])

    return f"{article_description} {combined_tags_str} {extra_tags_str}"
