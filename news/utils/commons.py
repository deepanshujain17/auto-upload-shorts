import re
from datetime import datetime, timedelta, timezone

def get_zulu_time_minus(minutes: int = 15) -> str:
    """
    Returns the UTC (Zulu) time string for 'minutes' ago from now.

    Args:
        minutes (int): Number of minutes to subtract from current UTC time. Default is 15.

    Returns:
        str: Time in ISO 8601 Zulu format (e.g., '2025-05-12T11:45:00Z')
    """
    # Get the current UTC time
    current_utc_time = datetime.now(timezone.utc)

    # Subtract the given number of minutes
    time_minus_delta = current_utc_time - timedelta(minutes=minutes)

    # Format the result as an ISO 8601 Zulu time string
    return time_minus_delta.strftime('%Y-%m-%dT%H:%M:%SZ')

# TODO: Add support for all lowercase word extraction too eg. dohadiamondleague2025
def normalize_hashtag(text: str) -> str:
    """
    Normalize the given text by removing leading '#' and extracting words with Pascal case.
    Filters out single-letter words.
    e.g. "#NeerajChopra -> Neeraj Chopra"

    Args:
        text (str): The text to normalize.

    Returns:
        str: Normalized text with words of length > 1.
    """
    text = text.lstrip("#")
    pattern = re.compile(
        r'''
            [A-Z]{3,}(?=[A-Z][a-z])  # acronyms (≥3 letters) before a Pascal-Case word
            | [A-Z][a-z]+            # Pascal-Case words
            | [A-Z]{3,}              # standalone acronyms (≥3 letters)
            | [A-Z]{2,}              # standalone acronyms (≥2 letters)
            ''',
        re.VERBOSE
    )
    words = pattern.findall(text)
    return " ".join(words) or text
