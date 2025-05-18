import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Constants
CLIENT_SECRETS_FILE = "client_secrets.json"
# Scopes for YouTube API. Make sure to adjust the scopes based on your needs.
#TODO: Test & update it for playlist insert if necessary
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_PICKLE = "token.pkl"

def authenticate_youtube():
    """
    Authenticate with YouTube API using OAuth 2.0

    Returns:
        googleapiclient.discovery.Resource: Authenticated YouTube API client
    """
    creds = None

    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PICKLE, "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)
