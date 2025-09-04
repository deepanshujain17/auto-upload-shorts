import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Constants
CLIENT_SECRETS_FILE = "client_secrets.json"
# Scopes for YouTube API. Make sure to adjust the scopes based on your needs.
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_PICKLE = "token.pkl"
# Additional token file for Hindi channel
TOKEN_PICKLE_HI = "token_hi.pkl"


def _detect_lang() -> str:
    """Best-effort language detection without changing callers.
    Prefers settings.news.news_settings.lang if present, then .language.
    Defaults to 'en'.
    """
    try:
        from settings.news import news_settings  # lazy import to avoid cycles
        lang = getattr(news_settings, "language", None)
        if isinstance(lang, str) and lang:
            return lang.lower()
    except Exception:
        pass
    return "en"


def authenticate_youtube():
    """
    Authenticate with YouTube API using OAuth 2.0

    Returns:
        googleapiclient.discovery.Resource: Authenticated YouTube API client
    """
    creds = None

    # Pick token file based on language (support a separate channel for Hindi)
    lang = _detect_lang()
    token_file = TOKEN_PICKLE_HI if lang == "hi" else TOKEN_PICKLE

    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    youtube = build("youtube", "v3", credentials=creds)
    # Increase HTTP timeout for slower/resumable uploads
    youtube._http.timeout = 300  # 5 minutes
    return youtube
