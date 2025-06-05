import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_env_var(key: str, default=None):
    """Get environment variable with optional default value"""
    return os.getenv(key, default)
