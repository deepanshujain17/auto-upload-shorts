import os
from datetime import datetime
from pathlib import Path


class HashtagStorage:
    """Manages storage and retrieval of processed hashtags"""

    @staticmethod
    def _get_hashtag_file_path():
        """Returns the path to trending hashtags file"""
        output_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "output/history"
        output_dir.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist
        file_path = output_dir / "trending_hashtags.txt"
        if not file_path.exists():
            file_path.touch()  # Create the file if it doesn't exist
        return file_path

    @classmethod
    def read_history(cls):
        """Read the hashtag history file and return a set of (hashtag, date) tuples"""
        file_path = cls._get_hashtag_file_path()
        history = set()
        if file_path.exists():
            with open(file_path, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        history.add((parts[0], parts[1]))
        return history

    @classmethod
    def save_hashtag(cls, hashtag):
        """Save a hashtag with current date to the history file"""
        file_path = cls._get_hashtag_file_path()
        current_date = datetime.now().strftime('%Y-%m-%d')
        with open(file_path, 'a') as f:
            f.write(f"{hashtag},{current_date}\n")

    @classmethod
    def is_hashtag_processed_today(cls, hashtag):
        """Check if a hashtag was already processed today"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        history = cls.read_history()
        return (hashtag, current_date) in history
