import re
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

def generate_tags_with_frequency(article, max_tags=3):
    """
    Generate frequency-based tags from an article's content.

    Args:
        article (dict): A dictionary containing article information with possible keys:
            - title: The article's title
            - description: A brief description of the article
            - content: The main content of the article
            - source: A dictionary containing source information with a 'name' key
        max_tags (int, optional): Maximum number of tags to generate. Defaults to 3.

    Returns:
        list: A list of tuples containing (tag, frequency) pairs, sorted by frequency
            in descending order, limited to max_tags items.
    """
    # Combine relevant article text
    text = ' '.join(filter(None, [
        article.get('title', ''),
        article.get('description', ''),
        article.get('content', ''),
        article.get('source', {}).get('name', '')
    ]))

    # Tokenize and clean
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    # Remove stopwords
    filtered_words = [word for word in words if word not in ENGLISH_STOP_WORDS]

    # Count word frequencies
    word_counts = Counter(filtered_words)

    # Get top N most common
    most_common = word_counts.most_common(max_tags)

    # Print each tag and its frequency
    print("🔖 Top Tags with Frequency:")
    for tag, freq in most_common:
        print(f"{tag}: {freq}")

    return most_common
