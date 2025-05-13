import re
from collections import Counter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

def generate_tags_with_frequency(article, max_tags=3):
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
