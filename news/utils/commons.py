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
